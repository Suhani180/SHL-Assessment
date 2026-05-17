"""
Environment configuration.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    NVIDIA_API_KEY: str

    MODEL_NAME: str = "meta/llama-3.1-8b-instruct"

    TOP_K: int = 10

    class Config:
        env_file = ".env"


settings = Settings()