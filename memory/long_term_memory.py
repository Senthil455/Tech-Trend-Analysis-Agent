import psycopg2
from psycopg2.extras import Json

class LongTermMemory:
    """
    Manages the long-term memory for storing historical trends and reports.
    """
    def __init__(self, db_url):
        self.db_url = db_url
        self.connection = psycopg2.connect(self.db_url)
        self._initialize_tables()

    def _initialize_tables(self):
        """Create necessary tables if they do not exist."""
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS trend_history (
                    id SERIAL PRIMARY KEY,
                    topic TEXT NOT NULL,
                    date DATE NOT NULL,
                    score NUMERIC NOT NULL,
                    data JSONB
                );
                """
            )
            self.connection.commit()

    def store_trend(self, topic, date, score, data):
        """Store a trend in the database."""
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO trend_history (topic, date, score, data)
                VALUES (%s, %s, %s, %s);
                """,
                (topic, date, score, Json(data))
            )
            self.connection.commit()

    def get_trend_history(self, topic):
        """Retrieve historical data for a specific topic."""
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT date, score, data FROM trend_history
                WHERE topic = %s
                ORDER BY date ASC;
                """,
                (topic,)
            )
            return cursor.fetchall()

    def close(self):
        """Close the database connection."""
        self.connection.close()