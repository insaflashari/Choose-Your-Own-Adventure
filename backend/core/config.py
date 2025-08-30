#config.py
#Settings Loader
#Purpose: Loads environment variables from .env and turns them into an object you can use anywhere.

#take environment variables and make them into a python object we can then use and reference throughout our code

from typing import List
from pydantic_settings import BaseSettings  # Base class for managing settings with validation
from pydantic import field_validator  # Allows us to add custom field validation/transform logic
import os  # Used to access environment variables

# This Settings class stores configuration for the app
# It automatically loads values from environment variables or a `.env` file.
class Settings(BaseSettings):
    API_PREFIX: str = "/api"  # Base URL prefix for all API endpoints
    DEBUG: bool = False  # Controls debug mode (affects database URL generation logic)

    DATABASE_URL: str   # The database connection string (set dynamically if not in debug mode)

    ALLOWED_ORIGINS: str = ""  # Comma-separated list of origins allowed for CORS requests

    OPENAI_API_KEY: str  # API key for OpenAI services (must be set in environment variables)

    # Custom initialization logic to build DATABASE_URL when DEBUG is False
    def __init__(self, **values):
        super().__init__(**values)
        if not self.DEBUG:
            # Pull database credentials from environment variables
            db_user = os.getenv("DB_USER")
            db_password = os.getenv("DB_PASSWORD")
            db_host = os.getenv("DB_HOST")
            db_port = os.getenv("DB_PORT")
            db_name = os.getenv("DB_NAME")
            # Format the DATABASE_URL string for SQLAlchemy/PostgreSQL
            self.DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    # Ensures ALLOWED_ORIGINS is stored as a list instead of a string
    @field_validator("ALLOWED_ORIGINS")
    def parse_allowed_origins(cls, v: str) -> List[str]:
        return v.split(",") if v else []

    class Config:
        env_file = ".env"  # Load variables from .env file
        env_file_encoding = "utf-8"  # Ensure UTF-8 encoding
        case_sensitive = True  # Environment variables are case-sensitive


# Create a single global instance of Settings to be imported and used throughout the app
settings = Settings()
