import tempfile
import unittest
from pathlib import Path

from api.react_agent import ReActAgent
from api.main import analyze_trends
from config.config import Config
from memory.long_term_memory import LongTermMemory
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

        self.assertEqual(report["query"], "AI agents")
        self.assertEqual(report["top_trends"][0]["source_count"], 0)
        self.assertTrue(all(item["mode"] == "demo" for item in report["evidence"]))
        self.assertGreaterEqual(len(report["react_trace"]), 5)
        self.assertTrue(report["report_date"])

    def test_score_validates_factors_and_classifies(self):
        self.assertEqual(calculate_trend_score(100, 100, 100, 100, 100, 100, 100), 100)
        self.assertEqual(classify_score(91), "Explosive")

    def test_observed_factors_use_evidence(self):
        factors = calculate_observed_factors([
            {"source": "news", "items": [{"title": "a"}, {"title": "b"}]},
            {"source": "github", "items": [{"name": "repo", "stargazers_count": 10}]},
        ])
        self.assertEqual(factors["volume"], 30)
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
        self.assertEqual(report["evidence"][0]["items"], [])
        self.assertEqual(report["evidence"][0]["error"], "temporary source failure")

    def test_whitespace_query_is_rejected(self):
        with self.assertRaises(Exception) as context:
            analyze_trends("   ")
        self.assertEqual(context.exception.status_code, 422)


if __name__ == "__main__":
    unittest.main()