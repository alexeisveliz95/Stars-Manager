import os
import sys
import requests
import urllib.parse
import shutil
from datetime import datetime
from groq import Groq

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def generate_visual_prompt(tweet_content):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    # SYSTEM PROMPT: El "ADN" visual de tus imágenes
    system_prompt = (
        "You are a high-end technical illustrator specialized in minimalist blueprints. "
        "Your goal is to create a visual prompt for a technical drawing. "
        "\nVISUAL STYLE: "
        "- Background: Deep Navy Blue (hex #001122). "
        "- Lines: Ultra-thin, crisp white and cyan lines. "
        "- Subject: A minimalist isometric schematic of software architecture, nodes, or data structures. "
        "- Aesthetics: Professional, clean, engineering precision, technical annotations, grid system. "
        "\nRULES: "
        "1. Start with: 'A technical minimalist blueprint of...' "
        "2. Focus on structural geometric shapes. "
        "3. NO glows, NO neon, NO people, NO text. "
        "4. Everything in ENGLISH."
    )
    
    response = client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Create a technical blueprint prompt for: {tweet_content}"}
        ]
    )
    return response.choices[0].message.content.strip()

def download_and_persist(visual_prompt, modo):
    """Descarga la imagen y la guarda tanto para el bot como para el historial"""
    encoded_prompt = urllib.parse.quote(visual_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&enhance=true"
    
    # Rutas
    temp_output = os.path.join(BASE_DIR, f"image_{modo}.png")
    history_dir = os.path.join(BASE_DIR, "data", "history_images")
    os.makedirs(history_dir, exist_ok=True)
    
    print(f"📡 Generando imagen con estilo Blueprint Navy...")
    res = requests.get(url)
    
    if res.status_code == 200:
        # Guardar archivo temporal para el bot de Twitter
        with open(temp_output, 'wb') as f:
            f.write(res.content)
            
        # Guardar en historial con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_path = os.path.join(history_dir, f"{timestamp}_{modo}.png")
        shutil.copy2(temp_output, history_path)
        
        print(f"✅ Imagen lista para Twitter: {temp_output}")
        print(f"📁 Imagen guardada en historial: {history_path}")
        return True
    return False

def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else "single"
    input_file = os.path.join(BASE_DIR, f"tweet_{modo}.txt")

    if not os.path.exists(input_file):
        return

    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    v_prompt = generate_visual_prompt(content)
    download_and_persist(v_prompt, modo)

if __name__ == "__main__":
    main()