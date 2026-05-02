import requests
from bs4 import BeautifulSoup

def _parse_number(text: str) -> int:
    """Convierte strings de GitHub a int. Maneja comas, sufijos k/m y basura."""
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

def get_trending_repos():
    url = "https://github.com/trending"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"❌ Scraper: GitHub devolvió HTTP {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, 'lxml')
        repos = []
        
        articles = soup.find_all('article', class_='Box-row')
        for article in articles[:25]:  # GitHub muestra 25 — los necesitamos todos para el pool de 20
            h2_tag = article.find('h2', class_='h3')
            a_tag = h2_tag.find('a') if h2_tag else None
            
            if not a_tag:
                continue
            
            relative_path = a_tag['href']
            repo_name = relative_path.strip('/')
            repo_url = f"https://github.com{relative_path}"
            
            # Estrellas totales — convertidas a int
            stars_tag = article.find('a', href=lambda x: x and 'stargazers' in x)
            stars = _parse_number(stars_tag.get_text(strip=True)) if stars_tag else 0

            # Crecimiento hoy — convertido a int
            growth_tag = article.find('span', class_='d-inline-block float-sm-right')
            growth = _parse_number(growth_tag.get_text(strip=True)) if growth_tag else 0

            desc_tag = article.find('p', class_='col-9')
            description = desc_tag.get_text(strip=True) if desc_tag else "Sin descripción"

            repos.append({
                "name": repo_name,
                "html_url": repo_url,
                "description": description,
                "stars": stars,
                "growth": growth,
            })

        print(f"✅ Scraper: {len(repos)} repos extraídos de GitHub trending")
        return repos

    except Exception as e:
        print(f"❌ Error en Scraper: {e}")
        return []