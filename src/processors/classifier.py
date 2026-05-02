import math
from config import CATEGORIES_DB

def clean_text(text):
    if not text: return ""
    # Eliminamos caracteres que rompen el formato Markdown y X
    cleaned = text.encode("ascii", "ignore").decode("ascii")
    return cleaned.replace("|", "-").replace("\n", " ").strip()

def assign_category(repo):
    # Unificamos el texto para análisis[cite: 5]
    text_to_analyze = f"{repo.name} {repo.description} {' '.join(repo.topics or [])}".lower()
    
    # Mejora: Categorización por orden de importancia en CATEGORIES_DB[cite: 1, 5]
    for category, keywords in CATEGORIES_DB.items():
        if any(kw.lower() in text_to_analyze for kw in keywords):
            return category
    return "Otros"


def calculate_score(stars_total, stars_today):

    try:
        total = int(stars_total)
        growth = int(stars_today)
    except (ValueError, TypeError):
        return 0

    if total == 0: return 0

    # Implementación del "Momentum Real" de tu estrategia
    # Premiamos que las estrellas de hoy sean una gran parte del total
    acceleration = (growth / total) * 50 
    
    # Ponderación: 70% crecimiento absoluto, 30% aceleración relativa
    score = (growth * 0.7) + (acceleration * 0.3)
    
    # Pequeño bonus por ser Open Source activo (si tiene muchas estrellas totales)[cite: 1]
    bonus_log = math.log10(total) * 2
    
    return round(score + bonus_log, 2)