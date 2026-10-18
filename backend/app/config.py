"""Settings loaded from the repo-root .env file."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


class Settings:
    """Environment-driven configuration. Read once at import time."""

    api_key: str = os.getenv("GEMINI_API_KEY", "")
    model: str = os.getenv("AI_MODEL", "gemini-2.5-flash")
    use_mock: bool = os.getenv("USE_MOCK", "false").lower() == "true"
    # Gemini 2.5 models "think" before answering, and thinking tokens count
    # toward this limit, so leave generous headroom.
    max_tokens: int = 8000
    request_timeout_s: float = 60.0


settings = Settings()