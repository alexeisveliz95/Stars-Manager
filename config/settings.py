from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str | None = None
    telegram_bot_token: str | None = None
    telegram_channel_id: str | None = None
    telegram_log_chat_id: str | None = None
    telegram_feed_chat_id: str | None = None
    x_api_key: str | None = None
    x_api_secret: str | None = None
    x_access_token: str | None = None
    x_access_token_secret: str | None = None

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
