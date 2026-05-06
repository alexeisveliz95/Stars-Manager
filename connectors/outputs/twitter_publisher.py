"""
twitter_publisher.py — Publisher para X (Twitter) via Tweepy v2.

Migrado desde twitter_bot.py. La lógica de archivos (leer .txt, archivar
imagen, limpiar artefactos) se movió a post_runner.py — este módulo
solo se ocupa de autenticar y publicar.

Secrets requeridos (GitHub Actions / .env):
    X_API_KEY            — API Key de tu app en X Developer Portal
    X_API_SECRET         — API Secret de tu app en X Developer Portal
    X_ACCESS_TOKEN       — Access Token de tu cuenta
    X_ACCESS_TOKEN_SECRET — Access Token Secret de tu cuenta

IMPORTANTE: tu app de X debe tener permisos Read and Write activados.
Regenera los access tokens después de cambiar los permisos.
"""

import os
import re
import tweepy

from config.settings import settings
from connectors.outputs.publisher import Publisher, PostResult


class TwitterPublisher(Publisher):
    """
    Publisher para X (Twitter).

    Usa dos clientes Tweepy en paralelo — es el modelo que impone la API:
        · API v1.1 (tweepy.API)    → único endpoint que acepta media_upload
        · API v2  (tweepy.Client)  → create_tweet, includes_threads support

    Estrategia de publicación:
        · Sin separador "---"  →  tweet único
        · Con separador "---"  →  hilo: cada parte como reply al tweet anterior
    """

    # Nota: platform_key="x" referencia el PlatformProfile en publisher.PROFILES.
    # El nombre del archivo es twitter_publisher.py por preferencia de estilo —
    # son cosas independientes.
    platform_key = "x"
    _url_pattern = re.compile(r"https?://\S+", re.IGNORECASE)

    def __init__(self):
        self._api_key             = settings.x_api_key
        self._api_secret          = settings.x_api_secret
        self._access_token        = settings.x_access_token
        self._access_token_secret = settings.x_access_token_secret

        # Los clientes se inicializan solo si las credenciales están presentes
        self._api_v1 = None
        self._client_v2 = None
        if self._credentials_present():
            self._setup_clients()

    # ------------------------------------------------------------------
    # Interfaz pública
    # ------------------------------------------------------------------

    def post(self, text: str, image_path: str | None = None) -> PostResult:
        """
        Publica en X. Soporta tweet único e hilos.

        Args:
            text:       Contenido generado por writer_agent.
                        Si contiene "---", cada parte se publica como
                        reply encadenado (hilo).
            image_path: Ruta absoluta a la imagen. Solo se adjunta
                        al primer tweet del hilo.

        Returns:
            PostResult con el tweet_id del primer tweet publicado.
        """
        # 1. Validar credenciales
        creds_error = self._check_credentials()
        if creds_error:
            return PostResult(success=False, platform=self.platform_key, error=creds_error)

        # 2. Modo ahorro X API: extraemos enlaces para evitar el coste
        # de "Content: Create (with URL)".
        sanitized_text, deferred_links = self._strip_links(text)

        # 3. Validar contenido contra el perfil de la plataforma
        warnings = self.validate(sanitized_text)
        for w in warnings:
            print(f"⚠️  TwitterPublisher: {w}")

        # 4. Subir imagen si existe
        media_id = None
        if image_path:
            media_id = self._upload_image(image_path)
            if media_id is None:
                print("⚠️  TwitterPublisher: fallo al subir imagen — publicando solo texto.")

        # 5. Splitear en partes si es hilo
        separator = self.profile.thread_separator
        parts = [p.strip() for p in sanitized_text.split(separator) if p.strip()]

        try:
            if len(parts) <= 1:
                result = self._post_single(parts[0], media_id)
            else:
                result = self._post_thread(parts, media_id)

            if deferred_links:
                result.metadata["deferred_links"] = deferred_links
                result.metadata["link_strategy"] = "defer_external_links"
            return result
        except Exception as e:
            return PostResult(
                success=False,
                platform=self.platform_key,
                error=f"Error inesperado al publicar: {e}",
            )

    def _strip_links(self, text: str) -> tuple[str, list[str]]:
        """Elimina URLs del texto para evitar el tier caro por publicación con enlace."""
        links = self._url_pattern.findall(text)
        cleaned = self._url_pattern.sub("", text)
        cleaned = "\n".join(line.rstrip() for line in cleaned.splitlines())
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
        return cleaned, links

    # ------------------------------------------------------------------
    # Estrategias internas
    # ------------------------------------------------------------------

    def _post_single(self, text: str, media_id: str | None) -> PostResult:
        """Publica un tweet único."""
        print("🐦 TwitterPublisher: publicando tweet único...")
        media_ids = [media_id] if media_id else None

        response = self._client_v2.create_tweet(text=text, media_ids=media_ids)
        return self._build_result(response)

    def _post_thread(self, parts: list[str], media_id: str | None) -> PostResult:
        """
        Publica un hilo: el primer tweet lleva la imagen,
        cada parte siguiente se encadena como reply al anterior.
        """
        print(f"🧵 TwitterPublisher: publicando hilo de {len(parts)} partes...")

        # Primer tweet — con imagen si existe
        media_ids = [media_id] if media_id else None
        first = self._client_v2.create_tweet(text=parts[0], media_ids=media_ids)

        result = self._build_result(first)
        if not result.success:
            return result

        previous_id = first.data["id"]

        # Tweets siguientes — encadenados como reply
        for i, part in enumerate(parts[1:], start=2):
            print(f"   └─ parte {i}/{len(parts)}...")
            reply = self._client_v2.create_tweet(
                text=part,
                in_reply_to_tweet_id=previous_id,
            )
            reply_result = self._build_result(reply)

            if not reply_result.success:
                print(f"⚠️  TwitterPublisher: parte {i} del hilo falló — {reply_result.error}")
                # Devolvemos éxito parcial: el hilo empezó aunque no terminó
                return PostResult(
                    success=True,
                    platform=self.platform_key,
                    post_id=str(first.data["id"]),
                    error=f"Hilo incompleto: falló la parte {i} — {reply_result.error}",
                    metadata={"parts_published": i - 1, "parts_total": len(parts)},
                )

            previous_id = reply.data["id"]

        print(f"✅ TwitterPublisher: hilo completo ({len(parts)} partes publicadas)")
        return PostResult(
            success=True,
            platform=self.platform_key,
            post_id=str(first.data["id"]),
            metadata={"parts_published": len(parts), "parts_total": len(parts)},
        )

    # ------------------------------------------------------------------
    # Media upload
    # ------------------------------------------------------------------

    def _upload_image(self, image_path: str) -> str | None:
        """
        Sube la imagen via API v1.1 y devuelve el media_id_string.
        Devuelve None si falla — el caller decide si publicar sin imagen.
        """
        print(f"📸 TwitterPublisher: subiendo imagen '{os.path.basename(image_path)}'...")
        try:
            media = self._api_v1.media_upload(filename=image_path)
            print(f"   └─ media_id: {media.media_id_string}")
            return media.media_id_string
        except Exception as e:
            print(f"❌ TwitterPublisher: error al subir imagen — {e}")
            return None

    # ------------------------------------------------------------------
    # Setup de clientes Tweepy
    # ------------------------------------------------------------------

    def _setup_clients(self):
        """
        Inicializa los dos clientes Tweepy.

        v1 → media_upload (no disponible en v2)
        v2 → create_tweet (IMPORTANTE: siempre usar kwargs explícitos
             en tweepy.Client — el primer arg posicional es bearer_token,
             pasar api_key en ese slot provoca 401 silencioso)
        """
        auth = tweepy.OAuth1UserHandler(
            self._api_key,
            self._api_secret,
            self._access_token,
            self._access_token_secret,
        )
        self._api_v1 = tweepy.API(auth)

        self._client_v2 = tweepy.Client(
            consumer_key        = self._api_key,
            consumer_secret     = self._api_secret,
            access_token        = self._access_token,
            access_token_secret = self._access_token_secret,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _credentials_present(self) -> bool:
        return all([
            self._api_key,
            self._api_secret,
            self._access_token,
            self._access_token_secret,
        ])

    def _check_credentials(self) -> str | None:
        """
        Valida que todos los secrets estén presentes.
        Devuelve mensaje de error o None si todo está bien.
        """
        missing = [
            name for name, value in {
                "X_API_KEY":             self._api_key,
                "X_API_SECRET":          self._api_secret,
                "X_ACCESS_TOKEN":        self._access_token,
                "X_ACCESS_TOKEN_SECRET": self._access_token_secret,
            }.items()
            if not value
        ]
        if missing:
            return f"Faltan secrets: {', '.join(missing)}"
        return None

    def _build_result(self, response) -> PostResult:
        """
        Convierte la respuesta de tweepy.Client.create_tweet() en PostResult.

        tweepy devuelve un objeto Response con .data['id'] si tuvo éxito
        o lanza una excepción — no hay un campo 'ok' como en Telegram.
        """
        if response and response.data:
            tweet_id = str(response.data["id"])
            print(f"✅ TwitterPublisher: publicado (tweet_id: {tweet_id})")
            return PostResult(
                success=True,
                platform=self.platform_key,
                post_id=tweet_id,
            )
        return PostResult(
            success=False,
            platform=self.platform_key,
            error="Tweepy no devolvió datos — posible fallo silencioso de la API.",
        )
