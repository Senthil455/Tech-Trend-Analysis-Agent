import tempfile
import unittest
from pathlib import Path

from api.react_agent import ReActAgent
from memory.long_term_memory import LongTermMemory
from trend_engine.trend_analysis import calculate_trend_score, classify_score


class AgentTests(unittest.TestCase):
    def test_agent_returns_structured_cross_platform_report(self):
        with tempfile.TemporaryDirectory() as directory:
            memory_path = Path(directory) / "memory.json"
            agent = ReActAgent(memory=LongTermMemory(f"sqlite:///{memory_path}"))
            report = agent.run("AI agents")

        self.assertEqual(report["query"], "AI agents")
        self.assertEqual(report["top_trends"][0]["source_count"], 3)
        self.assertGreaterEqual(len(report["react_trace"]), 5)
        self.assertTrue(report["report_date"])

    def test_score_validates_factors_and_classifies(self):
        self.assertEqual(calculate_trend_score(100, 100, 100, 100, 100, 100, 100), 100)
        self.assertEqual(classify_score(91), "Explosive")


if __name__ == "__main__":
    unittest.main()