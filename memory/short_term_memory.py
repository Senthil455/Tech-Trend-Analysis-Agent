class ShortTermMemory:
    """
    Manages the short-term memory for the agent during a single session.
    """
    def __init__(self):
        self.reset()

    def update_query(self, query):
        """Update the current query in memory."""
        self.state["query"] = query

    def add_tool_usage(self, tool_name, result):
        """Log the usage of a tool and its result."""
        self.state["tools_used"].append(tool_name)
        self.state["observations"].append(result)

    def add_evidence(self, evidence):
        self.state.setdefault("evidence", []).extend(evidence)

    def get_state(self):
        """Retrieve the current state of short-term memory."""
        return self.state

    def reset(self):
        """Reset the short-term memory for a new session."""
        self.state = {
            "query": None,
            "tools_used": [],
            "observations": []
        }