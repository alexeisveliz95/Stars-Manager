import os
import requests

from config.settings import settings
from connectors.outputs.publisher import Publisher, PostResult

# ---------------------------------------------------------------------------
# Límites internos de la API de Telegram
# (distintos del max_chars del PlatformProfile, que aplica al texto completo)
# ---------------------------------------------------------------------------
_CAPTION_MAX_CHARS = 1024   # límite de caption en sendPhoto
_BASE_URL = "https://api.telegram.org/bot{token}/{method}"


class TelegramPublisher(Publisher):
    """
    Publisher para canales y grupos de Telegram via Bot API.

    Secrets requeridos (GitHub Actions / .env):
        TELEGRAM_BOT_TOKEN   — token del bot (@BotFather)
        TELEGRAM_CHANNEL_ID  — ID del canal (@nombre o numérico, ej: -1001234567890)

    Estrategia de publicación:
        · Con imagen + texto <= 1024 chars  →  sendPhoto con caption
        · Con imagen + texto >  1024 chars  →  sendPhoto sin caption + sendMessage
        · Sin imagen                        →  sendMessage

    parse_mode:
        HTML por defecto — más robusto que MarkdownV2 (que requiere escapar
        muchos caracteres). El writer_agent puede generar HTML básico
        (<b>, <i>, <code>) cuando platform="telegram".
    """

    platform_key = "telegram"

    def __init__(self, parse_mode: str = "HTML"):
        """
        Args:
            parse_mode: Modo de formato del texto. "HTML" o "MarkdownV2".
                        Se ignora si el texto no contiene marcado.
        """
        self.parse_mode = parse_mode
        self._token = settings.telegram_bot_token
        self._channel_id = settings.telegram_channel_id

    # ------------------------------------------------------------------
    # Interfaz pública
    # ------------------------------------------------------------------

    def post(self, text: str, image_path: str | None = None) -> PostResult:
        """
        Publica texto y opcionalmente una imagen en el canal configurado.

        Args:
            text:       Contenido generado por writer_agent.
                        Telegram no soporta hilos — si el texto incluye '---'
                        se loguea un warning pero se publica el texto completo.
            image_path: Ruta absoluta a la imagen (.png / .jpg).

        Returns:
            PostResult con el message_id de Telegram si tuvo éxito.
        """
        # 1. Validar credenciales
        creds_error = self._check_credentials()
        if creds_error:
            return PostResult(success=False, platform=self.platform_key, error=creds_error)

        # 2. Validar contenido contra el perfil de la plataforma
        warnings = self.validate(text)
        for w in warnings:
            print(f"⚠️  TelegramPublisher: {w}")

        # 3. Elegir estrategia y publicar
        try:
            if image_path and os.path.exists(image_path):
                return self._post_with_image(text, image_path)
            else:
                if image_path:
                    print(f"⚠️  TelegramPublisher: imagen no encontrada en '{image_path}' — publicando solo texto.")
                return self._post_text(text)

        except Exception as e:
            return PostResult(
                success=False,
                platform=self.platform_key,
                error=f"Error inesperado: {e}",
            )

    # ------------------------------------------------------------------
    # Estrategias internas
    # ------------------------------------------------------------------

    def _post_text(self, text: str) -> PostResult:
        """Publica un mensaje de texto via sendMessage."""
        print("📨 TelegramPublisher: enviando mensaje de texto...")

        payload = {
            "chat_id":    self._channel_id,
            "text":       text,
            "parse_mode": self.parse_mode,
        }

        response = self._call("sendMessage", data=payload)
        return self._build_result(response)

    def _post_with_image(self, text: str, image_path: str) -> PostResult:
        """
        Publica imagen con caption si el texto cabe en 1024 chars.
        Si no cabe, envía la imagen sola y el texto como mensaje separado.
        """
        if len(text) <= _CAPTION_MAX_CHARS:
            print("📸 TelegramPublisher: enviando imagen con caption...")
            return self._send_photo(image_path, caption=text)
        else:
            print(
                f"📸 TelegramPublisher: texto ({len(text)} chars) excede el límite de caption "
                f"({_CAPTION_MAX_CHARS}). Enviando imagen y texto por separado..."
            )
            photo_result = self._send_photo(image_path, caption=None)
            if not photo_result.success:
                return photo_result

            text_result = self._post_text(text)
            # Devuelve el resultado del mensaje de texto — es el que tiene el contenido principal
            return text_result

    def _send_photo(self, image_path: str, caption: str | None) -> PostResult:
        """Llama a sendPhoto con o sin caption."""
        payload = {"chat_id": self._channel_id}
        if caption:
            payload["caption"] = caption
            payload["parse_mode"] = self.parse_mode

        with open(image_path, "rb") as img:
            response = self._call("sendPhoto", data=payload, files={"photo": img})

        return self._build_result(response)

    # ------------------------------------------------------------------
    # HTTP helper
    # ------------------------------------------------------------------

    def _call(self, method: str, data: dict, files: dict | None = None) -> requests.Response:
        """
        Ejecuta una llamada a la Bot API de Telegram.

        Args:
            method: Nombre del método (ej: "sendMessage", "sendPhoto").
            data:   Parámetros del payload.
            files:  Archivos a adjuntar (solo sendPhoto).
        """
        url = _BASE_URL.format(token=self._token, method=method)
        return requests.post(url, data=data, files=files, timeout=30)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _check_credentials(self) -> str | None:
        """
        Valida que los secrets estén presentes.
        Devuelve un mensaje de error o None si todo está bien.
        """
        missing = [
            name for name, value in {
                "TELEGRAM_BOT_TOKEN":  self._token,
                "TELEGRAM_CHANNEL_ID": self._channel_id,
            }.items()
            if not value
        ]
        if missing:
            return f"Faltan secrets: {', '.join(missing)}"
        return None

    def _build_result(self, response: requests.Response) -> PostResult:
        """
        Convierte la respuesta HTTP de Telegram en un PostResult estandarizado.

        La API de Telegram siempre devuelve JSON con {"ok": true/false, ...}.
        """
        try:
            body = response.json()
        except Exception:
            return PostResult(
                success=False,
                platform=self.platform_key,
                error=f"Respuesta no parseable: HTTP {response.status_code}",
            )

        if body.get("ok"):
            message_id = str(body["result"].get("message_id", ""))
            print(f"✅ TelegramPublisher: publicado correctamente (message_id: {message_id})")
            return PostResult(
                success=True,
                platform=self.platform_key,
                post_id=message_id,
                metadata={"chat_id": self._channel_id},
            )
        else:
            error_msg = body.get("description", "Error desconocido de la API")
            error_code = body.get("error_code", "?")
            print(f"❌ TelegramPublisher: error {error_code} — {error_msg}")
            return PostResult(
                success=False,
                platform=self.platform_key,
                error=f"[{error_code}] {error_msg}",
            )