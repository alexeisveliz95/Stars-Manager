import os
from datetime import datetime
from processors.classifier import clean_text

def save_all_files(organized_data):

    os.makedirs("Categorias", exist_ok=True)
     
    for cat, repos in organized_data.items():
        if not repos: continue
        filename = f"Categorias/{cat.replace(' ', '_')}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# 📂 {cat}\n\n| Proyecto | Estrellas | Descripción | Link |\n| :--- | :--- | :--- | :--- |\n")
            # Ordenar por estrellas de mayor a menor
            repos.sort(key=lambda x: x.stars, reverse=True)
            for r in repos:
                f.write(f"| **{r.name}** | ⭐ {r.stars:,} | {clean_text(r.description)} | [🔗]({r.html_url}) |\n")

    
    with open("DASHBOARD.md", "w", encoding="utf-8") as f:
        f.write(f"# 🚀 AI Radar Dashboard\n")
        f.write(f"> 🕒 Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        
        f.write("## 📌 Mis Categorías (Curación Personal)\n")
        for cat in sorted(organized_data.keys()):
            if organized_data[cat]:
                f.write(f"- [**{cat}**](Categorias/{cat.replace(' ', '_')}.md) ({len(organized_data[cat])} repos)\n")
        
        f.write("\n---\n")
        f.write("## 📈 Historial de Tendencias\n")
        f.write("Consulta los reportes diarios de crecimiento:\n")

        if os.path.exists("Tendencias"):
            # Listamos los archivos, los ordenamos de más nuevo a más viejo
            archivos_trends = sorted(os.listdir("Tendencias"), reverse=True)
            for archivo in archivos_trends:
                if archivo.endswith(".md"):
                    fecha = archivo.replace("Trending-", "").replace(".md", "")
                    f.write(f"- [{fecha}](Tendencias/{archivo})\n")

def save_trends(trending_data):

    os.makedirs("Tendencias", exist_ok=True)
    date_str = datetime.now().strftime('%Y-%m-%d')
    filename = f"Tendencias/Trending-{date_str}.md"
    
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

    with open("DASHBOARD.md", "a", encoding="utf-8") as f:
        f.write(f"\n\n## 📈 Último Análisis de Tendencias\n")
        f.write(f"- [Ver tendencias del {date_str}]({filename})\n")