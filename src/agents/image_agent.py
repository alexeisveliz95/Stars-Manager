import os
import sys
import shutil
from datetime import datetime
from groq import Groq
from huggingface_hub import InferenceClient

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def generate_visual_prompt(tweet_content):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    # Diccionario de estilos para dar variedad manteniendo la identidad visual
    estilos_visuales = {
        "technical_schematic": "2D minimalist technical schematic, precise nodes and pathways.",
        "blueprint_logic": "Industrial blueprint style, technical drafting lines, engineering grid.",
        "cyber_network": "Cybernetic network diagram, glowing electric cyan connections, high-tech matrix.",
        "data_flow": "Abstract data flow architecture, streamlined vector paths, symmetrical logic gates."
    }

    system_prompt = (
        "You are a master of technical drafting and minimalist digital art. "
        f"Based on the tweet content, choose the most fitting style from: {list(estilos_visuales.keys())}. "
        "\nSTRICT VISUAL GUIDELINES: "
        "- Background: Solid Deep Navy Blue (#000814). "
        "- Graphics: Precise, ultra-thin white and electric cyan lines. "
        "- Subject: A symmetrical, clean diagram of nodes, data pathways, or circuit logic.[cite: 2] "
        "- Aesthetic: High-end software architecture, professional, sharp edges, no blur, no 3D.[cite: 2] "
        "\nINSTRUCTIONS: "
        "1. Start with the chosen style description. "
        "2. Translate the tweet's core concept into a visual technical metaphor. "
        "3. Add: 'flat vector style, sharp lines, isometric but no perspective distortion, white and cyan on dark navy'.[cite: 2] "
        "4. NO text, NO people, NO realistic lighting, NO shadows, NO gradients.[cite: 2]"
    )
    
    response = client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Tweet: {tweet_content}"}
        ]
    )
    
    # Limpiamos y reforzamos el prompt final para evitar que FLUX se desvíe
    v_prompt = response.choices[0].message.content.strip()
    v_prompt += ", minimalist 2D flat vector, no shadows, no 3D, solid background" 
    return v_prompt

def download_hf_image(visual_prompt, modo):
    try:
        token = os.environ.get("HF_TOKEN")[cite: 2]
        if not token:
            print("❌ ERROR: La variable HF_TOKEN no está configurada.")[cite: 2]
            return False

        client = InferenceClient(api_key=token.strip())[cite: 2]

        print(f"📡 Generando imagen con FLUX vía InferenceClient...")[cite: 2]
        
        # Generación directa con el modelo optimizado
        image = client.text_to_image(
            visual_prompt,
            model="black-forest-labs/FLUX.1-schnell"[cite: 2]
        )

        # Rutas de guardado consistentes con tu estructura[cite: 2]
        temp_output = os.path.join(BASE_DIR, f"image_{modo}.png")
        history_dir = os.path.join(BASE_DIR, "data", "history_images")
        os.makedirs(history_dir, exist_ok=True)

        image.save(temp_output)[cite: 2]
        
        # Historial con timestamp[cite: 2]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_path = os.path.join(history_dir, f"{timestamp}_{modo}.png")
        shutil.copy2(temp_output, history_path)
        
        print(f"✅ Imagen guardada exitosamente en: {history_path}")
        return True

    except Exception as e:
        print(f"❌ Error con el cliente de Hugging Face: {e}")[cite: 2]
        return False

def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else "single"[cite: 2]
    input_file = os.path.join(BASE_DIR, f"tweet_{modo}.txt")[cite: 2]

    if not os.path.exists(input_file): return

    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    v_prompt = generate_visual_prompt(content)
    print(f"🎨 Prompt dinámico generado: {v_prompt}")
    download_hf_image(v_prompt, modo)

if __name__ == "__main__":
    main()