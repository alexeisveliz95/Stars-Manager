import os
from datetime import datetime
from processors.classifier import clean_text

# 1. Definir la raíz del proyecto respecto a este archivo (sube dos niveles: src -> processors)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def save_all_files(organized_data):
    # 2. Usar rutas absolutas hacia la raíz
    categorias_dir = os.path.join(ROOT, "Categorias")
    os.makedirs(categorias_dir, exist_ok=True)
     
    for cat, repos in organized_data.items():
        if not repos: continue
        # Construir ruta completa
        filename = os.path.join(categorias_dir, f"{cat.replace(' ', '_')}.md")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# 📂 {cat}\n\n| Proyecto | Estrellas | Descripción | Link |\n| :--- | :--- | :--- | :--- |\n")
            repos.sort(key=lambda x: x.stars, reverse=True)
            for r in repos:
                f.write(f"| **{r.name}** | ⭐ {r.stars:,} | {clean_text(r.description)} | [🔗]({r.html_url}) |\n")

    # 3. El DASHBOARD también debe ir a la raíz
    dashboard_path = os.path.join(ROOT, "DASHBOARD.md")
    with open(dashboard_path, "w", encoding="utf-8") as f:
        f.write(f"# 🚀 AI Radar Dashboard\n")
        f.write(f"> 🕒 Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        
        f.write("## 📌 Mis Categorías (Curación Personal)\n")
        for cat in sorted(organized_data.keys()):
            if organized_data[cat]:
                # El enlace en Markdown debe seguir siendo relativo para Obsidian
                f.write(f"- [**{cat}**](Categorias/{cat.replace(' ', '_')}.md) ({len(organized_data[cat])} repos)\n")
        
        f.write("\n---\n")
        f.write("## 📈 Historial de Tendencias\n")
        f.write("Consulta los reportes diarios de crecimiento:\n")

        tendencias_dir = os.path.join(ROOT, "Tendencias")
        if os.path.exists(tendencias_dir):
            archivos_trends = sorted(os.listdir(tendencias_dir), reverse=True)
            for archivo in archivos_trends:
                if archivo.endswith(".md"):
                    fecha = archivo.replace("Trending-", "").replace(".md", "")
                    f.write(f"- [{fecha}](Tendencias/{archivo})\n")

def save_trends(trending_data):
    tendencias_dir = os.path.join(ROOT, "Tendencias")
    os.makedirs(tendencias_dir, exist_ok=True)
    date_str = datetime.now().strftime('%Y-%m-%d')
    filename = os.path.join(tendencias_dir, f"Trending-{date_str}.md")
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# 🔥 Tendencias GitHub - {date_str}\n\n")
        f.write("Análisis de crecimiento rápido vs. popularidad total.\n\n")
        f.write("| Ranking | Repositorio | Crecimiento | Total Stars | Link |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
        
        for i, r in enumerate(trending_data, 1):
            # Determinamos el status según el score de nuestro algoritmo
            status = "🔥 HOT" if float(r.get('rank_score', 0)) > 100 else "📈"
            
            # Formateamos el nombre como enlace
            name_link = f"[{r['name']}]({r['html_url']})"
            
            # Obtenemos los valores con seguridad (.get) y formateamos números con comas
            try:
                stars_total = int(r.get('stars', 0))
                growth_today = int(r.get('growth', 0))
            except ValueError:
                stars_total = 0
                growth_today = 0

            # Escribimos la fila principal
            f.write(f"| {i} | {status} **{name_link}** | 🚀 +{growth_today:,} | ⭐ {stars_total:,} | [🔗 Check Repo]({r['html_url']}) |\n")
            # Escribimos la descripción en una sub-fila para que no ensanche la tabla
            f.write(f"| | > *{clean_text(r.get('description', 'Sin descripción'))}* | | | |\n")


    dashboard_path = os.path.join(ROOT, "DASHBOARD.md")
    with open(dashboard_path, "a", encoding="utf-8") as f:
        f.write(f"\n\n## 📈 Último Análisis de Tendencias\n")
        # El enlace en el texto del MD se queda relativo para que Obsidian lo encuentre
        f.write(f"- [Ver tendencias del {date_str}](Tendencias/Trending-{date_str}.md)\n")