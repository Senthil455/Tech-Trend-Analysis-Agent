from pydantic import BaseSettings

class Config(BaseSettings):
    """
    Configuration settings for the Tech Trend Analysis Agent.
    """
    db_url: str = "postgresql://user:password@localhost:5432/tech_trends"
    openai_api_key: str
    max_iterations: int = 8
    minimum_sources: int = 3
    emerging_threshold: int = 70
    growth_threshold: int = 30

    class Config:
        env_file = ".env"