from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: Optional[str] = None
    hf_token: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    telegram_log_chat_id: Optional[str] = None
    telegram_feed_chat_id: Optional[str] = None
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()