"""
post_runner.py — Orquestador de publicación multiplataforma.

Sustituye al bloque `if __name__ == "__main__"` de twitter_bot.py y centraliza
todo el flujo de publicación: leer archivos, instanciar publishers, publicar
y limpiar artefactos.

Uso desde workflow / CLI:
    python src/social/post_runner.py <modo> <plataforma> [<plataforma> ...]

Ejemplos:
    python src/social/post_runner.py single twitter
    python src/social/post_runner.py single twitter telegram
    python src/social/post_runner.py thread telegram
"""

import os
import sys
import shutil
from datetime import datetime
from connectors.inputs.outputs.publish_log import append_publish_event

# ---------------------------------------------------------------------------
# Rutas base
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data", "history_images")

# ---------------------------------------------------------------------------
# Registry de publishers
# Añadir aquí cada nueva plataforma — post_runner no necesita más cambios.
# ---------------------------------------------------------------------------

def _get_publisher(platform: str):
    """
    Instancia el publisher correspondiente a la plataforma solicitada.
    Importación diferida para no cargar dependencias innecesarias.
    """
    if platform == "twitter":
        from connectors.inputs.outputs.twitter_publisher import TwitterPublisher
        return TwitterPublisher()
    if platform == "telegram":
        from connectors.inputs.outputs.telegram_publisher import TelegramPublisher
        return TelegramPublisher()
    raise ValueError(
        f"Plataforma '{platform}' no reconocida. "
        f"Plataformas disponibles: twitter, telegram"
    )

# ---------------------------------------------------------------------------
# Helpers de archivos
# ---------------------------------------------------------------------------

def _read_text(modo: str) -> str | None:
    """Lee el archivo de texto generado por writer_agent."""
    path = os.path.join(BASE_DIR, f"tweet_{modo}.txt")
    if not os.path.exists(path):
        print(f"❌ post_runner: no se encontró '{path}'. ¿Se ejecutó writer_agent?")
        return None
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    if not content:
        print(f"❌ post_runner: el archivo tweet_{modo}.txt está vacío.")
        return None
    return content


def _resolve_image(modo: str) -> str | None:
    """Devuelve la ruta de la imagen si existe, None si no."""
    path = os.path.join(BASE_DIR, f"image_{modo}.png")
    if os.path.exists(path):
        return path
    print(f"ℹ️  post_runner: no hay imagen para modo '{modo}' — se publicará solo texto.")
    return None


def _archive_image(image_path: str, modo: str):
    """Mueve la imagen a data/history_images/ con timestamp."""
    os.makedirs(DATA_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(DATA_DIR, f"{timestamp}_{modo}.png")
    shutil.move(image_path, dest)
    print(f"📁 post_runner: imagen archivada → data/history_images/{os.path.basename(dest)}")


def _cleanup(modo: str):
    """Elimina el archivo de texto temporal tras publicar."""
    path = os.path.join(BASE_DIR, f"tweet_{modo}.txt")
    if os.path.exists(path):
        os.remove(path)
        print(f"🧹 post_runner: eliminado tweet_{modo}.txt")

# ---------------------------------------------------------------------------
# Flujo principal
# ---------------------------------------------------------------------------

def run(modo: str, platforms: list[str]):
    """
    Ejecuta el flujo completo de publicación para el modo y plataformas dados.

    Args:
        modo:      Formato del contenido ("single", "list", "thread").
        platforms: Lista de plataformas destino ("twitter", "telegram", ...).

    Flujo:
        1. Leer texto generado por writer_agent
        2. Resolver ruta de imagen (opcional)
        3. Para cada plataforma → instanciar publisher → publicar
        4. Si al menos una publicación fue exitosa → archivar imagen + limpiar .txt
    """
    print(f"\n🚀 post_runner: modo='{modo}' | plataformas={platforms}\n")

    # 1. Leer artefactos generados por los agentes
    text = _read_text(modo)
    if not text:
        sys.exit(1)

    image_path = _resolve_image(modo)

    # 2. Publicar en cada plataforma
    results = []
    for platform in platforms:
        print(f"── Publicando en '{platform}' {'─' * 30}")
        try:
            publisher = _get_publisher(platform)
            result = publisher.post(text, image_path)
            results.append(result)

            if result.success:
                print(f"✅ '{platform}': publicado (id: {result.post_id})")
            else:
                print(f"❌ '{platform}': falló — {result.error}")

        except ValueError as e:
            print(f"❌ post_runner: {e}")
        except Exception as e:
            print(f"❌ '{platform}': error inesperado — {e}")

    print()

    # 3. Limpieza — solo si al menos una plataforma publicó correctamente
    any_success = any(r.success for r in results)

    append_publish_event(
        base_dir=BASE_DIR,
        mode=modo,
        text=text,
        image_used=bool(image_path),
        results=[
            {
                "platform": r.platform,
                "success": r.success,
                "post_id": r.post_id,
                "error": r.error,
                "metadata": r.metadata,
            }
            for r in results
        ],
    )

    if any_success:
        if image_path:
            _archive_image(image_path, modo)
        _cleanup(modo)
    else:
        print(
            "⚠️  post_runner: ninguna plataforma publicó correctamente. "
            "Los archivos temporales se conservan para debug."
        )
        sys.exit(1)

    # 4. Resumen final
    print("\n── Resumen " + "─" * 40)
    for r in results:
        status = "✅" if r.success else "❌"
        print(f"  {status} {r.platform:<12} id={r.post_id or '—':<20} error={r.error or '—'}")
    print()


# ---------------------------------------------------------------------------
# Entrada CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    """
    Argumentos:
        sys.argv[1]   — modo: "single" | "list" | "thread"
        sys.argv[2:]  — plataformas: "twitter" | "telegram" | ambas

    Ejemplos:
        python src/social/post_runner.py single twitter
        python src/social/post_runner.py single twitter telegram
        python src/social/post_runner.py thread telegram
    """
    if len(sys.argv) < 3:
        print("Uso: python post_runner.py <modo> <plataforma> [<plataforma> ...]")
        print("Ejemplo: python post_runner.py single twitter telegram")
        sys.exit(1)

    modo_arg      = sys.argv[1]
    platforms_arg = sys.argv[2:]

    run(modo_arg, platforms_arg)
