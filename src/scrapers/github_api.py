import requests
from models import Repo
from config import TOKEN, USER

def get_starred_repos():
    repos = []
    page = 1
    headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    while True:
        url = f"https://api.github.com/users/{USER}/starred?page={page}&per_page=100"
        response = requests.get(url, headers=headers)
        if response.status_code != 200: 
            print(f"❌ Error API: {response.status_code}")
            break
        
        data = response.json()
        if not data: break
        
        for r in data:
            repos.append(Repo(
                name=r["name"],
                html_url=r["html_url"],
                description=r.get("description"),
                stars=r["stargazers_count"],
                language=r.get("language"),
                topics=r.get("topics", [])
            ))
        page += 1
    return repos