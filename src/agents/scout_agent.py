import os
import requests
from groq import Groq

class ScoutAgent:
    def __init__(self):
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.client_groq = Groq(api_key=self.groq_key)
        self.languages = ["python", "typescript", "go", "rust", "csharp", "cpp", "mojo", "zig"]

    def buscar_tendencias(self):
        joyas_validadas = []
        for lang in self.languages:
            # Buscamos repos populares de la última semana
            url = f"https://api.github.com/search/repositories?q=language:{lang}+stars:>50&sort=stars&order=desc"
            res = requests.get(url).json()
            
            if 'items' in res:
                for repo in res['items'][:3]: # Evaluamos el top 3 de cada uno
                    if self._es_interesante(repo['name'], repo['description']):
                        joyas_validadas.append({
                            'name': repo['name'],
                            'url': repo['html_url'],
                            'desc': repo['description'],
                            'lang': lang
                        })
        return joyas_validadas

    def _es_interesante(self, nombre, descripcion):

        if not descripcion: return False
        
        prompt = f"¿Es '{nombre}' ({descripcion}) una herramienta o librería útil para devs? Responde solo SÍ o NO."
        chat = self.client_groq.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )
        return "SÍ" in chat.choices[0].message.content.upper()