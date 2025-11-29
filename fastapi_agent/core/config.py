"""
Configuration management using Pydantic Settings.
Loads environment variables from .env file.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    google_api_key: str
    gemini_model: str = "gemini-2.0-flash"  # Higher free tier limits (15/min vs 50/day for pro)

    django_api_url: str
    django_service_secret: str

    aws_ses_access_key_id: str
    aws_ses_secret_access_key: str
    aws_ses_region_name: str = "us-east-1"
    default_from_email: str

    frontend_url: str
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
