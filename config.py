import os
from dataclasses import dataclass


@dataclass
class Config:
    google_api_key: str | None
    mock_mode: bool

    @classmethod
    def from_env(cls) -> "Config":
        google_key = os.getenv("GOOGLE_API_KEY")
        mock_mode = not bool(google_key)
        return cls(
            google_api_key=google_key,
            mock_mode=mock_mode,
        )


config = Config.from_env()
