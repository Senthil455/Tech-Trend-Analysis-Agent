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
        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        user_agent = os.getenv("REDDIT_USER_AGENT", "TechTrendAnalyzer/0.1")
        results = []
        mode = "demo"
        fallback_reason = None
        if not self.use_demo_data and os.getenv("TREND_LIVE_DATA") == "1":
            if not client_id or not client_secret:
                fallback_reason = "Reddit OAuth credentials are not configured"
            else:
                try:
                    token_response = requests.post(
                        "https://www.reddit.com/api/v1/access_token",
                        data={"grant_type": "client_credentials"},
                        auth=(client_id, client_secret),
                        headers={"User-Agent": user_agent},
                        timeout=10,
                    )
                    token_response.raise_for_status()
                    access_token = token_response.json().get("access_token")
                    if not access_token:
                        fallback_reason = "Reddit OAuth returned no access token"
                    else:
                        response = requests.get(
                            "https://oauth.reddit.com/search",
                            params={"q": query, "limit": limit},
                            headers={
                                "Authorization": f"Bearer {access_token}",
                                "User-Agent": user_agent,
                            },
                            timeout=10,
                        )
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