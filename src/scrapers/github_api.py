import requests
from models import Repo
from config import TOKEN, USER

def get_starred_repos() -> list[Repo]:
    repos = []
    page = 1
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }

    while True:
        url = f"https://api.github.com/users/{USER}/starred?page={page}&per_page=100"

        try:
            response = requests.get(url, headers=headers, timeout=15)
        except requests.Timeout:
            print(f"⚠️ Timeout en página {page} — se retornan los {len(repos)} repos obtenidos hasta ahora.")
            break

        # Rate limit explícito — distinto a otros errores
        if response.status_code == 403:
            remaining = response.headers.get("X-RateLimit-Remaining", "?")
            print(f"❌ Rate limit alcanzado (restantes: {remaining}). Repos cargados: {len(repos)}")
            break

        if response.status_code != 200:
            print(f"❌ Error API GitHub: HTTP {response.status_code} en página {page}")
            break

        data = response.json()
        if not data:
            break

        for r in data:
            repos.append(Repo(
                name=r["full_name"],        # "owner/repo" — necesario para links y deduplicación
                html_url=r["html_url"],
                description=r.get("description"),
                stars=r["stargazers_count"],
                language=r.get("language"),
                topics=r.get("topics", []),
            ))

        page += 1

    print(f"✅ GitHub API: {len(repos)} repos starred cargados.")
    return repos