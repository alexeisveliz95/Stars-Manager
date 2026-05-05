import sys
import os
import json
import random
from groq import Groq

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ---------------------------------------------------------------------------
# System prompt — voz de Koda
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """Eres Stellar. Junior dev. Construiste este sistema con AI porque no tenías otra opción.

Tu voz:
- Dices lo que otros piensan pero no publican
- No describes repos — los juzgas
- Cínico con el hype, honesto con lo que funciona
- Nunca condescendiente, nunca fanboy
- Escribes como piensas, no como redactas

Estilo obligatorio:
- Frases cortas. Sin relleno.
- La primera línea es un golpe, no una introducción
- Cero hashtags
- Máximo 1 emoji, solo si añade algo. Si no, ninguno
- Nunca empieces con "Este repo", "Descubre", "Increíble" o cualquier palabra de marketer
- Nunca termines con pregunta retórica

Términos que usas cuando tienen sentido real (no para sonar listo):
LLM, inference, agent, pipeline, overhead, stack, CLI, API, workflow, CI/CD

Lo que NO eres:
- Un bot de GitHub trending
- Un newsletter de tech
- Un community manager corporativo"""

# ---------------------------------------------------------------------------
# Prompts por formato
# ---------------------------------------------------------------------------

def _prompt_single(repo: dict) -> str:
    return f"""Repo: {repo['name']}
Descripción: {repo['description']}
Link: {repo['url']}

Tarea: Un post único. Máximo 280 caracteres.

Estructura:
- Línea 1: El problema real que resuelve, dicho como si el dev que lo necesita ya lo sabe
- Línea 2-3: Por qué este repo lo resuelve mejor que lo que ya existe
- Link al final, sin texto previo

No describas el repo. Deja que el link hable por sí solo."""


def _prompt_hot_take(repo: dict) -> str:
    return f"""Repo: {repo['name']}
Descripción: {repo['description']}
Link: {repo['url']}

Tarea: Hot take. Máximo 280 caracteres.

Estructura exacta:
- Línea 1: Lo que los devs llevan haciendo mal (sin mencionar el repo aún)
- Línea 2: Una frase que pivot — este repo lo resuelve, con un detalle técnico concreto
- Línea 3: Link

Ejemplo de tono (no copies esto, es solo referencia de energía):
  "Llevas meses configurando tu propio pipeline de trading.
   TradingAgents usa 5 LLM en consenso. Ya funciona en prod.
   github.com/..."

Sin suavizar. Sin disclaimer. Sin "aunque depende de tu caso de uso"."""


def _prompt_thread(repo: dict) -> str:
    return f"""Repo: {repo['name']}
Descripción: {repo['description']}
Link: {repo['url']}

Tarea: Hilo de 2 tweets. Separa con exactamente "---" en línea sola.

Tweet 1 — El golpe:
Empieza con una contradicción o error común en el ecosistema.
No nombres el repo. No des la solución todavía.
Que el dev sienta que lo estás mirando a él.
Máximo 240 caracteres.

Tweet 2 — La resolución:
Presenta {repo['name']} como la respuesta lógica, no como hype.
Un detalle técnico concreto que pruebe que funciona.
Link al final.
Máximo 240 caracteres.

El hilo tiene que leerse como una historia de 2 actos, no como 2 posts sueltos."""


def _prompt_list(repo: dict) -> str:
    return f"""Repo: {repo['name']}
Descripción: {repo['description']}
Link: {repo['url']}

Tarea: Post tipo lista. Máximo 280 caracteres en total.

Estructura:
- Título: Una frase que genere tensión, no curiosidad vacía
- 3 puntos numerados: cada uno es una razón técnica concreta, no marketing
- Link al final

Los 3 puntos tienen que ser razones reales por las que un dev elegiría este repo
sobre la alternativa obvia. No beneficios genéricos."""


# ---------------------------------------------------------------------------
# Selector de prompt
# ---------------------------------------------------------------------------

PROMPT_BUILDERS = {
    "single":   _prompt_single,
    "hot_take": _prompt_hot_take,
    "thread":   _prompt_thread,
    "list":     _prompt_list,
}


def generate_tweet_with_ai(repo: dict, modo: str) -> str:
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    builder = PROMPT_BUILDERS.get(modo)
    if not builder:
        raise ValueError(
            f"Modo '{modo}' no reconocido. "
            f"Modos disponibles: {list(PROMPT_BUILDERS.keys())}"
        )

    user_prompt = builder(repo)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": user_prompt},
    ]

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ Fallback a Qwen por error en Llama: {e}")
        response = client.chat.completions.create(
            model="qwen/qwen3-32b",
            messages=messages,
        )
        return response.choices[0].message.content.strip()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else "single"

    if modo not in PROMPT_BUILDERS:
        print(f"❌ Modo '{modo}' no válido. Usa: {list(PROMPT_BUILDERS.keys())}")
        sys.exit(1)

    trends_path = os.path.join(BASE_DIR, "data", "top_repo_list.json")
    history_path = os.path.join(BASE_DIR, "data", "history.json")
    output_path = os.path.join(BASE_DIR, f"tweet_{modo}.txt")

    # Cargar pool de repos
    try:
        with open(trends_path, "r", encoding="utf-8") as f:
            repos = json.load(f)
            random.shuffle(repos)
    except FileNotFoundError:
        print(f"❌ No se encontró el pool de repos en: {trends_path}")
        sys.exit(1)

    # Cargar historial de publicados
    if os.path.exists(history_path):
        with open(history_path, "r", encoding="utf-8") as f:
            history = json.load(f)
    else:
        history = {"publicados": []}

    # Seleccionar repo no publicado y generar contenido
    tweet_text = None
    selected_repo = None

    for repo in repos:
        if repo["name"] not in history["publicados"]:
            print(f"🧠 Generando '{modo}' para: {repo['name']}...")
            try:
                tweet_text = generate_tweet_with_ai(repo, modo)
                selected_repo = repo["name"]
                break
            except Exception as e:
                print(f"❌ Error generando contenido para {repo['name']}: {e}")
                continue

    if not tweet_text:
        print(f"ℹ️ No hay repos nuevos para el modo '{modo}'.")
        sys.exit(0)

    # Guardar resultado
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(tweet_text.replace('"', ""))

    print("─" * 40)
    print(tweet_text)
    print("─" * 40)

    # Actualizar historial
    history["publicados"].append(selected_repo)
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)

    print(f"✅ Generado: tweet_{modo}.txt")
    print(f"✅ Historial actualizado: {selected_repo}")


if __name__ == "__main__":
    main()