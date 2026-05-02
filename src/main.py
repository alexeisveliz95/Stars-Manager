import json
import os
import sys

# 1. Ajuste de rutas para importaciones
# Añadimos 'src' al path para que Python encuentre scrapers, processors, etc.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.github_api import get_starred_repos
from scrapers.trending import get_trending_repos
from processors.classifier import assign_category, calculate_score
from processors.markdown_gen import save_all_files, save_trends

# 2. Configuración de rutas raíz[cite: 1, 2]
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
TOP_REPO_FILE = os.path.join(DATA_DIR, "top_repo_list.json")

def run():
    print("🚀 Iniciando Radar de Inteligencia...")
    
    # Asegurar que la carpeta data existe
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
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
        s_total = repo.get('stars', 0)
        s_growth = repo.get('growth', 0)
        repo['rank_score'] = calculate_score(s_total, s_growth)
    
    # Ordenar por score
    trending_global.sort(key=lambda x: x.get('rank_score', 0), reverse=True)
    
    # Guardar archivos Markdown (Asegúrate que save_all_files use la ruta raíz)[cite: 1, 3]
    # Si save_all_files no acepta rutas, tendrás que ajustarlo dentro de markdown_gen.py
    save_all_files(organized) 
    save_trends(trending_global) 
    print("✅ Todo actualizado correctamente.")

    # Exportar el JSON a la carpeta data en la raíz[cite: 2, 3]
    with open(TOP_REPO_FILE, "w", encoding="utf-8") as f:
        data_to_export = []
        for r in trending_global[:5]:
            data_to_export.append({
                "name": r['name'],
                "description": r['description'],
                "growth": r['growth'],
                "stars": r['stars'],
                "url": r.get('html_url', r.get('url')) # Manejo de clave por si varía[cite: 3]
            })
        json.dump(data_to_export, f, indent=4)
    
    print(f"✅ JSON exportado en: {TOP_REPO_FILE}")
    print("✅ Todo listo. Testigo preparado para el Agente Social.")

if __name__ == "__main__":
    run()