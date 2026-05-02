import os
import sys
import requests
import urllib.parse
from groq import Groq

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def generate_visual_prompt(tweet_content):
    """Convierte el tweet en un prompt artístico para la IA de imagen"""
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    system_prompt = (
        "Eres un diseñador gráfico conceptual. Tu tarea es resumir un tweet técnico en un prompt de imagen. "
        "Estilo: 3D render, tech, minimalista, colores neón suaves sobre fondo oscuro, alta resolución. "
        "REGLA: El prompt debe estar en INGLÉS y no debe pedir texto ni letras dentro de la imagen."
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

if __name__ == "__main__":
    main()