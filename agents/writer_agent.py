import json
import os
from groq import Groq

def generate_tweet_with_ai(repo):
    # 1. Crear el cliente centralizado
    client = Groq(api_key=os.environ.get("AI_API_KEY"))
    
    prompt = [
        {
            "role": "user",
            "content": (
                f"Actúa como un experto en tecnología. Crea un hilo de 2 posts para X sobre el repo: {repo['name']}.\n\n"
                f"POST 1: Un gancho (hook) increíble sobre la utilidad del repo. Sin links. Máximo 250 caracteres.\n"
                f"POST 2: Una frase corta de invitación y el link: {repo['url']}\n\n"
                f"SEPARA LOS POSTS CON EL SÍMBOLO '---'.\n"
                f"REGLAS:\n"
                f"- Tono humano y técnico.\n"
                f"- Descripción: {repo['description']}"
            )
        }
    ]


    #  Llamada a la API usando el nuevo método
    try:
        # Probamos con el nombre limpio (sin prefijos)
        response = client.chat.completions.create(
            model='llama-3.3-70b-versatile', 
            messages=prompt
        )
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        # Si falla, intentamos con la versión específica que nunca falla
        print(f"⚠️ Reintentando con versión específica por error: {e}")
        response = client.chat.completions.create(
            model='qwen/qwen3-32b', 
            messages=prompt
        )
        return response.choices[0].message.content.strip()

def main():
    # 1. Cargar tendencias
    try:
        with open("top_repo_list.json", "r", encoding="utf-8") as f:
            repos = json.load(f)
    except FileNotFoundError:
        print("❌ No se encontró el archivo de tendencias.")
        return

    # 2. Cargar historial
    history_path = "data/history.json"
    if os.path.exists(history_path):
        with open(history_path, "r", encoding="utf-8") as f:
            history = json.load(f)
    else:
        history = {"publicados": []}

    # 3. Lógica de selección
    tweet_text = None
    selected_repo_name = None

    for repo in repos:
        if repo['name'] not in history['publicados']:
            print(f"🧠 Groq analizando: {repo['name']}...")
            try:
                tweet_text = generate_tweet_with_ai(repo)
                selected_repo_name = repo['name']
                break
            except Exception as e:
                print(f"❌ Error con Groq: {e}")
                continue

    

    # 4. Guardar para el bot de Twitter
    if tweet_text:
        with open("tweet_ready.txt", "w", encoding="utf-8") as f:
            # Limpiar posibles comillas que a veces pone la IA
            f.write(tweet_text.replace('"', ''))
        
        print("--- CONTENIDO DEL TWEET GENERADO ---")
        print(tweet_text)
        print("------------------------------------")
        
        history['publicados'].append(selected_repo_name)
        with open(history_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4)
        print("✅ Tweet generado con éxito por Groq.")
    else:
        print("ℹ️ Nada nuevo por hoy.")

if __name__ == "__main__":
    main()
