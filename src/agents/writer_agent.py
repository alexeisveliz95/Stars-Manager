import json
import os
import random
from groq import Groq

def generate_tweet_with_ai(repo, tipo_estrategia="momentum"):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    # Dentro del loop de repos en main()

    # 1. Definimos las plantillas basadas en tu documento "Stars-Manager"
    if tipo_estrategia == "deep_dive":
        template = (
            f"Estrategia: DEEP DIVE.\n"
            f"Estructura: Gancho de impacto sobre borrar herramientas antiguas + beneficios concretos.\n"
            f"Repo: {repo['name']} - {repo['description']}\n"
        )
    elif tipo_estrategia == "viral_list":
        template = (
            f"Estrategia: TOP SEMANAL.\n"
            f"Estructura: 'Los repos que están explotando' + métricas de momentum.\n"
            f"Repo: {repo['name']} - {repo['description']}\n"
        )
    else: # Momentum / Utility
        template = (
            f"Estrategia: MOMENTUM[cite: 1].\n"
            f"Estructura: Gancho increíble + utilidad técnica inmediata[cite: 1].\n"
            f"Repo: {repo['name']} - {repo['description']}\n"
        )

    prompt = [
        {
            "role": "system",
            "content": "Eres un Tech Influencer experto en crecimiento orgánico en X. Tu objetivo es llegar a 10k seguidores[cite: 1]."
        },
        {
            "role": "user",
            "content": (
                f"{template}\n"
                f"POST 1: Hook viral (máx 250 carac). Sin links. Usa emojis estratégicos[cite: 1].\n"
                f"POST 2: Valor técnico + Link: {repo['url']} + CTA (Call to Action)[cite: 1].\n"
                f"SEPARA CON '---'. REGLAS: Tono humano, cero robots, lenguaje para devs[cite: 1]."
            )
        }
    ]

    # Mantenemos tu lógica de reintentos con Qwen si falla Llama
    try:
        response = client.chat.completions.create(
            model='llama-3.3-70b-versatile', 
            messages=prompt
        )
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"⚠️ Reintentando con Qwen por error: {e}")
        response = client.chat.completions.create(
            model='qwen/qwen3-32b', 
            messages=prompt
        )
        return response.choices[0].message.content.strip()


def main():
    # 1. Cargar tendencias
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    trends_path = os.path.join(BASE_DIR, "data", "top_repo_list.json")
    history_path = os.path.join(BASE_DIR, "data", "history.json")
    output_path = os.path.join(BASE_DIR, "data", "tweet_ready.txt")

    try:
        with open(trends_path, "r", encoding="utf-8") as f:
            repos = json.load(f)
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo de tendencias en: {trends_path}")
        return
    
    # 2. Cargar historial    
    if os.path.exists(history_path):
        with open(history_path, "r", encoding="utf-8") as f:
            history = json.load(f)
    else:
        # Aseguramos que la carpeta data exista si no hay historial
        os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
        history = {"publicados": []}
    

    # 3. Lógica de selección
    tweet_text = None
    selected_repo_name = None

    for repo in repos:

        if repo['name'] not in history['publicados']:
            # Elegimos una personalidad diferente cada vez
            estrategias = ["momentum", "deep_dive", "viral_list"]
            selected_strategy = random.choice(estrategias)
            print(f"🧠 Groq analizando '{repo['name']}' con estrategia: {selected_strategy}...")
            
            try:
                # Pasamos la estrategia a tu función de IA evolucionada
                tweet_text = generate_tweet_with_ai(repo, selected_strategy)
                selected_repo_name = repo['name']
                break
            except Exception as e:
                print(f"❌ Error con Groq: {e}")
                continue

    
    # 4. Guardar para el bot de Twitter
    if tweet_text:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(tweet_text.replace('"', ''))

        print("--- CONTENIDO DEL TWEET GENERADO ---")
        print(tweet_text)
        print("------------------------------------")
               
        history['publicados'].append(selected_repo_name)
        # Guardar historial actualizado
        with open(history_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4)
        print(f"✅ Tweet generado y guardado en {output_path}")

if __name__ == "__main__":
    main()
