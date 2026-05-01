from config import CATEGORIES_DB

def clean_text(text):
    if not text: return ""
    return text.encode("ascii", "ignore").decode("ascii").replace("|", "-")

def assign_category(repo):
    text_to_analyze = f"{repo.name} {repo.description} {' '.join(repo.topics)}".lower()
    for category, keywords in CATEGORIES_DB.items():
        if any(kw in text_to_analyze for kw in keywords):
            return category
    return "Otros"


def calculate_score(stars_total, stars_today):
  
    try:
        total = int(stars_total)
        growth = int(stars_today)
    except:
        return 0

    # FÓRMULA: (Crecimiento diario * 0.8) + (Logaritmo del total * 0.2)
    # Usamos un peso mayor en el crecimiento para detectar "virales"
    score = (growth * 0.8) + (total * 0.05)
    return round(score, 2)