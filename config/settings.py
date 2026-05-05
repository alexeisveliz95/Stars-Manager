from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    groq_api_key: str
    telegram_bot_token: str
    telegram_log_chat_id: str
    telegram_feed_chat_id: str
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()