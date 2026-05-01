import json
from scrapers.github_api import get_starred_repos
from scrapers.trending import get_trending_repos
from processors.classifier import assign_category, calculate_score
from processors.markdown_gen import save_all_files, save_trends

def run():
    print("🚀 Iniciando Radar de Inteligencia...")
    
    all_stars = get_starred_repos()
    organized = {}
    for repo in all_stars:
        cat = assign_category(repo)
        if cat not in organized: organized[cat] = []
        organized[cat].append(repo)
    
    # Tendencias con Ranking
    print("🔥 Buscando tendencias en GitHub...")
    trending_global = get_trending_repos()
    
    for repo in trending_global:
        # Usamos .get() para evitar el KeyError
        s_total = repo.get('stars', 0)
        s_growth = repo.get('growth', 0)
        repo['rank_score'] = calculate_score(s_total, s_growth)
    
    # Ordenar por score
    trending_global.sort(key=lambda x: x.get('rank_score', 0), reverse=True)
    
    # Guardar todo
    save_all_files(organized) 
    save_trends(trending_global) 
    print("✅ Todo actualizado correctamente.")

    with open("top_repo_list.json", "w", encoding="utf-8") as f:
        data_to_export = []
        for r in trending_global[:5]:
            data_to_export.append({
                "name": r['name'],
                "description": r['description'],
                "growth": r['growth'],
                "stars": r['stars'],
                "url": r['html_url']
            })
        json.dump(data_to_export, f, indent=4)
    
    print("✅ Todo listo. Testigo preparado para el Agente Social.")

if __name__ == "__main__":
    run()