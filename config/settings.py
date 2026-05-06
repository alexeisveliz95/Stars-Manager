"""Centralized application settings.

All environment-driven configuration should be declared here so the rest of
application can depend on a single, typed settings object.
"""

from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict




class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables and ``.env``.

    Secrets are optional at startup because this repository runs multiple
    independent jobs (GitHub stars sync, content generation, Telegram/X
    publishing). Use the ``*_configured`` helpers or ``require`` methods to
    validate the variables needed by a specific feature before calling it.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # GitHub stars synchronization
    stars_token: str | None = Field(default=None, validation_alias="STARS_TOKEN")
    github_repository_owner: str | None = Field(
        default=None,
        validation_alias="GITHUB_REPOSITORY_OWNER",
    )

    # AI providers
    groq_api_key: str | None = Field(default=None, validation_alias="GROQ_API_KEY")
    hf_token: str | None = Field(default=None, validation_alias="HF_TOKEN")

    # Telegram content channel
    telegram_bot_token: str | None = Field(
        default=None,
        validation_alias="TELEGRAM_BOT_TOKEN",
    )
    telegram_channel_id: str | None = Field(
        default=None,
        validation_alias="TELEGRAM_CHANNEL_ID",
    )

    # Stellar operations/logging channel
    stellar_bot_token: str | None = Field(
        default=None,
        validation_alias="STELLAR_BOT_TOKEN",
    )
    stellar_channel_id: str | None = Field(
        default=None,
        validation_alias="STELLAR_CHANNEL_ID",
    )

    # X/Twitter publishing
    x_api_key: str | None = Field(default=None, validation_alias="X_API_KEY")
    x_api_secret: str | None = Field(default=None, validation_alias="X_API_SECRET")
    x_access_token: str | None = Field(default=None, validation_alias="X_ACCESS_TOKEN")
    x_access_token_secret: str | None = Field(
        default=None,
        validation_alias="X_ACCESS_TOKEN_SECRET",
    )

    @property
    def github_configured(self) -> bool:
        """Whether GitHub stars synchronization credentials are present."""

        return bool(self.stars_token and self.github_repository_owner)

    @property
    def github_headers(self) -> dict[str, str]:
        """HTTP headers for GitHub API calls."""

        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.stars_token:
            headers["Authorization"] = f"Bearer {self.stars_token}"
        return headers

    @property
    def telegram_configured(self) -> bool:
        """Whether Telegram content publishing credentials are present."""

        return bool(self.telegram_bot_token and self.telegram_channel_id)

    @property
    def stellar_configured(self) -> bool:
        """Whether the Stellar logging channel credentials are present."""

        return bool(self.stellar_bot_token and self.stellar_channel_id)

    @property
    def x_configured(self) -> bool:
        """Whether X/Twitter publishing credentials are present."""

        return all(
            (
                self.x_api_key,
                self.x_api_secret,
                self.x_access_token,
                self.x_access_token_secret,
            )
        )

    def require(self, *field_names: str) -> None:
        """Raise a clear error when required settings are missing.

        Args:
            *field_names: Attribute names from this settings class.

        Raises:
            ValueError: If any requested setting is not configured.
        """

        missing = [name for name in field_names if not getattr(self, name, None)]
        if missing:
            env_names = [self._env_name(name) for name in missing]
            raise ValueError(
                "Missing required environment variable(s): " + ", ".join(env_names)
            )

    def require_github(self) -> None:
        """Validate required settings for GitHub stars synchronization."""

        self.require("stars_token", "github_repository_owner")

    def require_telegram(self) -> None:
        """Validate required settings for Telegram content publishing."""

        self.require("telegram_bot_token", "telegram_channel_id")

    def require_stellar(self) -> None:
        """Validate required settings for Stellar logging notifications."""

        self.require("stellar_bot_token", "stellar_channel_id")

    def require_x(self) -> None:
        """Validate required settings for X/Twitter publishing."""

        self.require(
            "x_api_key",
            "x_api_secret",
            "x_access_token",
            "x_access_token_secret",
        )

    @classmethod
    def _env_name(cls, field_name: str) -> str:
        field = cls.model_fields[field_name]
        validation_alias: Any = field.validation_alias
        return str(validation_alias or field_name).upper()


settings = Settings()
