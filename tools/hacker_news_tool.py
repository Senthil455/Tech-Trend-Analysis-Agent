import os

import requests

from tools.tool_interface import Tool


class HackerNewsTool(Tool):
    name = "search_hacker_news"
    description = "Search Hacker News for recent technology discussions."

    def __init__(self, use_demo_data=True):
        self.use_demo_data = use_demo_data

    def execute(self, query: str, limit: int = 10):
        results = []
        mode = "demo"
        fallback_reason = None
        if self.use_demo_data:
            fallback_reason = "demo mode is enabled"
        elif os.getenv("TREND_LIVE_DATA") != "1":
            fallback_reason = "TREND_LIVE_DATA is not enabled"
        else:
            try:
                response = requests.get(
                    "https://hn.algolia.com/api/v1/search",
                    params={"query": query, "hitsPerPage": limit},
                    timeout=10,
                )
                response.raise_for_status()
                hits = response.json().get("hits", [])
                for hit in hits[:limit]:
                    item = dict(hit)
                    item["score"] = item.get("points", 0)
                    if not item.get("url") and item.get("objectID"):
                        item["url"] = f"https://news.ycombinator.com/item?id={item['objectID']}"
                    results.append(item)
                mode = "live" if results else "demo"
                if not results:
                    fallback_reason = "Hacker News returned no results"
            except (requests.RequestException, ValueError):
                fallback_reason = "Hacker News request failed"

        if not results:
            results = [{"title": f"Developers discuss {query}", "source": "Demo Hacker News"}][:limit]
        return {
            "query": query,
            "results": results,
            "mode": mode,
            "fallback_reason": fallback_reason,
        }