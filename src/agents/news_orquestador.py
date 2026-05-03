import os
import sys

# Aseguramos que Python encuentre la carpeta src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.scrapers.hn_scraper import HNScraper
from src.agents.scrapers.reddit_scraper import RedditScraper
from src.agents.scrapers.rss_scraper import RSSScraper
from src.agents.writer_agent import WriterAgent
from src.agents.image_agent import ImageAgent
# Importa aquí tu función real de twitter_bot
# from twitter_bot import publicar_en_x 

def ejecutar_noticias():
    print("🚀 --- Iniciando Flujo de Noticias de Ruflo ---")
    
    # 1. Definimos los scrapers en orden de prioridad
    fuentes = [
        HNScraper(), 
        RedditScraper(), 
        RSSScraper()
    ]
    
    noticia_seleccionada = None

    # 2. Intentamos obtener una noticia válida
    for scraper in fuentes:
        try:
            print(f"🔎 Probando con: {type(scraper).__name__}...")
            resultado = scraper.fetch_news()
            
            if resultado:
                noticia_seleccionada = resultado
                print(f"✅ Noticia encontrada en {resultado['source']}: {resultado['title']}")
                break # Detenemos la búsqueda al encontrar la primera
        except Exception as e:
            print(f"⚠️ Error en {type(scraper).__name__}: {e}")
            continue

    if not noticia_seleccionada:
        print("📭 No se encontraron noticias nuevas que coincidan con config.py")
        return

    # 3. Redacción del Tweet
    print("✍️  Redactando tweet...")
    writer = WriterAgent()
    # Usamos el parámetro mode="noticia" para activar el prompt de periodista
    tweet_text = writer.redactar(noticia_seleccionada, mode="noticia")

    # 4. Generación de Imagen
    print("🎨 Generando imagen temática...")
    artista = ImageAgent()
    # Usamos el título de la noticia como base para la imagen
    ruta_imagen = artista.generar(noticia_seleccionada['title'], mode="noticia")

    # 5. Publicación final
    print(f"📤 Publicando en X...")
    print(f"--- TWEET ---\n{tweet_text}\n--------------")
    
    # Descomenta esta línea cuando estés listo para publicar de verdad:
    # publicar_en_x(tweet_text, ruta_imagen)
    
    print("🎯 ¡Proceso de noticias finalizado con éxito!")

if __name__ == "__main__":
    ejecutar_noticias()