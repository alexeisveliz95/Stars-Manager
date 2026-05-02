import sys
import tweepy
import os

def post_content(file_name):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # Ahora la ruta depende del argumento que le pasemos
    TWEET_FILE = os.path.join(BASE_DIR, file_name)

    if not os.path.exists(TWEET_FILE):
        print(f"ℹ️ No hay contenido para {file_name}. Saltando...")
        return

    client = tweepy.Client(
        consumer_key=os.getenv("X_API_KEY"),
        consumer_secret=os.getenv("X_API_SECRET"),
        access_token=os.getenv("X_ACCESS_TOKEN"),
        access_token_secret=os.getenv("X_ACCESS_TOKEN_SECRET")
    )

    try:
        # 2. Intentar abrir el archivo con la ruta absoluta corregida
        if not os.path.exists(TWEET_FILE):
            print(f"❌ No se encontró el archivo de contenido en: {TWEET_FILE}")
            return

        with open(TWEET_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        # Dividimos el contenido por el delimitador ---[cite: 4]
        parts = [p.strip() for p in content.split("---") if p.strip()]
        
        if not parts:
            print("⚠️ El archivo está vacío.")
            return

        if len(parts) < 2:
            print("⚠️ Formato simple detectado. Publicando post único.")
            client.create_tweet(text=parts[0])
        else:
            # 1. Publicar el Post Principal (Gancho)[cite: 1, 4]
            first_tweet = client.create_tweet(text=parts[0])
            first_id = first_tweet.data['id']
            print(f"✅ Post 1 (Gancho) publicado: {first_id}")

            # 2. Publicar la Respuesta (Link y Valor)[cite: 1, 4]
            client.create_tweet(
                text=parts[1],
                in_reply_to_tweet_id=first_id
            )
            print("✅ Post 2 (Hilo con link) publicado.")

            print(f"✅ Publicación de {file_name} completada con éxito.")

        # 3. Limpieza: Borrar el archivo tras publicar con éxito para no repetir
        os.remove(TWEET_FILE) 

    except Exception as e:
        print(f"❌ Error al publicar {file_name}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("❌ Uso: python twitter_bot.py <nombre_archivo.txt>")
        sys.exit(1)

    file_name = sys.argv[1]
    post_content(file_name)