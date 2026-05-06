import feedparser
import time
from config import ALL_KEYWORDS

class RSSScraper:
    def __init__(self):
        self.feeds = [
            "https://techcrunch.com/feed/",
            "https://www.theverge.com/rss/frontpage/index.xml",
            "https://www.wired.com/feed/rss",
        ]

    def fetch_news(self):
        print("📰 RSSScraper: Revisando feeds de noticias...")

        for url in self.feeds:
            try:
                feed = feedparser.parse(url)

                for entry in feed.entries:
                    title = entry.get("title", "")
                    link = entry.get("link", "")

                    if not title or not link:
                        continue

                    if any(kw.lower() in title.lower() for kw in ALL_KEYWORDS):
                        print(f"🎯 Match en RSS: {title}")
                        return {
                            "title": title,
                            "url": link,
                            "source": "Tech News",
                            "id": link,  # URL como ID único
                        }

                time.sleep(1)

            except Exception as e:
                print(f"❌ RSSScraper error en {url}: {e}")
                continue

        print("ℹ️ RSSScraper: Sin noticias nuevas que coincidan.")
        return None