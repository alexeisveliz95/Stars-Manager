import requests
import json
import os
from config import ALL_KEYWORDS

# Renombrada a HNScraper y método a fetch_news() para consistencia con el orquestador
class HNScraper:
    def __init__(self):
        self.base_url = "https://hacker-news.firebaseio.com/v0"
        self.history_file = "data/news_history.json"

    def _load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                return json.load(f)
        return []

    def _save_history(self, news_id):
        history = self._load_history()
        history.append(news_id)
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, "w") as f:
            json.dump(history[-100:], f)  # Máximo 100 entradas

    def fetch_news(self):
        print("🔎 HNScraper: Buscando noticias relevantes...")
        history = self._load_history()

        try:
            response = requests.get(
                f"{self.base_url}/topstories.json", timeout=10
            )
            if response.status_code != 200:
                print(f"❌ HNScraper: HTTP {response.status_code}")
                return None

            top_ids = response.json()[:50]

            for item_id in top_ids:
                if item_id in history:
                    continue

                item_resp = requests.get(
                    f"{self.base_url}/item/{item_id}.json", timeout=10
                )
                if item_resp.status_code != 200:
                    continue

                item = item_resp.json()
                if not item:
                    continue

                title = item.get("title", "")
                url = item.get("url")

                if not url or not title:
                    continue

                if any(kw.lower() in title.lower() for kw in ALL_KEYWORDS):
                    print(f"🎯 Match en HN: {title}")
                    self._save_history(item_id)
                    return {
                        "title": title,
                        "url": url,
                        "source": "Hacker News",
                        "id": item_id,
                    }

            print("ℹ️ HNScraper: Sin noticias nuevas que coincidan.")
            return None

        except requests.Timeout:
            print("⚠️ HNScraper: Timeout al conectar con Hacker News.")
            return None
        except Exception as e:
            print(f"❌ HNScraper: {e}")
            return None