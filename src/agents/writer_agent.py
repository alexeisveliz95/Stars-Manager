import sys
import os
import json
import random
from groq import Groq

# 1. Configuración de rutas dinámicas[cite: 2, 4]
# Sube dos niveles desde src/agents/ hasta la raíz del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def generate_tweet_with_ai(repo, modo):
    """
    Genera contenido usando Groq con prompts específicos según el modo.
    Evita el tono genérico de IA usando jerga técnica y reglas de estilo.
    """
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    # CONTEXTO MAESTRO: Define la personalidad para evitar sonar como un robot
    system_context = (
        "Eres un Desarrollador Senior y Tech Influencer con 10k seguidores. "
        "Tu estilo es: Directo, técnico, un poco cínico con el software inflado y entusiasta con el minimalismo. "
        "REGLAS: Prohibido hashtags. Prohibido exclamaciones excesivas. "
        "Usa términos como: DX, boilerplate, overhead, stack, production-ready."
    )

    # ESTRATEGIAS DE PROMPT SEGÚN EL MODO SELECCIONADO
    if modo == "thread":
        # Estrategia DEEP DIVE: Problema real -> Solución técnica[cite: 1]
        user_prompt = (
            f"Repo: {repo['name']} - {repo['description']}\n"
            "Tarea: Crea un HILO de 2 posts.\n"
            "POST 1: Hook de impacto. Empieza con una crítica a una herramienta vieja o un problema de arquitectura. No nombres el repo aún.\n"
            "POST 2: Introduce {repo['name']}. Por qué es la solución moderna + Link: {repo['url']}\n"
            "SEPARA CON '---'"
        )
    elif modo == "list":
        # Estrategia VIRAL LIST: Formato rápido de leer[cite: 1]
        user_prompt = (
            f"Repo: {repo['name']} - {repo['description']}\n"
            "Tarea: Crea un post tipo LISTA.\n"
            "Estructura: '3 razones por las que este repo va a explotar'. "
            "Jerga técnica y directa. Link al final: {repo['url']}"
        )
    else:
        # Estrategia MOMENTUM: Post único potente[cite: 1]
        user_prompt = (
            f"Repo: {repo['name']} - {repo['description']}\n"
            "Tarea: Post único de alto impacto.\n"
            "Estructura: Beneficio inmediato para el flujo de trabajo + Link: {repo['url']}. "
            "Máximo 1 emoji técnico."
        )

    prompt = [
        {"role": "system", "content": system_context},
        {"role": "user", "content": user_prompt}
    ]

    # Lógica de fallback entre modelos para asegurar la publicación[cite: 4]
    try:
        response = client.chat.completions.create(
            model='llama-3.3-70b-versatile', 
            messages=prompt
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ Fallback a Qwen por error en Llama: {e}")
        response = client.chat.completions.create(
            model='qwen/qwen3-32b', 
            messages=prompt
        )
        return response.choices[0].message.content.strip()

def main():
    # 1. Capturar el modo desde el argumento del Workflow (ej: "single", "thread", "list")[cite: 1]
    modo = sys.argv[1] if len(sys.argv) > 1 else "single"
    
    # 2. Definir rutas absolutas a archivos en /data[cite: 2, 4]
    trends_path = os.path.join(BASE_DIR, "data", "top_repo_list.json")
    history_path = os.path.join(BASE_DIR, "data", "history.json")
    
    # El archivo de salida cambia según el modo para que el bot de Twitter sepa qué publicar
    output_filename = f"tweet_{modo}.txt"
    output_path = os.path.join(BASE_DIR, output_filename)

    # 3. Cargar tendencias
    try:
        with open(trends_path, "r", encoding="utf-8") as f:
            repos = json.load(f)
            random.shuffle(repos) # <--- Mezclamos la lista para no publicar siempre en orden
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo de tendencias en: {trends_path}")
        return

    # 4. Cargar historial de publicados[cite: 2, 4]
    if os.path.exists(history_path):
        with open(history_path, "r", encoding="utf-8") as f:
            history = json.load(f)
    else:
        history = {"publicados": []}

    # 5. Selección de repositorio no publicado[cite: 4]
    tweet_text = None
    selected_repo_name = None

    for repo in repos:

        if repo['name'] not in history['publicados']:
            print(f"🧠 Generando contenido '{modo}' para: {repo['name']}...")
            try:
                tweet_text = generate_tweet_with_ai(repo, modo)
                selected_repo_name = repo['name']
                break
            except Exception as e:
                print(f"❌ Error con Groq: {e}")
                continue

    # 6. Guardar resultado y actualizar historial[cite: 2, 4]
    if tweet_text:
        # Guardamos en la raíz para que el bot de Twitter lo vea fácilmente
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(tweet_text.replace('"', ''))
        
        history['publicados'].append(selected_repo_name)

        with open(history_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4)
        
        print(f"✅ Archivo generado: {output_filename}")
        print(f"✅ Historial actualizado con: {selected_repo_name}")
    else:
        print(f"ℹ️ No hay repositorios nuevos para el modo '{modo}'.")

if __name__ == "__main__":
    main()
