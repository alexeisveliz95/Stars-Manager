import requests

from config.settings import settings


class TelegramLogger:
    """Logger mínimo para enviar eventos del engine a Telegram."""

    def __init__(self):
        settings.require_telegram("log")
        self._token = settings.telegram_bot_token
        self._chat_id = settings.telegram_log_chat_id

    async def log_event(self, level: str, message: str, context: dict | None = None) -> None:
        payload = {
            "chat_id": self._chat_id,
            "text": self._format_message(level, message, context),
            "parse_mode": "HTML",
        }
        response = requests.post(
            f"https://api.telegram.org/bot{self._token}/sendMessage",
            data=payload,
            timeout=15,
        )
        if response.status_code != 200:
            raise RuntimeError(
                f"TelegramLogger falló con HTTP {response.status_code}: {response.text}"
            )

    def _format_message(
        self, level: str, message: str, context: dict | None = None
    ) -> str:
        context = context or {}
        lines = [f"<b>{level}</b> {message}"]
        for key, value in context.items():
            lines.append(f"<code>{key}</code>: {value}")
        return "\n".join(lines)
