from abc import ABC, abstractmethod
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Platform Profile
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PlatformProfile:
    """
    Define las capacidades y restricciones de una plataforma de publicación.
    Tanto writer_agent como cada Publisher consultan este objeto — única fuente
    de verdad para evitar que el agente genere contenido que el publisher
    luego no pueda manejar.
    """
    max_chars: int
    supports_markdown: bool       # negrita, cursiva, monospace, etc.
    supports_threads: bool        # publicación encadenada de mensajes
    supports_images: bool
    image_formats: list[str]      # formatos de imagen aceptados
    thread_separator: str = "---" # token que writer_agent usa para separar partes


# ---------------------------------------------------------------------------
# Registry de perfiles
# ---------------------------------------------------------------------------

PROFILES: dict[str, PlatformProfile] = {
    "x": PlatformProfile(
        max_chars       = 280,
        supports_markdown = False,
        supports_threads  = True,
        supports_images   = True,
        image_formats     = ["png", "jpg", "jpeg", "gif", "webp"],
        thread_separator  = "---",
    ),
    "telegram": PlatformProfile(
        max_chars         = 4096,
        supports_markdown = True,
        supports_threads  = False,
        supports_images   = True,
        image_formats     = ["png", "jpg", "jpeg", "gif", "webp"],
    ),
    "whatsapp": PlatformProfile(
        max_chars         = 1000,
        supports_markdown = False,
        supports_threads  = False,
        supports_images   = True,
        image_formats     = ["jpg", "jpeg", "png"],
    ),
}


# ---------------------------------------------------------------------------
# PostResult
# ---------------------------------------------------------------------------

@dataclass
class PostResult:
    """
    Resultado estandarizado que devuelve publisher.post().
    Permite al orquestador saber qué ocurrió sin depender de excepciones.
    """
    success: bool
    platform: str
    post_id: str | None = None     # ID del mensaje/tweet publicado si la API lo devuelve
    error: str | None = None       # mensaje de error legible si success=False
    metadata: dict = field(default_factory=dict)  # datos extra opcionales por plataforma


# ---------------------------------------------------------------------------
# Clase base abstracta
# ---------------------------------------------------------------------------

class Publisher(ABC):
    """
    Interfaz común para todos los publishers del sistema.

    Cada plataforma implementa esta clase y define:
      - platform_key  →  clave que referencia su PlatformProfile en PROFILES
      - post()        →  lógica concreta de publicación

    El orquestador solo interactúa con esta interfaz, lo que permite añadir
    plataformas nuevas sin modificar ningún código existente.

    Uso básico:
        publisher = XPublisher()
        profile   = publisher.profile          # consulta restricciones
        result    = publisher.post(text, image_path)
        if not result.success:
            print(result.error)
    """

    # Las subclases deben declarar su clave de plataforma
    platform_key: str = NotImplemented

    @property
    def profile(self) -> PlatformProfile:
        """Devuelve el PlatformProfile correspondiente a esta plataforma."""
        if self.platform_key not in PROFILES:
            raise ValueError(
                f"'{self.platform_key}' no tiene un PlatformProfile definido en PROFILES. "
                f"Plataformas disponibles: {list(PROFILES.keys())}"
            )
        return PROFILES[self.platform_key]

    def validate(self, text: str) -> list[str]:
        """
        Valida el texto contra el perfil de la plataforma antes de publicar.
        Devuelve una lista de errores — vacía si todo está bien.

        El publisher puede llamar a esto en post() para emitir warnings
        en lugar de fallar silenciosamente.
        """
        errors = []
        profile = self.profile

        if len(text) > profile.max_chars:
            errors.append(
                f"Texto demasiado largo: {len(text)} caracteres "
                f"(máximo {profile.max_chars} para {self.platform_key})"
            )

        if "---" in text and not profile.supports_threads:
            errors.append(
                f"{self.platform_key} no soporta hilos. "
                "El separador '---' será ignorado o causará un error en post()."
            )

        return errors

    @abstractmethod
    def post(self, text: str, image_path: str | None = None) -> PostResult:
        """
        Publica el contenido en la plataforma.

        Args:
            text:       Texto generado por writer_agent. Si la plataforma
                        soporta hilos, las partes vienen separadas por
                        profile.thread_separator.
            image_path: Ruta absoluta a la imagen. None si no hay imagen.

        Returns:
            PostResult con success=True y post_id si la publicación fue exitosa,
            o success=False y error con el motivo del fallo.
        """
        ...