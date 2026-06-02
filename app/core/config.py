import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


class Settings:
    BASE_DIR = Path(__file__).resolve().parents[2]

    APP_NAME: str = os.getenv("APP_NAME", "Safe NL-to-SQL Analytics Assistant")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    APP_ENV: str = os.getenv("APP_ENV", "development")

    FLASK_HOST: str = os.getenv("FLASK_HOST", "127.0.0.1")
    FLASK_PORT: int = int(os.getenv("FLASK_PORT", "5000"))
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "True").lower() == "true"

    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-5-mini")

    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "data/safe_analytics.db")

    MAX_QUERY_ROWS: int = int(os.getenv("MAX_QUERY_ROWS", "100"))
    MAX_QUERY_SECONDS: int = int(os.getenv("MAX_QUERY_SECONDS", "5"))

    ENABLE_MUTEX: bool = os.getenv("ENABLE_MUTEX", "False").lower() == "true"
    APP_MUTEX_NAME: str = os.getenv(
        "APP_MUTEX_NAME",
        "safe_nl_to_sql_analytics_assistant",
    )

    ENABLE_API_KEY_AUTH: bool = (
        os.getenv("ENABLE_API_KEY_AUTH", "False").lower() == "true"
    )
    APP_API_KEY: str | None = os.getenv("APP_API_KEY")

    ENABLE_RATE_LIMITING: bool = (
        os.getenv("ENABLE_RATE_LIMITING", "True").lower() == "true"
    )

    RATE_LIMIT_STORAGE_URI: str = os.getenv(
        "RATE_LIMIT_STORAGE_URI",
        "memory://",
    )

    RATE_LIMIT_DEFAULT: str = os.getenv("RATE_LIMIT_DEFAULT", "100 per hour")
    RATE_LIMIT_QUERY: str = os.getenv("RATE_LIMIT_QUERY", "30 per minute")

    @property
    def database_full_path(self) -> Path:
        return self.BASE_DIR / self.DATABASE_PATH

    @property
    def data_dir(self) -> Path:
        return self.BASE_DIR / "data"

    @property
    def logs_dir(self) -> Path:
        return self.BASE_DIR / "logs"


settings = Settings()