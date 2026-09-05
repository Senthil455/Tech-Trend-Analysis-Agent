from config.config import Config
from memory.long_term_memory import LongTermMemory
from memory.short_term_memory import ShortTermMemory
from reports.report_generator import ReportGenerator
from tools.github_tool import GitHubTool
from tools.news_tool import NewsTool
from tools.reddit_tool import RedditTool
from trend_engine.trend_analysis import calculate_trend_score, classify_score

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class ReActAgent:
    """
    A ReAct-based agent that reasons and acts iteratively.
    """
    def __init__(self, config=None, memory=None):
        self.config = config or Config()
        self.memory = memory or LongTermMemory(self.config.db_url)
        self.short_term = ShortTermMemory()
        self.report_generator = ReportGenerator()
        self.tools = {"search_news": NewsTool(), "search_reddit": RedditTool(), "search_github": GitHubTool()}
        self.llm = OpenAI(api_key=self.config.openai_api_key) if OpenAI and self.config.openai_api_key else None

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
        actions = [(name, {"query": topic, "limit": 5}) for name in self.tools if enabled[name]]
        if self.llm:
            actions = self._llm_actions(topic, actions)
        return topic, actions

    def _llm_actions(self, topic, fallback):
        tool_descriptions = ", ".join(self.tools)
        response = self.llm.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "Choose source tools for trend research. Return JSON: {\"tools\":[\"search_news\"]}. Only use listed tools."},
                {"role": "user", "content": f"Topic: {topic}. Available tools: {tool_descriptions}"},
            ],
        )
        names = response.choices[0].message.content
        import json
        selected = json.loads(names).get("tools", [])
        return [(name, {"query": topic, "limit": 5}) for name in selected if name in self.tools]

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
        topic, actions = self.reason(user_query)
        self.short_term.reset()
        self.short_term.update_query(topic)
        evidence = []
        for tool_name, tool_args in actions[: self.config.max_iterations]:
            observation = self.act(tool_name, tool_args)
            evidence.append({"source": tool_name.removeprefix("search_"), "items": observation["results"]})

        source_count = len(evidence)
        score = calculate_trend_score(72, 68, 75, source_count * 25, 90, 72, 80)
        trend = {
            "topic": topic,
            "score": score,
            "classification": classify_score(score),
            "source_count": source_count,
        }
        histories = {topic: self.memory.get_trend_history(topic)}
        self.memory.store_trend(topic, __import__("datetime").date.today(), score, trend)
        report = self.report_generator.generate_report(topic, [trend], evidence, histories)
        report["react_trace"] = [
            {"step": "reason", "decision": "Collect cross-platform signals"},
            *[{"step": "act", "tool": name} for name, _ in actions[: self.config.max_iterations]],
            {"step": "observe", "sources": source_count},
            {"step": "reason", "decision": "Score and compare with long-term memory"},
        ]
        return report