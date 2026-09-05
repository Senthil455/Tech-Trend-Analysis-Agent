from fastapi import FastAPI
from api.react_agent import ReActAgent

app = FastAPI()

# Initialize the ReAct agent
agent = ReActAgent()

@app.post("/analyze")
def analyze_trends(query: str):
    """
    Endpoint to analyze technology trends based on a user query.

    Args:
        query (str): The user's query about technology trends.

    Returns:
        dict: The agent's observations.
    """
    result = agent.run(query)
    return {"query": query, "observations": result}