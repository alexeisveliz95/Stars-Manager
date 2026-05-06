import os
from datetime import datetime
from typing import List
from models.content_item import ContentItem

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _format_stars(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}k"
    return str(n)


def _growth_bar(momentum: float, max_momentum: float, width: int = 10) -> str:
    """Barra de progreso más elegante."""
    if max_momentum <= 0:
        return "░" * width
    filled = round((momentum / max_momentum) * width)
    filled = max(1, min(filled, width))
    return "█" * filled + "░" * (width - filled)


def _tier(stars: int) -> tuple:
    if stars >= 100_000:
        return "🏆", "Elite"
    if stars >= 10_000:
        return "🔥", "Popular"
    if stars >= 1_000:
        return "⭐", "Notable"
    return "🌱", "Emerging"


def _truncate(text: str, max_len: int = 110) -> str:
    if not text:
        return "Sin descripción"
    text = text.replace("\n", " ").strip()
    if len(text) <= max_len:
        return text
    return text[:max_len].rsplit(" ", 1)[0] + "…"


# ====================== MAIN FUNCTIONS ======================

def save_all_files(items: List[ContentItem]):
    """Guarda archivos por categoría con estética premium."""
    categorias_dir = os.path.join(ROOT, "Categorias")
    os.makedirs(categorias_dir, exist_ok=True)

    # Agrupar por categoría
    organized: dict = {}
    for item in items:
        main_cat = item.categories[0] if item.categories else "Otros"
        organized.setdefault(main_cat, []).append(item)

    for cat, cat_items in organized.items():
        if not cat_items:
            continue

        cat_items.sort(key=lambda x: x.score, reverse=True)
        total = len(cat_items)
        top_score = cat_items[0].score
        total_stars = sum(item.raw_data.get("stargazers_count", 0) for item in cat_items)

        filename = os.path.join(categorias_dir, f"{cat.replace(' ', '_')}.md")

        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# 📂 {cat}\n\n")

            # Callout premium
            f.write(f"> [!info] Resumen de Categoría\n")
            f.write(f"> **{total} proyectos** · ")
            f.write(f"⭐ Mejor score: **{top_score:.2f}** · ")
            f.write(f"Estrellas totales: **{_format_stars(total_stars)}**\n")
            f.write(f"> Actualizado: `{datetime.now().strftime('%Y-%m-%d %H:%M')}`\n\n")
            f.write("---\n\n")

            # Tabla principal
            f.write("## 📋 Proyectos Destacados\n\n")
            f.write("| Proyecto | Score | Stars | Momentum | Descripción |\n")
            f.write("| :--- | ---: | ---: | ---: | :--- |\n")

            for item in cat_items:
                stars = item.raw_data.get("stargazers_count", 0)
                short_name = item.title.split("/")[-1] if "/" in item.title else item.title
                name_link = f"[**{short_name}**]({item.url})"
                momentum_bar = _growth_bar(item.momentum, max((i.momentum for i in cat_items), default=1))

                desc = _truncate(item.summary or "", 95)

                f.write(
                    f"| {name_link} | **{item.score:.2f}** | "
                    f"{_format_stars(stars)} | `{momentum_bar}` | {desc} |\n"
                )

            f.write("\n---\n")

    _write_dashboard(organized)


def _write_dashboard(organized: dict):
    """Dashboard principal con estética premium."""
    dashboard_path = os.path.join(ROOT, "DASHBOARD.md")
    total_items = sum(len(v) for v in organized.values())
    active_cats = len([v for v in organized.values() if v])

    with open(dashboard_path, "w", encoding="utf-8") as f:
        f.write("# 🚀 Stellar Content Engine — Dashboard\n\n")

        f.write(f"> [!tip] **Estado del Sistema**\n")
        f.write(f"> 🕒 Última actualización: `{datetime.now().strftime('%Y-%m-%d %H:%M')}`\n")
        f.write(f"> 📦 **{total_items}** proyectos curados en **{active_cats}** categorías\n\n")
        f.write("---\n\n")

        f.write("## 📌 Categorías Activas\n\n")
        f.write("| Categoría | Proyectos | Mejor Score |\n")
        f.write("| :--- | :---: | ---: |\n")

        for cat in sorted(organized.keys()):
            items = organized[cat]
            if not items:
                continue
            best = max(items, key=lambda x: x.score)
            link = f"[**{cat}**](Categorias/{cat.replace(' ', '_')}.md)"
            f.write(f"| {link} | {len(items)} | **{best.score:.2f}** |\n")

        f.write("\n---\n\n")
        f.write("**Engine migrado a ContentItem Architecture**\n")


def save_trending_report(items: List[ContentItem], date_str: str = None):
    """Reporte de Trending con estética aún más fuerte."""
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    tendencias_dir = os.path.join(ROOT, "Tendencias")
    os.makedirs(tendencias_dir, exist_ok=True)

    filename = os.path.join(tendencias_dir, f"Trending-{date_str}.md")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# 🔥 GitHub Trending — {date_str}\n\n")

        f.write(f"> [!info] Resumen del día\n")
        f.write(f"> **{len(items)}** repositorios analizados · Top score: **{max((i.score for i in items), default=0):.2f}**\n\n")
        f.write("---\n\n")

        f.write("## 🏆 Top 10 - Momentum\n\n")
        f.write("| # | Proyecto | Score | Stars | Momentum |\n")
        f.write("| :---: | :--- | ---: | ---: | ---: |\n")

        max_momentum = max((item.momentum for item in items), default=1)

        for i, item in enumerate(items[:10], 1):
            stars = item.raw_data.get("stargazers_count", 0)
            bar = _growth_bar(item.momentum, max_momentum)
            short_name = item.title.split("/")[-1] if "/" in item.title else item.title

            f.write(
                f"| **{i}** | [**{short_name}**]({item.url}) | "
                f"**{item.score:.2f}** | {_format_stars(stars)} | `{bar}` |\n"
            )

        # Top 3 con detalle
        f.write("\n## 🥇 Detalle Top 3\n\n")
        for i, item in enumerate(items[:3]):
            medals = ["🥇", "🥈", "🥉"]
            desc = _truncate(item.summary or "", 130)
            f.write(f"### {medals[i]} [{item.title}]({item.url})\n\n")
            f.write(f"> [!note] {desc}\n\n")
            f.write(f"- **Score:** {item.score:.3f}\n")
            f.write(f"- **Momentum:** {item.momentum:.1f}\n")
            f.write(f"- **Categorías:** {', '.join(item.categories)}\n\n")
            f.write("---\n\n")

    print(f"✅ Reporte de trending guardado: {filename}")