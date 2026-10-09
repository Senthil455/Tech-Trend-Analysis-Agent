import os
import unittest
from unittest.mock import Mock, patch

from tools.reddit_tool import RedditTool


class RedditToolTests(unittest.TestCase):
    @patch("tools.reddit_tool.requests.get")
    @patch("tools.reddit_tool.requests.post")
    def test_live_search_uses_reddit_oauth(self, post, get):
        token_response = Mock()
        token_response.json.return_value = {"access_token": "test-token"}
        post.return_value = token_response

        search_response = Mock()
        search_response.json.return_value = {
            "data": {"children": [{"data": {"title": "A discussion"}}]}
        }
        get.return_value = search_response

        with patch.dict(os.environ, {
            "TREND_LIVE_DATA": "1",
            "REDDIT_CLIENT_ID": "client-id",
            "REDDIT_CLIENT_SECRET": "client-secret",
            "REDDIT_USER_AGENT": "test-agent/1.0",
        }, clear=True):
            observation = RedditTool(use_demo_data=False).execute("AI", limit=1)

        self.assertEqual(observation["mode"], "live")
        self.assertEqual(observation["results"], [{"title": "A discussion"}])
        post.assert_called_once_with(
            "https://www.reddit.com/api/v1/access_token",
            data={"grant_type": "client_credentials"},
            auth=("client-id", "client-secret"),
            headers={"User-Agent": "test-agent/1.0"},
            timeout=10,
        )
        get.assert_called_once_with(
            "https://oauth.reddit.com/search",
            params={"q": "AI", "limit": 1},
            headers={
                "Authorization": "Bearer test-token",
                "User-Agent": "test-agent/1.0",
            },
            timeout=10,
        )

    @patch("tools.reddit_tool.requests.get")
    @patch("tools.reddit_tool.requests.post")
    def test_live_search_without_oauth_credentials_uses_demo(self, post, get):
        with patch.dict(os.environ, {"TREND_LIVE_DATA": "1"}, clear=True):
            observation = RedditTool(use_demo_data=False).execute("AI", limit=1)

        self.assertEqual(observation["mode"], "demo")
        self.assertEqual(
            observation["fallback_reason"],
            "Reddit OAuth credentials are not configured",
        )
        post.assert_not_called()
        get.assert_not_called()


if __name__ == "__main__":
    unittest.main()