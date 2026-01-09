"""
Application configuration for MarketMinds Chatbot.

this module handles the configuration settings required for the backend application.
havind a dedicated config module allows for better organization and easier management of settings.
"""
from pathlib import Path


class AppConfig:
    BASE_DIR: Path = Path(__file__).resolve().parents[2]

    DATA_DIR: Path = BASE_DIR / "data"
    RAW_DATA_DIR: Path = DATA_DIR / "raw"
    PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
    VECTOR_STORE_DIR: Path = DATA_DIR / "vector_store"


    APP_NAME: str = "MarketMinds"
    DEBUG: bool = True
    DEFAULT_MODEL_NAME: str = "mistral"


config = AppConfig()


 