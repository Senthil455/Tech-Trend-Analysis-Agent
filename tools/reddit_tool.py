from tools.tool_interface import Tool
import os
import requests

class RedditTool(Tool):
    name = "search_reddit"
    description = "Search Reddit for recent discussions about a given topic."

    def __init__(self, use_demo_data=True):
        self.use_demo_data = use_demo_data

    def execute(self, query: str, limit: int = 10):
        """
        Search Reddit for discussions using an external API.

        Args:
            query (str): The search query.
            limit (int): The maximum number of posts to retrieve.

        Returns:
            dict: A dictionary containing the search query and results.
        """
        # Example placeholder for API call (replace with actual Reddit API logic)
        api_url = "https://www.reddit.com/search.json"
        headers = {"User-Agent": "TechTrendAnalyzer/0.1"}
        results = []
        mode = "demo"
        fallback_reason = None
        if not self.use_demo_data and os.getenv("TREND_LIVE_DATA") == "1":
            try:
                response = requests.get(api_url, params={"q": query, "limit": limit}, headers=headers, timeout=10)
                response.raise_for_status()
                children = response.json().get("data", {}).get("children", [])
                results = [child.get("data", child) for child in children]
                mode = "live" if results else "demo"
                if not results:
                    fallback_reason = "Reddit returned no results"
            except (requests.RequestException, ValueError):
                fallback_reason = "Reddit request failed"
        elif self.use_demo_data:
            fallback_reason = "demo mode is enabled"
        else:
            fallback_reason = "TREND_LIVE_DATA is not enabled"
        if not results:
            results = [{"title": f"Practitioners debate {query}", "source": "Demo Reddit"}][:limit]

        return {
            "query": query,
            "results": results,
            "mode": mode,
            "fallback_reason": fallback_reason,
        }