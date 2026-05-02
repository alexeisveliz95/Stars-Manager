import os
import sys
import shutil
from datetime import datetime
from groq import Groq
from huggingface_hub import InferenceClient

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def generate_visual_prompt(tweet_content):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    system_prompt = (
        "You are a master of technical drafting and minimalist digital art. "
        "Create a prompt for a 2D flat vector-style technical schematic. "
        "\nSTRICT VISUAL GUIDELINES: "
        "- Background: Solid Deep Navy Blue (#000814). "
        "- Graphics: Precise, ultra-thin white and electric cyan lines. "
        "- Subject: A symmetrical, clean diagram of nodes, data pathways, or circuit logic. "
        "- Aesthetic: High-end software architecture, professional, sharp edges, no blur, no 3D. "
        "\nINSTRUCTIONS: "
        "1. Start with: 'A 2D minimalist technical schematic of...' "
        "2. Add: 'flat vector style, sharp lines, isometric but no perspective distortion, engineering grid'. "
        "3. NO text, NO people, NO realistic lighting, NO shadows."
    )
    
    response = client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Translate this tweet into a technical diagram concept: {tweet_content}"}
        ]
    )
    return response.choices[0].message.content.strip()


# Definimos el cliente fuera o dentro de la función
def download_hf_image(visual_prompt, modo):
    try:
        token = os.environ.get("HF_TOKEN")
        if not token:
            print("❌ ERROR: La variable HF_TOKEN no está configurada en el entorno.")
            return False

        client = InferenceClient(api_key=token.strip())

        print(f"📡 Generando imagen con FLUX vía InferenceClient...")
        
        # El método text_to_image devuelve un objeto PIL Image
        # Usamos FLUX.1-schnell que es gratuito y rápido para la API
        image = client.text_to_image(
            visual_prompt,
            model="black-forest-labs/FLUX.1-schnell"
        )

        # Rutas de guardado
        temp_output = os.path.join(BASE_DIR, f"image_{modo}.png")
        history_dir = os.path.join(BASE_DIR, "data", "history_images")
        os.makedirs(history_dir, exist_ok=True)

        # Guardar la imagen usando el método de PIL
        image.save(temp_output)
        
        # Copiar al historial
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_path = os.path.join(history_dir, f"{timestamp}_{modo}.png")
        shutil.copy2(temp_output, history_path)
        
        print(f"✅ Imagen guardada exitosamente.")
        return True

    except Exception as e:
        print(f"❌ Error con el cliente de Hugging Face: {e}")
        return False

def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else "single"
    input_file = os.path.join(BASE_DIR, f"tweet_{modo}.txt")

    if not os.path.exists(input_file): return

    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    v_prompt = generate_visual_prompt(content)
    print(f"🎨 Prompt técnico: {v_prompt}")
    download_hf_image(v_prompt, modo)

if __name__ == "__main__":
    main()