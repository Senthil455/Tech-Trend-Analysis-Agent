import json
import tempfile
import unittest
from pathlib import Path

from api.react_agent import ReActAgent
from api.main import analyze_trends
from config.config import Config
from memory.long_term_memory import LongTermMemory
from reports.schemas import TrendIntelligence
from reports.report_generator import ReportGenerator
from trend_engine.trend_analysis import calculate_observed_factors, calculate_trend_score, classify_score


class FailingTool:
    def execute(self, **kwargs):
        raise RuntimeError("temporary source failure")


class AgentTests(unittest.TestCase):
    def test_agent_returns_structured_cross_platform_report(self):
        with tempfile.TemporaryDirectory() as directory:
            memory_path = Path(directory) / "memory.json"
            agent = ReActAgent(
                config=Config(openai_api_key="", use_demo_data=True),
                memory=LongTermMemory(f"sqlite:///{memory_path}"),
            )
            report = agent.run("AI agents")

        self.assertEqual(report["request"]["query"], "AI agents")
        self.assertEqual(report["trend_overview"]["trend_score"], report["trend_metrics"]["overall_score"])
        self.assertFalse(report["cross_platform_analysis"]["platforms"])
        self.assertTrue(all(item["mode"] == "demo" for item in report["evidence"]))
        downstream = report["downstream_agent_context"]
        json.dumps(downstream)
        self.assertIn("key_facts", downstream)
        self.assertIn("must_not_claim", downstream)
        self.assertTrue(report["request"]["analysis_timestamp"])
        validated = TrendIntelligence.model_validate(report)
        json.dumps(validated.model_dump(mode="json"))
        self.assertIn("news", validated.platform_analysis.model_dump())

    def test_score_validates_factors_and_classifies(self):
        self.assertEqual(calculate_trend_score(100, 100, 100, 100, 100, 100, 100), 100)
        self.assertEqual(classify_score(91), "Explosive")

    def test_observed_factors_use_evidence(self):
        factors = calculate_observed_factors([
            {"source": "news", "items": [{"title": "a"}, {"title": "b"}]},
            {"source": "github", "items": [{"name": "repo", "stargazers_count": 10}]},
        ])
        self.assertEqual(factors["volume"], 44.0)
        self.assertEqual(factors["cross_platform"], 66.67)
        self.assertEqual(factors["authority"], 75)

    def test_tool_failure_is_reported_without_aborting(self):
        with tempfile.TemporaryDirectory() as directory:
            agent = ReActAgent(
                config=Config(openai_api_key="", use_demo_data=True),
                memory=LongTermMemory(str(Path(directory) / "memory.json")),
                tools={"search_broken": FailingTool()},
            )
            report = agent.run("robotics")
        self.assertEqual(report["analysis_metadata"]["source_status"]["broken"], "error")
        self.assertTrue(report["risks_and_uncertainties"])

    def test_whitespace_query_is_rejected(self):
        with self.assertRaises(Exception) as context:
            analyze_trends("   ")
        self.assertEqual(context.exception.status_code, 422)

    def test_source_links_are_preserved_without_fabrication(self):
        generator = ReportGenerator()
        evidence = [
            {
                "source": "reddit",
                "mode": "live",
                "items": [{"title": "Discussion", "permalink": "/r/technology/comments/abc/discussion"}],
            },
            {"source": "github", "mode": "live", "items": [{"name": "repo", "html_url": "https://github.com/example/repo"}]},
            {"source": "news", "mode": "demo", "items": [{"title": "Demo result"}]},
        ]
        report = generator.generate_report(
            "technology", [{"topic": "technology", "score": 20, "classification": "Watch", "source_count": 2, "factors": {}}], evidence, {"technology": []}
        )
        urls = {item.source: item.url for item in TrendIntelligence.model_validate(report).evidence}
        self.assertEqual(urls["reddit"], "https://www.reddit.com/r/technology/comments/abc/discussion")
        self.assertEqual(urls["github"], "https://github.com/example/repo")
        self.assertIsNone(urls["news"])


if __name__ == "__main__":
    unittest.main()