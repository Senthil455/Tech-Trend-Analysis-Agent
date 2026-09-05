from tools.tool_interface import Tool
import os
import requests


class GitHubTool(Tool):
    name = "search_github"
    description = "Search GitHub repositories and return developer interest signals."

    def __init__(self, use_demo_data=True):
        self.use_demo_data = use_demo_data

    def execute(self, query: str, limit: int = 10):
        mode = "demo"
        fallback_reason = None
        try:
            if self.use_demo_data or os.getenv("TREND_LIVE_DATA") != "1":
                fallback_reason = "live data is disabled"
                raise requests.RequestException("live data is disabled")
            response = requests.get(
                "https://api.github.com/search/repositories",
                params={"q": query, "sort": "stars", "order": "desc", "per_page": limit},
                headers={
                    "Accept": "application/vnd.github+json",
                    **({"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"} if os.getenv("GITHUB_TOKEN") else {}),
                },
                timeout=10,
            )
            response.raise_for_status()
            results = response.json().get("items", [])
            mode = "live" if results else "demo"
            if not results:
                fallback_reason = "GitHub returned no results"
        except (requests.RequestException, ValueError):
            results = []
            if fallback_reason is None:
                fallback_reason = "GitHub request failed"
        if not results:
            results = [{"name": f"{query}-framework", "description": "Demo developer activity signal"}]
        return {"query": query, "results": results, "mode": mode, "fallback_reason": fallback_reason}