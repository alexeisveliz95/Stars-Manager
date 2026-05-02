import tweepy
import os

def post_thread():
    client = tweepy.Client(
        consumer_key=os.getenv("X_API_KEY"),
        consumer_secret=os.getenv("X_API_SECRET"),
        access_token=os.getenv("X_ACCESS_TOKEN"),
        access_token_secret=os.getenv("X_ACCESS_TOKEN_SECRET")
    )

    try:
        with open("tweet_ready.txt", "r", encoding="utf-8") as f:
            content = f.read()

        # Dividimos el contenido por el delimitador ---
        parts = [p.strip() for p in content.split("---") if p.strip()]
        
        if len(parts) < 2:
            print("⚠️ El formato del tweet no tiene hilos. Publicando post único.")
            client.create_tweet(text=parts[0])
            return

        # 1. Publicar el Post Principal (Gancho)
        first_tweet = client.create_tweet(text=parts[0])
        first_id = first_tweet.data['id']
        print(f"✅ Post 1 publicado: {first_id}")

        # 2. Publicar la Respuesta (Link)
        client.create_tweet(
            text=parts[1],
            in_reply_to_tweet_id=first_id
        )
        print("✅ Post 2 (Hilo con link) publicado.")

    except Exception as e:
        print(f"❌ Error al crear el hilo: {e}")

if __name__ == "__main__":
    post_thread()