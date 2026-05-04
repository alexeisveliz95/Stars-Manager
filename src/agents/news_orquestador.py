import os
import subprocess
import sys

from src.scrapers.hn_scraper import HNScraper 
from scrapers.reddit_scraper import RedditScraper
from scrapers.rss_scraper import RSSScraper
from agents.writer_agent import generate_tweet_with_ai

# 1. Configuración de rutas para que Koda encuentre sus herramientas
# BASE_DIR apunta a la raíz del proyecto para ubicar archivos temporales
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(BASE_DIR, "src"))


def ejecutar_noticias():
    print("🤖 --- Koda News Agent: Iniciando Flujo de Noticias ---")

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
            print(f"⚠️ Error en {type(scraper).__name__}: {e}")
            continue

    if not noticia:
        print("📭 Sin noticias relevantes en este ciclo.")
        return

    # 2. Adaptación de la noticia para el WriterAgent
    repo_like = {
        "name": noticia["title"],
        "description": noticia["title"],
        "url": noticia["url"],
    }

    # 3. Generación del contenido del tweet (Modo Single)
    print("✍️ Koda está redactando el post...")
    try:
        tweet_text = generate_tweet_with_ai(repo_like, modo="single")
    except Exception as e:
        print(f"❌ Error redactando el tweet: {e}")
        return

    # 4. CREACIÓN DEL ARCHIVO TEMPORAL (Crucial para TwitterBot e ImageAgent)
    # Definimos el modo "single" para que coincida con la lógica de tus otros scripts
    modo = "single"
    archivo_texto = f"tweet_{modo}.txt"
    path_texto = os.path.join(BASE_DIR, archivo_texto)

    with open(path_texto, "w", encoding="utf-8") as f:
        # Limpiamos comillas accidentales para un tweet más limpio
        f.write(tweet_text.replace('"', ""))
    print(f"📝 Archivo preparado: {archivo_texto}")

    # 5. LLAMADA AL IMAGE AGENT (Subproceso externo)
    # Esto asegura que se use la lógica de image_agent_3.py sin modificarlo
    print("🎨 Koda solicitando generación de imagen...")
    try:
        # El agente de imagen leerá tweet_single.txt y generará image_single.png
        script_image = os.path.join(BASE_DIR, "src", "agents", "image_agent.py")
        subprocess.run(["python", script_image, modo], check=True)
        print(f"✅ Imagen generada con éxito como image_{modo}.png")
    except Exception as e:
        print(f"⚠️ Error en ImageAgent: {e} - Se intentará publicar solo texto.")

    # 6. LLAMADA AL TWITTER BOT (Subproceso externo)
    # El bot de Twitter leerá el texto, buscará la imagen y la archivará
    print(f"📤 Koda activando la publicación en X...")
    try:
        # twitter_bot_3.py busca automáticamente la imagen correspondiente al texto
        script_twitter = os.path.join(BASE_DIR, "src", "utils", "twitter_bot.py")
        subprocess.run(["python", script_twitter, archivo_texto], check=True)
        print("🎯 ¡Koda ha publicado la noticia con éxito!")
    except Exception as e:
        print(f"❌ Error al ejecutar el bot de Twitter: {e}")

if __name__ == "__main__":
    ejecutar_noticias()