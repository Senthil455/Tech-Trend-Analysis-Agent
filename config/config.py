from pydantic import BaseSettings

class Config(BaseSettings):
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

    class Config:
        env_file = ".env"