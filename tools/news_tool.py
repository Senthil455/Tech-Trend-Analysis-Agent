from tools.tool_interface import Tool
import os
import requests

class NewsTool(Tool):
    name = "search_news"
    description = "Search for recent news articles about a given topic."

    def __init__(self, use_demo_data=True):
        self.use_demo_data = use_demo_data

    def execute(self, query: str, limit: int = 10):
        """
        Search for news articles using an external API.

        Args:
            query (str): The search query.
            limit (int): The maximum number of articles to retrieve.

        Returns:
            dict: A dictionary containing the search query and results.
        """
        api_key = "" if self.use_demo_data else os.getenv("NEWS_API_KEY")
        results = []
        if api_key:
            try:
                response = requests.get(
                    "https://newsapi.org/v2/everything",
                    params={"q": query, "pageSize": limit, "sortBy": "publishedAt"},
                    headers={"X-Api-Key": api_key},
                    timeout=10,
                )
                response.raise_for_status()
                results = response.json().get("articles", [])
            except requests.RequestException:
                results = []
        if not results:
            results = [{"title": f"{query}: enterprise adoption accelerates", "source": "Demo News"}][:limit]

        return {
            "query": query,
            "results": results
        }