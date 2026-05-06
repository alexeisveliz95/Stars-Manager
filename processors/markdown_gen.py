import os
from datetime import datetime
from processors.classifier_old import clean_text

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _format_stars(n: int) -> str:
    """Formatea estrellas con sufijo k/m para compactar tablas."""
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}k"
    return str(n)

def _growth_bar(growth: int, max_growth: int, width: int = 10) -> str:
    """Barra de progreso unicode que representa el crecimiento relativo."""
    if max_growth == 0:
        return "░" * width
    filled = round((growth / max_growth) * width)
    filled = max(1, min(filled, width))
    return "█" * filled + "░" * (width - filled)

def _tier(stars: int) -> tuple:
    """Devuelve (emoji, label) según rango de estrellas."""
    if stars >= 100_000:
        return "🏆", "Elite · 100k+"
    if stars >= 10_000:
        return "🔥", "Popular · 10k+"
    if stars >= 1_000:
        return "⭐", "Notable · 1k+"
    return "🌱", "Emerging"

def _truncate(text: str, max_len: int = 100) -> str:
    """Recorta descripciones largas para que no rompan tablas."""
    text = clean_text(text)
    if len(text) <= max_len:
        return text
    return text[:max_len].rsplit(" ", 1)[0] + "…"


def save_all_files(organized_data: dict):
    categorias_dir = os.path.join(ROOT, "Categorias")
    os.makedirs(categorias_dir, exist_ok=True)

    for cat, repos in organized_data.items():
        if not repos:
            continue

        repos.sort(key=lambda x: x.stars, reverse=True)
        total = len(repos)
        top_stars = repos[0].stars if repos else 0
        total_stars = sum(r.stars for r in repos)

        filename = os.path.join(categorias_dir, f"{cat.replace(' ', '_')}.md")
        with open(filename, "w", encoding="utf-8") as f:

            # Header
            f.write(f"# 📂 {cat}\n\n")

            # Obsidian callout — resumen visual de la categoría
            f.write(f"> [!info] Resumen\n")
            f.write(f"> **{total} repos** curados · ")
            f.write(f"⭐ Top: **{_format_stars(top_stars)}** · ")
            f.write(f"Acumulado: **{_format_stars(total_stars)}** estrellas · ")
            f.write(f"Actualizado: `{datetime.now().strftime('%Y-%m-%d')}`\n\n")
            f.write("---\n\n")

            # Agrupar por tier
            tiers = [
                ("🏆 Elite", lambda r: r.stars >= 100_000),
                ("🔥 Popular", lambda r: 10_000 <= r.stars < 100_000),
                ("⭐ Notable", lambda r: 1_000 <= r.stars < 10_000),
                ("🌱 Emerging", lambda r: r.stars < 1_000),
            ]

            for tier_label, condition in tiers:
                tier_repos = [r for r in repos if condition(r)]
                if not tier_repos:
                    continue

                f.write(f"## {tier_label}\n\n")
                f.write("| Proyecto | ⭐ Stars | Descripción |\n")
                f.write("| :--- | ---: | :--- |\n")

                for r in tier_repos:
                    desc = _truncate(r.description or "Sin descripción", 90)
                    short_name = r.name.split("/")[-1] if "/" in r.name else r.name
                    name_link = f"[**{short_name}**]({r.html_url})"
                    f.write(f"| {name_link} | {_format_stars(r.stars)} | {desc} |\n")

                f.write("\n")

    _write_dashboard(organized_data)


def _write_dashboard(organized_data: dict):
    dashboard_path = os.path.join(ROOT, "DASHBOARD.md")
    total_repos = sum(len(v) for v in organized_data.values())
    active_cats = sum(1 for v in organized_data.values() if v)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    with open(dashboard_path, "w", encoding="utf-8") as f:
        f.write("# 🚀 Stars Manager — Dashboard\n\n")

        # Obsidian callout de estado general
        f.write(f"> [!tip] Estado del sistema\n")
        f.write(f"> 🕒 **Última sync:** {now}\n")
        f.write(f"> 📦 **{total_repos} repos** curados en ")
        f.write(f"**{active_cats} categorías** activas\n\n")
        f.write("---\n\n")

        # Tabla de categorías con top stars
        f.write("## 📌 Repositorios por Categoría\n\n")
        f.write("| Categoría | Repos | Top Stars |\n")
        f.write("| :--- | :---: | ---: |\n")

        for cat in sorted(organized_data.keys()):
            repos = organized_data[cat]
            if not repos:
                continue
            repos_sorted = sorted(repos, key=lambda x: x.stars, reverse=True)
            top = _format_stars(repos_sorted[0].stars)
            link = f"[**{cat}**](Categorias/{cat.replace(' ', '_')}.md)"
            f.write(f"| {link} | {len(repos)} | ⭐ {top} |\n")

        f.write("\n---\n\n")

        # Historial de tendencias
        f.write("## 📈 Historial de Tendencias\n\n")
        tendencias_dir = os.path.join(ROOT, "Tendencias")
        if os.path.exists(tendencias_dir):
            archivos = sorted(
                [a for a in os.listdir(tendencias_dir) if a.endswith(".md")],
                reverse=True
            )
            for archivo in archivos:
                fecha = archivo.replace("Trending-", "").replace(".md", "")
                f.write(f"- [{fecha}](Tendencias/{archivo})\n")
        else:
            f.write("_Sin reportes todavía._\n")


def save_trends(trending_data: list):
    tendencias_dir = os.path.join(ROOT, "Tendencias")
    os.makedirs(tendencias_dir, exist_ok=True)

    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(tendencias_dir, f"Trending-{date_str}.md")

    total = len(trending_data)
    max_growth = max((int(r.get("growth", 0)) for r in trending_data), default=1)
    total_growth = sum(int(r.get("growth", 0)) for r in trending_data)
    hot_count = sum(1 for r in trending_data if float(r.get("rank_score", 0)) > 100)

    # Repo #1 para el key insight
    top_repo = trending_data[0] if trending_data else None

    with open(filename, "w", encoding="utf-8") as f:

        # Header
        f.write(f"# 🔥 GitHub Trending — {date_str}\n\n")

        # Obsidian callout — resumen del día
        f.write(f"> [!info] Resumen del día\n")
        f.write(f"> **{total} repos** analizados · ")
        f.write(f"**{hot_count} en zona HOT** · ")
        f.write(f"**+{total_growth:,} estrellas** acumuladas en el top\n\n")

        # Key Insight — el repo más destacado del día
        if top_repo:
            top_name = top_repo["name"].split("/")[-1] if "/" in top_repo["name"] else top_repo["name"]
            top_growth = int(top_repo.get("growth", 0))
            top_stars = int(top_repo.get("stars", 0))
            top_url = top_repo.get("html_url", top_repo.get("url", "#"))
            top_desc = _truncate(top_repo.get("description", "Sin descripción"), 100)
            pct = (top_growth / top_stars * 100) if top_stars else 0

            f.write(f"> [!tip] 🏆 Key Insight — Repo del día\n")
            f.write(f"> **[{top_name}]({top_url})** lideró el trending con ")
            f.write(f"**+{top_growth:,} estrellas hoy** ")
            f.write(f"({pct:.2f}% de su total).\n")
            f.write(f"> _{top_desc}_\n\n")

        f.write("---\n\n")

        # Tabla compacta de ranking completo
        f.write("## 📊 Ranking de Momentum\n\n")
        f.write("| # | Repositorio | ⭐ Total | 🚀 Hoy | Momentum |\n")
        f.write("| :---: | :--- | ---: | ---: | :--- |\n")

        for i, r in enumerate(trending_data, 1):
            try:
                stars = int(r.get("stars", 0))
                growth = int(r.get("growth", 0))
            except (ValueError, TypeError):
                stars, growth = 0, 0

            score = float(r.get("rank_score", 0))
            status = "🔥" if score > 100 else "📈"
            bar = _growth_bar(growth, max_growth)
            url = r.get("html_url", r.get("url", "#"))
            name = r["name"].split("/")[-1] if "/" in r["name"] else r["name"]
            owner = r["name"].split("/")[0] if "/" in r["name"] else ""
            owner_str = f" `{owner}`" if owner else ""

            f.write(
                f"| {status} **{i}** | [**{name}**]({url}){owner_str} "
                f"| {_format_stars(stars)} | +{growth:,} | `{bar}` |\n"
            )

        f.write("\n---\n\n")

        # Cards de detalle para el top 5
        f.write("## 🏅 Top 5 — Detalle\n\n")
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]

        for i, r in enumerate(trending_data[:5]):
            try:
                stars = int(r.get("stars", 0))
                growth = int(r.get("growth", 0))
            except (ValueError, TypeError):
                stars, growth = 0, 0

            score = float(r.get("rank_score", 0))
            url = r.get("html_url", r.get("url", "#"))
            desc = _truncate(r.get("description", "Sin descripción"), 120)
            tier_emoji, tier_label = _tier(stars)
            bar = _growth_bar(growth, max_growth)
            medal = medals[i]
            full_name = r["name"]

            f.write(f"### {medal} [{full_name}]({url})\n\n")
            f.write(f"> [!note] {desc}\n\n")
            f.write("| Métrica | Valor |\n")
            f.write("| :--- | :--- |\n")
            f.write(f"| ⭐ Stars totales | **{stars:,}** · {tier_emoji} {tier_label} |\n")
            f.write(f"| 🚀 Crecimiento hoy | **+{growth:,}** |\n")
            f.write(f"| 📊 Momentum | `{bar}` |\n")
            f.write(f"| 🏷️ Score | `{score:.1f}` |\n")
            f.write("\n---\n\n")

    # Append al DASHBOARD: top 3 inline + link al reporte completo
    dashboard_path = os.path.join(ROOT, "DASHBOARD.md")
    existing = ""
    if os.path.exists(dashboard_path):
        with open(dashboard_path, "r", encoding="utf-8") as f:
            existing = f.read()

    if f"Trending-{date_str}" not in existing:
        top3 = trending_data[:3]
        with open(dashboard_path, "a", encoding="utf-8") as f:
            f.write(f"\n---\n\n## 🔥 Trending hoy · {date_str}\n\n")

            # Mini tabla de los top 3 inline — no hace falta abrir el reporte
            f.write("| # | Repo | 🚀 Hoy | ⭐ Total |\n")
            f.write("| :---: | :--- | ---: | ---: |\n")
            medals_short = ["🥇", "🥈", "🥉"]
            for j, r in enumerate(top3):
                try:
                    stars = int(r.get("stars", 0))
                    growth = int(r.get("growth", 0))
                except (ValueError, TypeError):
                    stars, growth = 0, 0
                name = r["name"].split("/")[-1] if "/" in r["name"] else r["name"]
                url = r.get("html_url", r.get("url", "#"))
                f.write(f"| {medals_short[j]} | [**{name}**]({url}) | +{growth:,} | {_format_stars(stars)} |\n")

            f.write(f"\n[📄 Ver reporte completo →](Tendencias/Trending-{date_str}.md)\n")