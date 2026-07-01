"""
Configuration module.
Loads and validates all environment variables at startup.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Central config class — all env vars live here."""

    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "5"))
    MAX_JD_LENGTH: int = int(os.getenv("MAX_JD_LENGTH", "5000"))
    MIN_JD_LENGTH: int = int(os.getenv("MIN_JD_LENGTH", "50"))
    MIN_RESUME_TEXT_LENGTH: int = int(os.getenv("MIN_RESUME_TEXT_LENGTH", "100"))

    @classmethod
    def validate(cls):
        """
        Validate that all required config values are present.
        Called once at app startup — fails fast if misconfigured.
        """
        if not cls.GOOGLE_API_KEY:
            raise ValueError(
                "GOOGLE_API_KEY is missing. "
                "Please set it in your .env file."
            )


# Single global config instance
config = Config()