import os
import sys
import requests
import urllib.parse
from datetime import datetime
from groq import Groq

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HISTORY_DIR = os.path.join(BASE_DIR, "data", "history_images")

def generate_visual_prompt(tweet_content):
    """Convierte el tweet en un prompt artístico para la IA de imagen"""
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    system_prompt = (
        "Eres un diseñador de planos técnicos (Blueprints) y arquitectura minimalista. "
        "Tu objetivo es crear un prompt de imagen que represente software de forma estructural. "
        "\nESTILO VISUAL OBLIGATORIO: "
        "- Fondo: Azul profundo de plano técnico (Navy Blueprint) o Negro mate de ingeniería. "
        "- Elementos: Líneas blancas finas, diagramas de flujo isométricos, cuadrículas milimétricas (grids). "
        "- Estética: Minimalista, técnica, limpia, tipo esquema de patentes o diagramas de sistemas de alta precisión. "
        "\nREGLAS DE COMPOSICIÓN: "
        "1. Usa metáforas geométricas: cubos para bases de datos, nodos para agentes, capas para frameworks. "
        "2. Evita efectos de brillo excesivo, nada de 'cyberpunk', nada de personas. "
        "3. El prompt debe ser en INGLÉS y empezar con: 'A technical minimalist blueprint of...' "
        "4. Incluye términos como: 'fine white lines', 'technical drawing', 'isometric schematic', 'blueprint aesthetic'."
    )
    
    response = client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Resume este tweet en un prompt visual de 20 palabras: {tweet_content}"}
        ]
    )
    return response.choices[0].message.content.strip()

def download_image(visual_prompt, output_path):
    """Descarga la imagen desde Pollinations.ai usando el prompt generado"""
    # Codificamos el prompt para que sea seguro en una URL
    encoded_prompt = urllib.parse.quote(visual_prompt)
    # Usamos parámetros para mejorar la calidad y evitar texto
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&enhance=true"
    
    print(f"📡 Solicitando imagen a Pollinations...")
    response = requests.get(image_url)
    
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            f.write(response.content)
        return True
    return False

def main():
    os.makedirs(HISTORY_DIR, exist_ok=True) # Asegurar que la carpeta existe
    modo = sys.argv[1] if len(sys.argv) > 1 else "single"
    
    # Nombre temporal para el bot de Twitter
    temp_output = os.path.join(BASE_DIR, f"image_{modo}.png")

    modo = sys.argv[1] if len(sys.argv) > 1 else "single"
    input_file = os.path.join(BASE_DIR, f"tweet_{modo}.txt")
    output_image = os.path.join(BASE_DIR, f"image_{modo}.png")

    if not os.path.exists(input_file):
        print(f"❌ No existe el archivo: {input_file}")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Generar prompt visual con Llama
    v_prompt = generate_visual_prompt(content)
    print(f"🎨 Prompt visual: {v_prompt}")

    # 2. Descargar la imagen
    if download_image(v_prompt, output_image):
        print(f"✅ Imagen guardada: {output_image}")
    else:
        print("❌ Error al descargar la imagen.")

    if download_image(v_prompt, temp_output):
        # COPIA DE SEGURIDAD INMEDIATA
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_path = os.path.join(HISTORY_DIR, f"{timestamp}_{modo}.png")
        import shutil
        shutil.copy(temp_output, history_path)
        print(f"✅ Imagen guardada en temporal y en histórico: {history_path}")

if __name__ == "__main__":
    main()