from fastapi import FastAPI, Query
from api.react_agent import ReActAgent

app = FastAPI(title="Tech Trend Analysis Agent", version="1.0.0")

# Initialize the ReAct agent
agent = ReActAgent()

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze")
def analyze_trends(query: str = Query(..., min_length=1)):
    """
    Endpoint to analyze technology trends based on a user query.

    Args:
        query (str): The user's query about technology trends.

    Returns:
        dict: The agent's observations.
    """
    result = agent.run(query)
    return result