import os

from pydantic import BaseModel

class Config(BaseModel):
    """
    Configuration settings for the Tech Trend Analysis Agent.
    """
    db_url: str = "sqlite:///trend_memory.db"
    openai_api_key: str = ""
    max_iterations: int = 8
    minimum_sources: int = 3
    minimum_score: int = 60
    emerging_threshold: int = 70
    growth_threshold: int = 30
    lookback_days: int = 7
    news_enabled: bool = True
    reddit_enabled: bool = True
    github_enabled: bool = True
    use_demo_data: bool = True

    def __init__(self, **values):
        environment_fields = {
            "db_url": "TREND_DB_URL",
            "openai_api_key": "OPENAI_API_KEY",
            "max_iterations": "TREND_MAX_ITERATIONS",
            "minimum_sources": "TREND_MINIMUM_SOURCES",
            "minimum_score": "TREND_MINIMUM_SCORE",
            "emerging_threshold": "TREND_EMERGING_THRESHOLD",
            "growth_threshold": "TREND_GROWTH_THRESHOLD",
            "lookback_days": "TREND_LOOKBACK_DAYS",
        }
        for field, variable in environment_fields.items():
            if field not in values and os.getenv(variable):
                values[field] = os.getenv(variable)
        super().__init__(**values)

