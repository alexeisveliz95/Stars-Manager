import requests
import time
from src.config import ALL_KEYWORDS

class RedditScraper:
    def __init__(self):
        # Subreddits que encajan con tus categorías de config.py
        self.subreddits = [
            "MachineLearning", 
            "LocalLLM", 
            "netsec", 
            "jailbreak", 
            "selfhosted"
        ]
        # Reddit requiere un User-Agent único para no bloquearte
        self.headers = {'User-agent': 'RufloBot/1.0'}
        self.history_file = "data/news_history.json"

    def fetch_news(self):
        print("👾 RedditScraper: Buscando hilos interesantes...")
        
        for sub in self.subreddits:
            try:
                url = f"https://www.reddit.com/r/{sub}/top/.json?t=day&limit=10"
                response = requests.get(url, headers=self.headers)
                
                if response.status_code != 200:
                    continue

                data = response.json()
                posts = data['data']['children']

                for post in posts:
                    p_data = post['data']
                    title = p_data['title']
                    
                    # Filtrado usando tus categorías globales
                    if any(kw.lower() in title.lower() for kw in ALL_KEYWORDS):
                        # Evitamos posts que sean solo imágenes o videos sin link externo útil
                        link = p_data.get('url')
                        
                        print(f"🎯 Match en r/{sub}: {title}")
                        return {
                            "title": title,
                            "url": link if "reddit.com" not in link else f"https://www.reddit.com{p_data['permalink']}",
                            "source": f"Reddit r/{sub}",
                            "id": p_data['id']
                        }
                
                # Un pequeño sleep para no ser agresivos con la API
                time.sleep(1)

            except Exception as e:
                print(f"❌ Error scrapeando r/{sub}: {e}")
        
        return None