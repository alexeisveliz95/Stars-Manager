import requests
from datetime import datetime
from typing import List

from models.content_item import ContentItem
from config.settings import settings


def get_starred_repos() -> List[ContentItem]:
    """Obtiene repositorios starred por el usuario y los devuelve como ContentItems."""
    settings.require_github()

    items: List[ContentItem] = []
    page = 1
    headers = {
        "Authorization": f"token {settings.stars_token}",
        "Accept": "application/vnd.github.v3+json",
    }

    while True:
        url = f"https://api.github.com/users/{settings.github_repository_owner}/starred?page={page}&per_page=100"

        try:
            response = requests.get(url, headers=headers, timeout=15)
        except requests.Timeout:
            print(f"⚠️ Timeout en página {page}")
            break

        if response.status_code == 403:
            remaining = response.headers.get("X-RateLimit-Remaining", "?")
            reset_time = response.headers.get("X-RateLimit-Reset", "?")
            print(f"❌ Rate limit alcanzado (restantes: {remaining}). Reset ≈ {reset_time}")
            break

        if response.status_code != 200:
            print(f"❌ Error API GitHub: HTTP {response.status_code}")
            break

        data = response.json()
        if not data:
            break

        for r in data:
            full_name = r["full_name"]
            item = ContentItem(
                id=f"github_starred_{full_name.replace('/', '_')}",
                source="github_starred",
                title=full_name,
                url=r["html_url"],
                summary=r.get("description"),
                score=0.0,
                momentum=0.0,  # Los starred no tienen "growth" como trending
                language=r.get("language"),
                owner=r["owner"]["login"],
                raw_data={
                    "stars": r["stargazers_count"],
                    "forks": r.get("forks_count"),
                    "topics": r.get("topics", []),
                    "updated_at": r.get("updated_at"),
                    "created_at": r.get("created_at"),
                    "page": page,
                },
                metadata={
                    "scraped_at": datetime.utcnow().isoformat(),
                    "source_type": "user_starred",
                    "api_page": page
                }
            )
            items.append(item)

        page += 1

    print(f"✅ GitHub Starred: {len(items)} repositorios cargados como ContentItem")
    return items