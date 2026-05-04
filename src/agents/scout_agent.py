import os
import requests
from groq import Groq
from config import TOKEN

class ScoutAgent:
    def __init__(self):
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.client_groq = Groq(api_key=self.groq_key)
        self.languages = ["python", "typescript", "go", "rust", "csharp", "cpp", "mojo", "zig"]
        self.headers = {
            "Authorization": f"token {TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }

    def buscar_tendencias(self):
        joyas_validadas = []
        for lang in self.languages:
            url = f"https://api.github.com/search/repositories?q=language:{lang}+stars:>50&sort=stars&order=desc"

            try:
                res = requests.get(url, headers=self.headers, timeout=15)
            except requests.Timeout:
                print(f"⚠️ Timeout buscando repos de {lang} — saltando.")
                continue

            if res.status_code == 403:
                remaining = res.headers.get("X-RateLimit-Remaining", "?")
                print(f"❌ Rate limit alcanzado (restantes: {remaining}). Abortando scout.")
                break

            if res.status_code != 200:
                print(f"❌ Error API GitHub: HTTP {res.status_code} para lenguaje {lang}")
                continue

            data = res.json()
            if 'items' not in data:
                continue

            for repo in data['items'][:3]:
                if self._es_interesante(repo['full_name'], repo.get('description', '')):
                    joyas_validadas.append({
                        'name': repo['full_name'],       # "owner/repo" para consistencia con el resto
                        'url': repo['html_url'],
                        'desc': repo.get('description', ''),
                        'lang': lang
                    })

        return joyas_validadas

    def _es_interesante(self, nombre, descripcion):
        if not descripcion:
            return False

        prompt = f"¿Es '{nombre}' ({descripcion}) una herramienta o librería útil para devs? Responde solo SÍ o NO."
        try:
            chat = self.client_groq.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
            )
            return "SÍ" in chat.choices[0].message.content.upper()
        except Exception as e:
            print(f"⚠️ Error evaluando {nombre}: {e}")
            return False