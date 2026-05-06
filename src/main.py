import json
import os
import sys

# 1. Ajuste de rutas para importaciones
# Añadimos 'src' al path para que Python encuentre scrapers, processors, etc.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from connectors.inputs.github_stars import get_starred_repos
from connectors.inputs.trending import get_trending_repos
from processors.classifier import assign_category, calculate_score
from processors.markdown_gen import save_all_files, save_trends

# 2. Configuración de rutas raíz
BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR      = os.path.join(BASE_DIR, "data")
TOP_REPO_FILE = os.path.join(DATA_DIR, "top_repo_list.json")


def run():
    # ── Stellar monitoring ────────────────────────────────────────────────
    try:
        from utils.stellar_logger import setup_stellar_monitoring, notify_workflow_end
        setup_stellar_monitoring("🔄 Stars Sync")
    except ImportError:
        setup_stellar_monitoring = lambda *a, **k: None
        notify_workflow_end      = lambda *a, **k: None
    # ─────────────────────────────────────────────────────────────────────

    print("🚀 Iniciando Radar de Inteligencia...")

    # Asegurar que la carpeta data existe
    os.makedirs(DATA_DIR, exist_ok=True)

    all_stars = get_starred_repos()
    organized = {}
    for repo in all_stars:
        cat = assign_category(repo)
        if cat not in organized:
            organized[cat] = []
        organized[cat].append(repo)

    # Tendencias con Ranking
    print("🔥 Buscando tendencias en GitHub...")
    trending_global = get_trending_repos()

    for repo in trending_global:
        s_total  = repo.get("stars", 0)
        s_growth = repo.get("growth", 0)
        repo["rank_score"] = calculate_score(s_total, s_growth)

    # Ordenar por score
    trending_global.sort(key=lambda x: x.get("rank_score", 0), reverse=True)

    # Guardar archivos Markdown
    save_all_files(organized)
    save_trends(trending_global)
    print("✅ Todo actualizado correctamente.")

    # Exportar el JSON a la carpeta data en la raíz
    # Guard: solo sobreescribir si hay datos — evita borrar el pool si el scraper falla
    if trending_global:
        with open(TOP_REPO_FILE, "w", encoding="utf-8") as f:
            data_to_export = []
            for r in trending_global[:20]:  # 20 repos = ~3 semanas de contenido sin repetir
                data_to_export.append({
                    "name":        r["name"],
                    "description": r["description"],
                    "growth":      r["growth"],
                    "stars":       r["stars"],
                    "url":         r.get("html_url", r.get("url")),
                })
            json.dump(data_to_export, f, indent=4)
        print(f"✅ JSON exportado en: {TOP_REPO_FILE} ({len(data_to_export)} repos)")
    else:
        print("⚠️  Scraper devolvió lista vacía — top_repo_list.json no fue modificado.")

    print("✅ Todo listo. Testigo preparado para el Agente Social.")
    notify_workflow_end(success=True)


if __name__ == "__main__":
    run()