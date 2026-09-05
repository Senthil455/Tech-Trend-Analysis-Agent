from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api.react_agent import ReActAgent

app = FastAPI(title="Tech Trend Analysis Agent", version="1.0.0")
app.mount("/web", StaticFiles(directory=Path(__file__).parent.parent / "web"), name="web")

# Initialize the ReAct agent
agent = ReActAgent()


@app.get("/")
def root():
    return FileResponse(Path(__file__).parent.parent / "web" / "index.html")


@app.get("/api-info")
def api_info():
    return {
        "name": app.title,
        "version": app.version,
        "status": "ok",
        "endpoints": {"health": "/health", "analyze": "/analyze", "docs": "/docs"},
    }


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
    if not query.strip():
        raise HTTPException(status_code=422, detail="Query must contain non-whitespace characters.")
    result = agent.run(query)
    return result