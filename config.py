import os
from dataclasses import dataclass


@dataclass
class Config:
    anthropic_api_key: str | None
    google_api_key: str | None
    openai_api_key: str | None
    mock_mode: bool

    @classmethod
    def from_env(cls) -> "Config":
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        google_key = os.getenv("GOOGLE_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        mock_mode = not all([anthropic_key, google_key, openai_key])

        return cls(
            anthropic_api_key=anthropic_key,
            google_api_key=google_key,
            openai_api_key=openai_key,
            mock_mode=mock_mode,
        )


config = Config.from_env()
