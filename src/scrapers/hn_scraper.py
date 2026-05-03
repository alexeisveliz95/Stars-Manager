import requests
import json
import os
from config import ALL_KEYWORDS

class NewsScraper:
    def __init__(self):
        self.base_url = "https://hacker-news.firebaseio.com/v0"
        self.history_file = "data/news_history.json"

    def _load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return []

    def _save_history(self, news_id):
        history = self._load_history()
        history.append(news_id)
        # Mantener solo los últimos 100 para no pesar
        with open(self.history_file, 'w') as f:
            json.dump(history[-100:], f)

    def fetch_trending_news(self):
        print("🔎 Buscando noticias que encajen con tus categorías...")
        history = self._load_history()
        
        try:
            # Obtener los IDs de las 50 noticias más top
            top_ids = requests.get(f"{self.base_url}/topstories.json").json()[:50]
            
            for item_id in top_ids:
                if item_id in history:
                    continue
                
                # Obtener detalle de la noticia
                item = requests.get(f"{self.base_url}/item/{item_id}.json").json()
                title = item.get("title", "")
                url = item.get("url")

                if not url or not title:
                    continue

                title_lower = title.lower()
                if any(kw.lower() in title_lower for kw in ALL_KEYWORDS):
                    print(f"🎯 ¡Match encontrado!: {title}")
                    
                    # Guardamos en el historial para no repetir
                    self._save_history(item_id)
                    
                    return {
                        "title": title,
                        "url": url,
                        "source": "Hacker News",
                        "id": item_id
                    }
            
            print("--- No se encontraron noticias nuevas con tus keywords ---")
            return None

        except Exception as e:
            print(f"❌ Error en NewsScraper: {e}")
            return None

if __name__ == "__main__":
    scraper = NewsScraper()
    noticia = scraper.fetch_trending_news()
    if noticia:
        print(f"Noticia lista para procesar: {noticia['title']}")