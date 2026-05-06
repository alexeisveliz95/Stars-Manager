import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(BASE_DIR, "src"))

from connectors.inputs.hn_scraper import HNScraper        # noqa: E402
from connectors.inputs.reddit_scraper import RedditScraper  # noqa: E402
from connectors.inputs.rss_scraper import RSSScraper        # noqa: E402
from agents.writer_agent import generate_tweet_with_ai  # noqa: E402


def ejecutar_noticias():
    # ── Stellar monitoring ────────────────────────────────────────────────
    try:
        from utils.stellar_logger import setup_stellar_monitoring, notify_workflow_end
        setup_stellar_monitoring("📰 News Agent")
    except ImportError:
        setup_stellar_monitoring = lambda *a, **k: None
        notify_workflow_end      = lambda *a, **k: None
    # ─────────────────────────────────────────────────────────────────────

    print("🤖 --- Stellar News Agent: Iniciando Flujo de Noticias ---")

    # 1. Búsqueda de noticias en las fuentes configuradas
    fuentes = [
        HNScraper(),
        RedditScraper(),
        RSSScraper(),
    ]

    noticia = None
    for scraper in fuentes:
        try:
            resultado = scraper.fetch_news()
            if resultado:
                noticia = resultado
                print(f"✅ Noticia encontrada en {resultado['source']}: {resultado['title']}")
                break
        except Exception as e:
            print(f"⚠️  Error en {type(scraper).__name__}: {e}")
            continue

    if not noticia:
        print("📭 Sin noticias relevantes en este ciclo.")
        notify_workflow_end(success=True)
        return

    # 2. Adaptación de la noticia para el WriterAgent
    repo_like = {
        "name":        noticia["title"],
        "description": noticia["title"],
        "url":         noticia["url"],
    }

    # 3. Generación del contenido del tweet (Modo Single)
    print("✍️  Stellar está redactando el post...")
    try:
        tweet_text = generate_tweet_with_ai(repo_like, modo="single")
    except Exception as e:
        print(f"❌ Error redactando el tweet: {e}")
        notify_workflow_end(success=False, error=str(e))
        return

    # 4. Creación del archivo temporal
    modo         = "single"
    archivo_texto = f"tweet_{modo}.txt"
    path_texto   = os.path.join(BASE_DIR, archivo_texto)

    with open(path_texto, "w", encoding="utf-8") as f:
        f.write(tweet_text.replace('"', ""))
    print(f"📝 Archivo preparado: {archivo_texto}")

    # 5. Image Agent
    print("🎨 Stellar solicitando generación de imagen...")
    try:
        script_image = os.path.join(BASE_DIR, "src", "agents", "image_agent.py")
        if not os.path.exists(script_image):
            raise FileNotFoundError(f"image_agent.py no encontrado en: {script_image}")
        subprocess.run(["python", script_image, modo], check=True)
        print(f"✅ Imagen generada con éxito como image_{modo}.png")
    except Exception as e:
        print(f"⚠️  Error en ImageAgent: {e} — Se intentará publicar solo texto.")

    # 6. Twitter Bot
    print("📤 Stellar activando la publicación en X...")
    try:
        script_twitter = os.path.join(BASE_DIR, "src", "social", "post_runner.py")
        if not os.path.exists(script_twitter):
            raise FileNotFoundError(f"post_runner.py no encontrado en: {script_twitter}")
        subprocess.run(["python", script_twitter, archivo_texto], check=True)
        print("🎯 ¡Stellar ha publicado la noticia con éxito!")
        notify_workflow_end(success=True)
    except Exception as e:
        print(f"❌ Error al ejecutar el bot de Twitter: {e}")
        notify_workflow_end(success=False, error=str(e))


if __name__ == "__main__":
    ejecutar_noticias()