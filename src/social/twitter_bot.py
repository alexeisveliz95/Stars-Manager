import sys
import tweepy
import os
import shutil
from datetime import datetime

def post_content(file_name):
    # 1. Configuración de rutas
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR = os.path.join(BASE_DIR, "data", "history_images")
    TWEET_FILE = os.path.join(BASE_DIR, file_name)
    
    # Asegurarnos de que la carpeta de histórico exista
    os.makedirs(DATA_DIR, exist_ok=True)
    
    image_name = file_name.replace("tweet_", "image_").replace(".txt", ".png")
    IMAGE_FILE = os.path.join(BASE_DIR, image_name)

    if not os.path.exists(TWEET_FILE):
        print(f"ℹ️ No hay contenido para {file_name}. Saltando...")
        return

    # 2. Autenticación (v1.1 y v2)
    api_key = os.getenv("X_API_KEY")
    api_secret = os.getenv("X_API_SECRET")
    access_token = os.getenv("X_ACCESS_TOKEN")
    access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")

    auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
    api_v1 = tweepy.API(auth)
    client_v2 = tweepy.Client(api_key, api_secret, access_token, access_token_secret)

    try:
        # 3. Subir Imagen
        media_id = None
        if os.path.exists(IMAGE_FILE):
            print(f"📸 Subiendo imagen: {image_name}")
            media = api_v1.media_upload(filename=IMAGE_FILE)
            media_id = media.media_id_string
        
        # 4. Leer y Publicar Texto
        with open(TWEET_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        parts = [p.strip() for p in content.split("---") if p.strip()]
        media_ids = [media_id] if media_id else None

        if len(parts) < 2:
            client_v2.create_tweet(text=parts[0], media_ids=media_ids)
        else:
            first_tweet = client_v2.create_tweet(text=parts[0], media_ids=media_ids)
            client_v2.create_tweet(text=parts[1], in_reply_to_tweet_id=first_tweet.data['id'])

        print(f"✅ Publicación de {file_name} exitosa.")

        # 5. ARCHIVADO DE IMAGEN (Datetime)
        if os.path.exists(IMAGE_FILE):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_image_name = f"{timestamp}_{image_name}"
            archive_path = os.path.join(DATA_DIR, new_image_name)
            
            # Movemos la imagen a la carpeta data/history_images
            shutil.move(IMAGE_FILE, archive_path)
            print(f"📁 Imagen archivada en: data/history_images/{new_image_name}")

        # Limpiar el archivo de texto
        os.remove(TWEET_FILE)

    except Exception as e:
        print(f"❌ Error al publicar: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    post_content(sys.argv[1])