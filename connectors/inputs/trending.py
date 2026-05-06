import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List

from models.content_item import ContentItem


def _parse_number(text: str) -> int:
    """Convierte strings de GitHub a int (maneja k, m, comas)."""
    if not text:
        return 0
    clean = text.strip().replace(',', '').lower().split()[0]
    try:
        if clean.endswith('k'):
            return int(float(clean[:-1]) * 1_000)
        if clean.endswith('m'):
            return int(float(clean[:-1]) * 1_000_000)
        return int(clean)
    except (ValueError, IndexError):
        return 0


def get_trending_repos() -> List[ContentItem]:
    """
    Scraper de GitHub Trending → devuelve List[ContentItem] directamente.
    """
    url = "https://github.com/trending"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"❌ Scraper: GitHub devolvió HTTP {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'lxml')
        items: List[ContentItem] = []
        
        articles = soup.find_all('article', class_='Box-row')

        for rank, article in enumerate(articles[:25], 1):
            h2_tag = article.find('h2', class_='h3')
            a_tag = h2_tag.find('a') if h2_tag else None

            if not a_tag:
                continue

            relative_path = a_tag['href']
            repo_name = relative_path.strip('/')
            repo_url = f"https://github.com{relative_path}"

            # Estrellas y crecimiento
            stars_tag = article.find('a', href=lambda x: x and 'stargazers' in x)
            stars = _parse_number(stars_tag.get_text(strip=True)) if stars_tag else 0

            growth_tag = article.find('span', class_='d-inline-block float-sm-right')
            growth = _parse_number(growth_tag.get_text(strip=True)) if growth_tag else 0

            desc_tag = article.find('p', class_='col-9')
            description = desc_tag.get_text(strip=True) if desc_tag else "Sin descripción"

            # Momentum aproximado (growth relativo)
            momentum = growth / (stars + 1) if stars > 0 else growth * 0.1

            item = ContentItem(
                id=f"github_trending_{repo_name.replace('/', '_')}",
                source="github_trending",
                title=repo_name,
                url=repo_url,
                summary=description,
                score=0.0,                    # Se calculará después
                momentum=round(momentum, 4),
                language=None,                # Se puede enriquecer después
                owner=repo_name.split('/')[0],
                raw_data={
                    "stars": stars,
                    "growth": growth,
                    "rank": rank,
                    "full_html": str(article)[:500]  # para debug
                },
                metadata={
                    "trending_rank": rank,
                    "scraped_at": datetime.utcnow().isoformat()
                }
            )
            items.append(item)

        print(f"✅ Scraper Trending: {len(items)} repositorios convertidos a ContentItem")
        return items

    except Exception as e:
        print(f"❌ Error en scraper trending: {e}")
        return []