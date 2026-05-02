import requests
from bs4 import BeautifulSoup

def get_trending_repos():
    url = "https://github.com/trending"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200: return []
        
        soup = BeautifulSoup(response.text, 'lxml')
        repos = []
        
        articles = soup.find_all('article', class_='Box-row')
        for article in articles[:15]:
            h2_tag = article.find('h2', class_='h3')
            a_tag = h2_tag.find('a') if h2_tag else None
            
            if not a_tag: continue
            
            relative_path = a_tag['href'] 
            repo_name = relative_path.strip('/')
            repo_url = f"https://github.com{relative_path}"
            
            # Estrellas Totales
            stars_tag = article.find('a', href=lambda x: x and 'stargazers' in x)
            stars_str = stars_tag.get_text(strip=True).replace(',', '') if stars_tag else "0"
            
            # Crecimiento hoy
            growth_tag = article.find('span', class_='d-inline-block float-sm-right')
            growth_str = growth_tag.get_text(strip=True).split()[0].replace(',', '') if growth_tag else "0"

            repos.append({
                "name": repo_name,
                "html_url": repo_url,
                "description": article.find('p', class_='col-9').get_text(strip=True) if article.find('p', class_='col-9') else "Sin descripción",
                "stars": stars_str,
                "growth": growth_str
            })
        return repos
    except Exception as e:
        print(f"❌ Error en Scraper: {e}")
        return []