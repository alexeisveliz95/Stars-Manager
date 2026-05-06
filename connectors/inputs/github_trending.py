# connectors/inputs/github_trending.py   ← Recomiendo renombrar así

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List

from models.content_item import ContentItem


def _parse_number(text: str) -> int:
    """Convierte strings de GitHub a int (k, m, comas)."""
    if not text:
        return 0
    clean = text.strip().replace(',', '').lower().split()[0]
    try:
        if clean.endswith('k'):
            return int(float(clean[:-1]) * 1_000)
        if clean.endswith('m'):
            return int(float(clean[:-1]) * 1_000_000)
        return int(clean)
    except (ValueError, IndexError, TypeError):
        return 0


def get_trending_repos(period: str = "daily") -> List[ContentItem]:
    """
    Scraper mejorado de GitHub Trending.
    period puede ser: daily, weekly, monthly
    """
    url = f"https://github.com/trending?since={period}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()   # Mejor manejo de errores HTTP

        soup = BeautifulSoup(response.text, 'lxml')
        articles = soup.find_all('article', class_='Box-row')

        items: List[ContentItem] = []

        for rank, article in enumerate(articles[:25], 1):
            # --- Extracción más robusta ---
            h2 = article.find('h2', class_='h3')
            a_tag = h2.find('a') if h2 else None
            if not a_tag:
                continue

            relative_path = a_tag['href'].strip('/')
            repo_name = relative_path
            repo_url = f"https://github.com/{relative_path}"

            # Estrellas
            stars_tag = article.find('a', href=lambda x: x and 'stargazers' in x)
            stars = _parse_number(stars_tag.get_text(strip=True) if stars_tag else "")

            # Crecimiento (estrellas hoy)
            growth_tag = article.find('span', class_='d-inline-block float-sm-right')
            growth = _parse_number(growth_tag.get_text(strip=True) if growth_tag else "")

            # Descripción
            desc_tag = article.find('p', class_='col-9')
            description = desc_tag.get_text(strip=True) if desc_tag else ""

            # Lenguaje
            lang_tag = article.find('span', itemprop='programmingLanguage')
            language = lang_tag.get_text(strip=True) if lang_tag else None

            # Momentum mejorado
            momentum = growth / (stars + 1) if stars > 0 else growth * 0.1

            item = ContentItem(
                id=f"github_trending_{repo_name.replace('/', '_').replace('.', '_')}",
                source="github_trending",
                title=repo_name,
                url=repo_url,
                summary=description,
                score=0.0,                    # Se calcula después
                momentum=round(momentum, 4),
                language=language,
                owner=repo_name.split('/')[0],
                raw_data={
                    "stars": stars,
                    "growth": growth,
                    "rank": rank,
                    "period": period,
                    "full_html_snippet": str(article)[:600]
                },
                metadata={
                    "trending_rank": rank,
                    "scraped_at": datetime.utcnow().isoformat(),
                    "period": period,
                    "source_url": url
                }
            )
            items.append(item)

        print(f"✅ GitHub Trending ({period}): {len(items)} repositorios → ContentItem")
        return items

    except requests.exceptions.RequestException as e:
        print(f"❌ Error HTTP en GitHub Trending: {e}")
        return []
    except Exception as e:
        print(f"❌ Error inesperado en scraper trending: {e}")
        return []