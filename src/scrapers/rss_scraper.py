import feedparser
import time
from src.config import ALL_KEYWORDS

class RSSScraper:
    def __init__(self):
        # Lista de feeds confiables
        self.feeds = [
            "https://techcrunch.com/feed/",
            "https://www.theverge.com/rss/frontpage/index.xml",
            "https://www.wired.com/feed/rss"
        ]

    def fetch_news(self):
        print("📰 RSSScraper: Revisando feeds de noticias...")
        
        for url in self.feeds:
            try:
                feed = feedparser.parse(url)
                
                for entry in feed.entries:
                    title = entry.title
                    link = entry.link
                    
                    # Filtrado por keywords de config.py
                    if any(kw.lower() in title.lower() for kw in ALL_KEYWORDS):
                        print(f"🎯 Match en RSS ({url}): {title}")
                        
                        return {
                            "title": title,
                            "url": link,
                            "source": "Tech News",
                            "id": link # Usamos la URL como ID único para el historial
                        }
                
                time.sleep(1) # Respeto entre feeds

            except Exception as e:
                print(f"❌ Error leyendo feed {url}: {e}")
        
        return None