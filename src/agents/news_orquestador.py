import os
import sys

# Añadimos src/ al path para que los imports funcionen igual que en el resto del proyecto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from scrapers.hn_scraper import HNScraper
from scrapers.reddit_scraper import RedditScraper
from scrapers.rss_scraper import RSSScraper
from agents.writer_agent import generate_tweet_with_ai
from agents.image_agent import generate_visual_prompt, download_hf_image
from social.twitter_bot import post_content

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def ejecutar_noticias():
    print("🚀 --- Iniciando Flujo de Noticias ---")

    # 1. Fuentes en orden de prioridad — HN primero por calidad, RSS último como fallback
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
            print(f"⚠️ Error en {type(scraper).__name__}: {e}")
            continue

    if not noticia:
        print("📭 Sin noticias nuevas que coincidan con las categorías configuradas.")
        return

    # 2. Adaptamos la noticia al formato que espera writer_agent
    repo_like = {
        "name": noticia["title"],
        "description": noticia["title"],
        "url": noticia["url"],
    }

    # 3. Generar tweet en modo "single" (formato más apropiado para noticias)
    print("✍️ Redactando tweet...")
    try:
        tweet_text = generate_tweet_with_ai(repo_like, modo="single")
    except Exception as e:
        print(f"❌ Error generando tweet: {e}")
        return

    # 4. Guardar tweet para que twitter_bot lo publique
    output_path = os.path.join(BASE_DIR, "tweet_single.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(tweet_text.replace('"', ""))
    print(f"✅ Tweet guardado en: tweet_single.txt")

    # 5. Generar imagen basada en el tweet
    print("🎨 Generando imagen...")
    try:
        v_prompt = generate_visual_prompt(tweet_text)
        download_hf_image(v_prompt, modo="single")
    except Exception as e:
        print(f"⚠️ Error generando imagen: {e} — continuando sin imagen.")

    print("🎯 Flujo de noticias completado.")
    print("--- TWEET GENERADO ---")
    print(tweet_text)
    print("----------------------")

    print(f"📤 Koda está publicando en X...")
    try:
        post_content(tweet_text) 
        print("🎯 ¡Post publicado con éxito!")
    except Exception as e:
        print(f"❌ Error al publicar en X: {e}")


if __name__ == "__main__":
    ejecutar_noticias()