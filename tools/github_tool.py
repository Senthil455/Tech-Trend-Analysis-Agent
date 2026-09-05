from tools.tool_interface import Tool
import os
import requests


class GitHubTool(Tool):
    name = "search_github"
    description = "Search GitHub repositories and return developer interest signals."

    def __init__(self, use_demo_data=True):
        self.use_demo_data = use_demo_data

    def execute(self, query: str, limit: int = 10):
        try:
            if self.use_demo_data or os.getenv("TREND_LIVE_DATA") != "1":
                raise requests.RequestException("demo mode")
            response = requests.get(
                "https://api.github.com/search/repositories",
                params={"q": query, "sort": "stars", "order": "desc", "per_page": limit},
                headers={"Accept": "application/vnd.github+json"},
                timeout=10,
            )
            response.raise_for_status()
            results = response.json().get("items", [])
        except requests.RequestException:
            results = []
        if not results:
            results = [{"name": f"{query}-framework", "description": "Demo developer activity signal"}]
        return {"query": query, "results": results}