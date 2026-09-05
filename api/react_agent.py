import os
import json
from datetime import date

from config.config import Config
from memory.long_term_memory import LongTermMemory
from memory.short_term_memory import ShortTermMemory
from reports.report_generator import ReportGenerator
from reports.schemas import TrendIntelligence
from tools.github_tool import GitHubTool
from tools.news_tool import NewsTool
from tools.reddit_tool import RedditTool
from trend_engine.trend_analysis import calculate_observed_factors, calculate_trend_score, classify_score

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class ReActAgent:
    """
    A ReAct-based agent that reasons and acts iteratively.
    """
    def __init__(self, config=None, memory=None, tools=None):
        self.config = config or Config()
        self.memory = memory or LongTermMemory(self.config.db_url)
        self.short_term = ShortTermMemory()
        self.report_generator = ReportGenerator()
        self.tools = tools or {
            "search_news": NewsTool(self.config.use_demo_data),
            "search_reddit": RedditTool(self.config.use_demo_data),
            "search_github": GitHubTool(self.config.use_demo_data),
        }
        self.llm = (
            OpenAI(api_key=self.config.openai_api_key, timeout=10, max_retries=0)
            if OpenAI and self.config.openai_api_key and not self.config.use_demo_data
            else None
        )

    def reason(self, user_query):
        """
        Reason about the user's query and decide on an action.
        """
        topic = user_query.strip() or "AI technology"
        enabled = {
            "search_news": self.config.news_enabled,
            "search_reddit": self.config.reddit_enabled,
            "search_github": self.config.github_enabled,
        }
        actions = [(name, {"query": topic, "limit": 5}) for name in self.tools if enabled.get(name, True)]
        if self.llm:
            actions = self._llm_actions(topic, actions)
        return topic, actions

    def _llm_actions(self, topic, fallback):
        tool_descriptions = ", ".join(self.tools)
        try:
            response = self.llm.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "Choose source tools for trend research. Return JSON: {\"tools\":[\"search_news\"]}. Only use listed tools."},
                    {"role": "user", "content": f"Topic: {topic}. Available tools: {tool_descriptions}"},
                ],
            )
            import json
            selected = json.loads(response.choices[0].message.content).get("tools", [])
            actions = [(name, {"query": topic, "limit": 5}) for name in selected if name in self.tools]
            return actions or fallback
        except Exception:
            return fallback

    def act(self, tool_name, tool_args):
        """
        Execute the selected tool and observe the results.
        """
        tool = self.tools.get(tool_name)
        if not tool:
            raise ValueError(f"Tool {tool_name} not found.")
        observation = tool.execute(**tool_args)
        self.short_term.add_tool_usage(tool_name, observation)
        return observation

    def run(self, user_query):
        """
        Run the ReAct loop for a given user query.
        """
        self.short_term.reset()
        topic, actions = self.reason(user_query)
        self.short_term.update_query(topic)
        evidence = []
        tool_trace = []
        for tool_name, tool_args in actions[: self.config.max_iterations]:
            try:
                observation = self.act(tool_name, tool_args)
                raw_items = observation.get("results", [])
                items = raw_items if isinstance(raw_items, list) else [raw_items]
                highlights = []
                for item in items[:3]:
                    if isinstance(item, dict):
                        highlight = item.get("title") or item.get("name") or item.get("description")
                        if highlight:
                            highlights.append(str(highlight))
                evidence.append({
                    "source": tool_name.removeprefix("search_"),
                    "items": items,
                    "highlights": highlights,
                    "mode": observation.get("mode", "live"),
                    "fallback_reason": observation.get("fallback_reason"),
                })
                tool_trace.append({"step": "act", "tool": tool_name, "items": len(items)})
            except Exception as error:
                evidence.append({
                    "source": tool_name.removeprefix("search_"),
                    "items": [],
                    "mode": "error",
                    "error": str(error),
                })
                tool_trace.append({"step": "act", "tool": tool_name, "error": "tool failed"})

        previous_history = self.memory.get_trend_history(topic)
        previous_score = previous_history[-1]["score"] if previous_history else None
        factors = calculate_observed_factors(evidence, previous_score, self.config.minimum_sources, topic)
        score = calculate_trend_score(**factors)
        source_count = sum(1 for item in evidence if item["items"] and item.get("mode") == "live")
        trend = {
            "topic": topic,
            "score": score,
            "classification": classify_score(score, self.config.emerging_threshold, self.config.minimum_score),
            "source_count": source_count,
            "evidence_sufficient": source_count >= self.config.minimum_sources,
            "factors": factors,
        }
        histories = {topic: previous_history}
        self.memory.store_trend(topic, date.today(), score, trend)
        report = self.report_generator.generate_report(
            topic,
            [trend],
            evidence,
            histories,
            minimum_sources=self.config.minimum_sources,
            lookback_days=self.config.lookback_days,
            tools_used=[name for name, _ in actions[: self.config.max_iterations]],
            iterations=len(actions[: self.config.max_iterations]),
            generation_mode="deterministic",
        )
        if self.llm:
            report = self._llm_interpret(report)
        report["analysis_metadata"]["source_status"] = {
            item["source"]: item.get("mode", "error") for item in evidence
        }
        report["analysis_metadata"]["generation_mode"] = report["analysis_metadata"].get(
            "generation_mode", "deterministic"
        )
        return report

    def _llm_interpret(self, deterministic_report):
        """Let the LLM interpret verified facts, never replace their metrics."""
        try:
            response = self.llm.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.2,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": "Return only valid JSON matching the supplied trend intelligence schema. Interpret facts, but never invent metrics, sources, URLs, dates, entities, or historical values. Use null or empty arrays when unavailable.",
                    },
                    {
                        "role": "user",
                        "content": json.dumps({
                            "schema": TrendIntelligence.model_json_schema(),
                            "verified_analysis": deterministic_report,
                        }),
                    },
                ],
            )
            candidate = TrendIntelligence.model_validate(json.loads(response.choices[0].message.content))
            base = TrendIntelligence.model_validate(deterministic_report).model_dump(mode="json")
            interpreted = candidate.model_dump(mode="json")
            for field in (
                "trend_overview", "why_trending", "key_drivers", "growth_analysis",
                "key_entities", "related_topics", "emerging_subtopics", "audience_analysis",
                "sentiment_analysis", "risks_and_uncertainties", "future_outlook",
                "prediction", "content_opportunities", "recommended_content_angles",
                "downstream_agent_context",
            ):
                base[field] = interpreted[field]
            base["analysis_metadata"]["generation_mode"] = "llm_interpreted"
            return base
        except Exception:
            return deterministic_report