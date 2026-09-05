from api.react_agent import ReActAgent
from trend_engine.trend_analysis import calculate_trend_score, classify_score


def test_agent_returns_structured_cross_platform_report(tmp_path):
    agent = ReActAgent(memory=__import__("memory.long_term_memory", fromlist=["LongTermMemory"]).LongTermMemory(
        f"sqlite:///{tmp_path / 'memory.json'}"
    ))
    report = agent.run("AI agents")

    assert report["query"] == "AI agents"
    assert report["top_trends"][0]["source_count"] == 3
    assert len(report["react_trace"]) >= 5
    assert report["report_date"]


def test_score_validates_factors_and_classifies():
    assert calculate_trend_score(100, 100, 100, 100, 100, 100, 100) == 100
    assert classify_score(91) == "Explosive"