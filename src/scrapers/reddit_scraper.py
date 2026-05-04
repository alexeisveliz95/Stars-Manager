import requests
import json
import os
import time
from config import ALL_KEYWORDS

class RedditScraper:
    def __init__(self):
        self.subreddits = [
            "MachineLearning",
            "LocalLLM",
            "netsec",
            "selfhosted",
            "programming",
        ]
        self.headers = {"User-agent": "StarsManagerBot/1.0"}
        self.history_file = "data/news_history.json"

    def _load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                return json.load(f)
        return []

    def _save_history(self, post_id):
        history = self._load_history()
        if post_id not in history:
            history.append(post_id)
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, "w") as f:
            json.dump(history[-100:], f)

    def fetch_news(self):
        print("👾 RedditScraper: Buscando hilos relevantes...")
        history = self._load_history()

        for sub in self.subreddits:
            try:
                url = f"https://www.reddit.com/r/{sub}/top/.json?t=day&limit=10"
                response = requests.get(url, headers=self.headers, timeout=10)

                if response.status_code != 200:
                    print(f"⚠️ RedditScraper: HTTP {response.status_code} en r/{sub}")
                    continue

                posts = response.json().get("data", {}).get("children", [])

                for post in posts:
                    p = post["data"]
                    post_id = p["id"]

                    if post_id in history:
                        continue

                    title = p.get("title", "")
                    if any(kw.lower() in title.lower() for kw in ALL_KEYWORDS):
                        link = p.get("url", "")
                        permalink = f"https://www.reddit.com{p['permalink']}"

                        print(f"🎯 Match en r/{sub}: {title}")
                        self._save_history(post_id)
                        return {
                            "title": title,
                            "url": link if "reddit.com" not in link else permalink,
                            "source": f"Reddit r/{sub}",
                            "id": post_id,
                        }

                time.sleep(1)  # Respeto entre subreddits

            except requests.Timeout:
                print(f"⚠️ RedditScraper: Timeout en r/{sub}")
                continue
            except Exception as e:
                print(f"❌ RedditScraper error en r/{sub}: {e}")
                continue

        print("ℹ️ RedditScraper: Sin noticias nuevas que coincidan.")
        return None