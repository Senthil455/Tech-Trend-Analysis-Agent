from tools.news_tool import NewsTool

class ReActAgent:
    """
    A ReAct-based agent that reasons and acts iteratively.
    """
    def __init__(self):
        self.tools = {
            "search_news": NewsTool()
        }
        self.state = {
            "query": None,
            "observations": []
        }

    def reason(self, user_query):
        """
        Reason about the user's query and decide on an action.
        """
        self.state["query"] = user_query
        return "search_news", {"query": user_query, "limit": 5}

    def act(self, tool_name, tool_args):
        """
        Execute the selected tool and observe the results.
        """
        tool = self.tools.get(tool_name)
        if tool:
            observation = tool.execute(**tool_args)
            self.state["observations"].append(observation)
            return observation
        else:
            raise ValueError(f"Tool {tool_name} not found.")

    def run(self, user_query):
        """
        Run the ReAct loop for a given user query.
        """
        tool_name, tool_args = self.reason(user_query)
        observation = self.act(tool_name, tool_args)
        return observation