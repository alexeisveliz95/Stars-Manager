# NOTA: el orden de las categorías define la prioridad de clasificación.
# Un repo que matchea múltiples categorías cae en la primera que aparece aquí.
# Las categorías más específicas deben ir antes que las generales.
CATEGORIES_DB = {
    # 🧠 La joya de la corona actual
    "AI & Data Science": [
        "ai", "llm", "gpt", "pytorch", "tensorflow", "neural", "openai",
        "deep learning", "langchain", "stable diffusion", "midjourney"
        # "ml" omitido — matchea en "html", "email", etc. Cubierto por los demás keywords.
    ],

    # 🎮 El nuevo nicho estratégico
    # NOTA: keywords con guión ("ps4-linux") pueden no matchear con \b en algunos contextos.
    # Se incluyen las versiones sin guión como fallback.
    "PlayStation Homebrew & Linux": [
        "ps4", "ps5", "playstation", "homebrew", "jailbreak",
        "orbis", "prospero", "exploit", "payload",
        "ps4 linux", "ps5 linux",   # versión sin guión para topics de GitHub
    ],

    # 🛡️ Siempre en tendencia y con mucho engagement
    "Cybersecurity & Hacking": [
        "security", "hacking", "pentest", "malware", "vulnerability",
        "infosec", "osint", "cryptography"
    ],

    # 🕸️ El ecosistema cripto (muy activo en GitHub)
    "Web3 & Blockchain": [
        "blockchain", "crypto", "ethereum", "smart-contract", "web3",
        "solidity", "defi", "nft"
    ],

    # 🏗️ El pan de cada día del desarrollo
    "Web Development": [
        "react", "vue", "html", "css", "javascript", "typescript",
        "frontend", "nextjs", "tailwind"
    ],

    # ⚙️ Los motores — "node" va aquí antes que en Mobile para evitar falsos positivos
    "Python & Backend": [
        "fastapi", "django", "flask", "sql", "redis", "postgres",
        "mongodb", "node"
        # "api" omitido — matchea en "capability", "apiary", etc.
    ],

    # 🤖 Herramientas que ahorran tiempo (muy buenas para monetizar)
    "Automation & DevOps": [
        "automation", "cli", "scraping", "workflow", "docker",
        "kubernetes", "terraform", "ci-cd",
        # "bot" omitido — matchea en "robot". "aws" omitido — matchea en "password".
    ],

    # 📱 Desarrollo Móvil
    "Mobile Development": [
        "android", "ios", "flutter", "react-native", "swift", "kotlin"
    ],
}

# Keywords para trabajar con otros módulos posteriormente.
ALL_KEYWORDS = [kw for keywords in CATEGORIES_DB.values() for kw in keywords]
