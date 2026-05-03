import os
from scripts.news_scraper import NewsScraper
from agents.writer_agent import WriterAgent
from agents.image_agent import ImageAgent
from twitter_bot import post_to_twitter # La función que ya usas para publicar

def main():
    # 1. ¿Hay noticias?
    scraper = NewsScraper()
    news = scraper.fetch_trending_news()
    
    if not news:
        print("📭 Hoy no hay noticias interesantes.")
        return

    # 2. Si hay, que el escritor redacte
    writer = WriterAgent()
    tweet_text = writer.compose_news_tweet(news)

    # 3. Que el artista genere la imagen
    artist = ImageAgent()
    image_path = artist.generate_for_news(news['title'])

    # 4. Al Twitter!
    post_to_twitter(tweet_text, image_path)
    print("🚀 ¡Noticia publicada!")

if __name__ == "__main__":
    main()