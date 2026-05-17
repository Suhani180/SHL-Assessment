"""
Environment configuration.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    GEMINI_API_KEY: str

    MODEL_NAME: str = "gemini-1.5-flash"

    TOP_K: int = 10

    class Config:
        env_file = ".env"


settings = Settings()