import json
import os

class LongTermMemory:
    """
    Manages the long-term memory for storing historical trends and reports.
    """
    def __init__(self, db_url="sqlite:///trend_memory.db"):
        self.path = db_url.removeprefix("sqlite:///") if db_url.startswith("sqlite:///") else "trend_memory.json"
        self.records = self._load()

    def _load(self):
        if not os.path.exists(self.path):
            return []
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                return json.load(file)
        except (OSError, json.JSONDecodeError):
            return []

    def store_trend(self, topic, date, score, data):
        """Store a trend in the database."""
        self.records.append({"topic": topic, "date": str(date), "score": score, "data": data})
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(self.records, file, indent=2)

    def get_trend_history(self, topic):
        """Retrieve historical data for a specific topic."""
        return [record for record in self.records if record["topic"].lower() == topic.lower()]

    def close(self):
        """Close the database connection."""
        return None