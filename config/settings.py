from typing import Iterable, Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str | None = Field(default=None, validation_alias="GROQ_API_KEY")
    hf_token: str | None = Field(default=None, validation_alias="HF_TOKEN")
    stars_token: str | None = Field(default=None, validation_alias="STARS_TOKEN")
    github_repository_owner: str | None = Field(
        default=None, validation_alias="GITHUB_REPOSITORY_OWNER"
    )

    telegram_bot_token: str | None = Field(
        default=None, validation_alias="TELEGRAM_BOT_TOKEN"
    )
    telegram_channel_id: str | None = Field(
        default=None, validation_alias="TELEGRAM_CHANNEL_ID"
    )
    telegram_log_chat_id: str | None = Field(
        default=None, validation_alias="TELEGRAM_LOG_CHAT_ID"
    )
    telegram_feed_chat_id: str | None = Field(
        default=None, validation_alias="TELEGRAM_FEED_CHAT_ID"
    )

    x_api_key: str | None = Field(default=None, validation_alias="X_API_KEY")
    x_api_secret: str | None = Field(default=None, validation_alias="X_API_SECRET")
    x_access_token: str | None = Field(default=None, validation_alias="X_ACCESS_TOKEN")
    x_access_token_secret: str | None = Field(
        default=None, validation_alias="X_ACCESS_TOKEN_SECRET"
    )

    class Config:
        env_file = ".env"
        extra = "ignore"

    def require_github(self) -> None:
        self._require_vars(["STARS_TOKEN", "GITHUB_REPOSITORY_OWNER"], "GitHub")

    def require_groq(self) -> None:
        self._require_vars(["GROQ_API_KEY"], "Groq")

    def require_huggingface(self) -> None:
        self._require_vars(["HF_TOKEN"], "Hugging Face")

    def require_telegram(
        self,
        purpose: Literal["channel", "log", "feed", "daily_engine"] = "channel",
    ) -> None:
        required_by_purpose = {
            "channel": ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHANNEL_ID"],
            "log": ["TELEGRAM_BOT_TOKEN", "TELEGRAM_LOG_CHAT_ID"],
            "feed": ["TELEGRAM_BOT_TOKEN", "TELEGRAM_FEED_CHAT_ID"],
            "daily_engine": [
                "TELEGRAM_BOT_TOKEN",
                "TELEGRAM_LOG_CHAT_ID",
                "TELEGRAM_FEED_CHAT_ID",
            ],
        }
        self._require_vars(required_by_purpose[purpose], "Telegram")

    def require_x(self) -> None:
        self._require_vars(
            [
                "X_API_KEY",
                "X_API_SECRET",
                "X_ACCESS_TOKEN",
                "X_ACCESS_TOKEN_SECRET",
            ],
            "X",
        )

    def _require_vars(self, variable_names: Iterable[str], service_name: str) -> None:
        missing = [name for name in variable_names if not self._env_value(name)]
        if missing:
            raise ValueError(
                f"Configuración incompleta para {service_name}. "
                f"Faltan variables de entorno: {', '.join(missing)}"
            )

    def _env_value(self, variable_name: str) -> str | None:
        field_by_env = {
            "GROQ_API_KEY": "groq_api_key",
            "HF_TOKEN": "hf_token",
            "STARS_TOKEN": "stars_token",
            "GITHUB_REPOSITORY_OWNER": "github_repository_owner",
            "TELEGRAM_BOT_TOKEN": "telegram_bot_token",
            "TELEGRAM_CHANNEL_ID": "telegram_channel_id",
            "TELEGRAM_LOG_CHAT_ID": "telegram_log_chat_id",
            "TELEGRAM_FEED_CHAT_ID": "telegram_feed_chat_id",
            "X_API_KEY": "x_api_key",
            "X_API_SECRET": "x_api_secret",
            "X_ACCESS_TOKEN": "x_access_token",
            "X_ACCESS_TOKEN_SECRET": "x_access_token_secret",
        }
        value = getattr(self, field_by_env[variable_name])
        return value.strip() if value else None


settings = Settings()
