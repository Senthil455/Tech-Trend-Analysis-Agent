import json
import os
import threading

class LongTermMemory:
    """
    Manages the long-term memory for storing historical trends and reports.
    """
    def __init__(self, db_url="trend_memory.json"):
        if db_url.startswith("sqlite:///"):
            self.path = db_url.removeprefix("sqlite:///")
        elif db_url.startswith("sqlite://"):
            self.path = db_url.removeprefix("sqlite://")
        else:
            self.path = db_url
        self._lock = threading.RLock()
        self.records = self._load()

    def _load(self):
        if not os.path.exists(self.path):
            return []
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                records = json.load(file)
                return records if isinstance(records, list) else []
        except (OSError, json.JSONDecodeError):
            return []

    def store_trend(self, topic, date, score, data):
        """Store a trend in the database."""
        record = {"topic": str(topic), "date": str(date), "score": float(score), "data": data}
        with self._lock:
            self.records.append(record)
            directory = os.path.dirname(os.path.abspath(self.path))
            os.makedirs(directory, exist_ok=True)
            temporary_path = f"{self.path}.tmp"
            with open(temporary_path, "w", encoding="utf-8") as file:
                json.dump(self.records, file, indent=2)
            os.replace(temporary_path, self.path)
        return record

    def get_trend_history(self, topic):
        """Retrieve historical data for a specific topic."""
        with self._lock:
            return [
                record for record in self.records
                if isinstance(record, dict) and str(record.get("topic", "")).lower() == topic.lower()
            ]

    def close(self):
        """Close the database connection."""
        return None