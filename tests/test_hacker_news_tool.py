import os
import unittest
from unittest.mock import Mock, patch

from tools.hacker_news_tool import HackerNewsTool


class HackerNewsToolTests(unittest.TestCase):
    @patch("tools.hacker_news_tool.requests.get")
    def test_live_search_uses_public_algolia_api(self, get):
        response = Mock()
        response.json.return_value = {
            "hits": [{
                "title": "A technology story",
                "points": 42,
                "num_comments": 8,
                "objectID": "123",
            }]
        }
        get.return_value = response

        with patch.dict(os.environ, {"TREND_LIVE_DATA": "1"}, clear=True):
            observation = HackerNewsTool(use_demo_data=False).execute("technology", limit=1)

        self.assertEqual(observation["mode"], "live")
        self.assertEqual(observation["results"][0]["score"], 42)
        self.assertEqual(
            observation["results"][0]["url"],
            "https://news.ycombinator.com/item?id=123",
        )
        get.assert_called_once_with(
            "https://hn.algolia.com/api/v1/search",
            params={"query": "technology", "hitsPerPage": 1},
            timeout=10,
        )

    def test_search_uses_demo_when_live_data_is_disabled(self):
        with patch.dict(os.environ, {}, clear=True):
            observation = HackerNewsTool(use_demo_data=False).execute("technology", limit=1)

        self.assertEqual(observation["mode"], "demo")
        self.assertEqual(observation["fallback_reason"], "TREND_LIVE_DATA is not enabled")


if __name__ == "__main__":
    unittest.main()