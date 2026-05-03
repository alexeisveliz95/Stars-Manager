import os
import sys
import shutil
from datetime import datetime
from groq import Groq
from huggingface_hub import InferenceClient

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ESTILOS_VISUALES = {
    "technical_schematic": (
        "2D technical schematic, precise circuit nodes, data pathway grid, connection ports",
        ["api", "system", "architecture", "pipeline", "microservice", "backend", "code", "function"]
    ),
    "blueprint_logic": (
        "engineering blueprint, technical drafting grid, annotation marks, cyanotype drafting",
        ["algorithm", "pattern", "design", "structure", "layer", "logic", "build", "framework"]
    ),
    "cyber_network": (
        "cybernetic network topology, interconnected glowing nodes, matrix data streams, neural mesh",
        ["ai", "neural", "llm", "security", "crypto", "decentralized", "web3", "model", "agent"]
    ),
    "data_flow": (
        "abstract data flow diagram, logic gate array, symmetrical binary stream, ETL pipeline",
        ["data", "database", "analytics", "stream", "processing", "etl", "sql", "storage"]
    ),
    "wave_signal": (
        "oscilloscope waveform traces, frequency domain visualization, sine and square waves",
        ["signal", "frequency", "protocol", "communication", "bandwidth", "audio", "modulation"]
    ),
    "topology_map": (
        "distributed system graph, geometric mesh topology, cluster node diagram, lattice",
        ["distributed", "graph", "cluster", "mesh", "network", "kubernetes", "devops", "infra",
         "trending", "ranking", "stars", "growth", "repo", "github", "language", "tool"]
    ),
    "market_flow": (
        "financial market flow diagram, candlestick pattern grid, trading signal nodes, price action pathway",
        ["finance", "trading", "market", "crypto", "price", "chart", "portfolio", "investment",
         "token", "defi", "yield", "volatility"]
    ),
    "knowledge_graph": (
        "knowledge graph network, bidirectional semantic links, concept node clusters, hierarchical information lattice",
        ["knowledge", "obsidian", "pkm", "notes", "zettelkasten", "learning", "concept",
         "research", "insight", "summary", "categorize", "organize"]
    ),
}

VISUAL_IDENTITY = (
    "deep navy blue obsidian background, Frosted glass textures,"
    "volumetric lighting, subtle bloom effect, high-end digital render, "
    "Fibonacci spiral arrangement, clean composition, "
    "FHD resolution, 16:9 aspect ratio, professional and elegant"
)

METAPHOR_EXAMPLES = """
METAPHOR EXAMPLES by story type — use these as templates:
- "X surpassed Y in stars/growth"   → two node clusters, one denser overtaking the other, directional edge flow
- "X grew fast / is trending"       → single central node with high-frequency radial connections exploding outward
- "X connects A and B"              → two distinct node groups with a single bridge pathway between them
- "Top N tools / repos / languages" → N parallel vertical columns of equal height, distinct node signatures per column
- "X vs Y comparison"               → symmetric split diagram, two mirrored architectures side by side
- "New release / launch"            → starburst emission pattern from central node, concentric ripple rings
- "Weekly/monthly report"           → timeline axis with milestone nodes, data density increasing toward present
- "How X works internally"          → layered horizontal architecture, internal zones, flow arrows between layers
- "Security / vulnerability"        → enclosed perimeter nodes, breach point highlighted, containment pathway
- "AI / LLM topic"                  → attention web, token nodes with weighted connection lines, transformer stack silhouette
"""

def build_selector_prompt() -> str:
    estilos_block = "\n".join(
        f'  "{key}": "{desc}"\n    keywords: {", ".join(kw)}'
        for key, (desc, kw) in ESTILOS_VISUALES.items()
    )
    return f"""You are a technical art director creating images for a GitHub trends and open source content account on X (Twitter).

AVAILABLE STYLES:
{estilos_block}

YOUR PROCESS:
1. Extract the CORE STORY from the tweet: what is growing, competing, connecting, failing, launching, ranking?
2. Pick the style whose keywords best match the topic.
3. Build a CONCRETE visual metaphor — specify shapes, their quantity, spatial arrangement,
   and how they relate to each other. The metaphor must reflect the tweet's story, not just its topic.

{METAPHOR_EXAMPLES}

OUTPUT RULES:
- Single dense line of comma-separated descriptors
- 40 to 70 words maximum
- Start directly with the chosen style description
- No preamble, no explanation, no quotes, no sentences
- Never mention the tweet text literally in the prompt"""


def generate_visual_prompt(tweet_content: str) -> str:
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.4,
        max_tokens=120,
        messages=[
            {"role": "system", "content": build_selector_prompt()},
            {"role": "user", "content": f"Tweet: {tweet_content}"},
        ],
    )

    raw = response.choices[0].message.content.strip()

    # Limpieza defensiva
    raw = raw.strip('"').strip("'")
    if raw.lower().startswith("prompt:"):
        raw = raw[7:].strip()

    final_prompt = f"{raw}, {VISUAL_IDENTITY}"
    return final_prompt


def download_hf_image(visual_prompt: str, modo: str) -> bool:
    try:
        token = os.environ.get("HF_TOKEN")
        if not token:
            print("❌ ERROR: HF_TOKEN no configurado.")
            return False

        client = InferenceClient(api_key=token.strip())
        print("📡 Generando imagen con FLUX.1-schnell...")

        image = client.text_to_image(
            visual_prompt,
            model="black-forest-labs/FLUX.1-schnell",
            width=1344,
            height=768,
        )

        temp_output = os.path.join(BASE_DIR, f"image_{modo}.png")
        history_dir = os.path.join(BASE_DIR, "data", "history_images")
        os.makedirs(history_dir, exist_ok=True)

        image.save(temp_output)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_path = os.path.join(history_dir, f"{timestamp}_{modo}.png")
        shutil.copy2(temp_output, history_path)

        print(f"✅ Imagen guardada: {history_path}")
        return True

    except Exception as e:
        print(f"❌ Error con HuggingFace: {e}")
        return False


def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else "single"
    input_file = os.path.join(BASE_DIR, f"tweet_{modo}.txt")

    if not os.path.exists(input_file):
        print(f"❌ No se encontró {input_file}")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if not content:
        print("❌ El archivo de tweet está vacío.")
        return

    v_prompt = generate_visual_prompt(content)

    # Log de auditoría — muestra qué estilo eligió el LLM para cada tweet
    style_detected = next(
        (key for key in ESTILOS_VISUALES if key in v_prompt), "unknown"
    )
    print(f"🎯 Estilo detectado: {style_detected}")
    print(f"🎨 Prompt generado ({len(v_prompt.split())} palabras):\n{v_prompt}\n")

    download_hf_image(v_prompt, modo)


if __name__ == "__main__":
    main()
