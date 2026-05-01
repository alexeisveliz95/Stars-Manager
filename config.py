import os

TOKEN = os.getenv("STARS_TOKEN")
USER = os.getenv("GITHUB_REPOSITORY_OWNER")

CATEGORIES_DB = {
    # 🧠 La joya de la corona actual
    "AI & Data Science": ["ai", "ml", "llm", "gpt", "pytorch", "tensorflow", "neural", "deep learning", "langchain", "stable diffusion", "midjourney", "openai"],
    
    # 🎮 El nuevo nicho estratégico
    "PlayStation Homebrew & Linux": ["ps4", "ps5", "playstation", "ps4-linux", "ps5-linux", "homebrew", "jailbreak", "orbis", "prospero", "exploit", "payload"],
    
    # 🛡️ Siempre en tendencia y con mucho engagement
    "Cybersecurity & Hacking": ["security", "hacking", "pentest", "malware", "vulnerability", "infosec", "osint", "cryptography"],
    
    # 🕸️ El ecosistema cripto (muy activo en GitHub)
    "Web3 & Blockchain": ["blockchain", "crypto", "ethereum", "smart-contract", "web3", "solidity", "defi", "nft"],
    
    # 🏗️ El pan de cada día del desarrollo
    "Web Development": ["react", "vue", "html", "css", "javascript", "typescript", "frontend", "nextjs", "tailwind"],
    
    # ⚙️ Los motores
    "Python & Backend": ["fastapi", "django", "flask", "sql", "redis", "postgres", "mongodb", "api", "node"],
    
    # 🤖 Herramientas que ahorran tiempo (muy buenas para monetizar)
    "Automation & DevOps": ["automation", "bot", "cli", "scraping", "workflow", "docker", "kubernetes", "ci-cd", "aws", "terraform"],
    
    # 📱 Desarrollo Móvil
    "Mobile Development": ["android", "ios", "flutter", "react-native", "swift", "kotlin"]
}