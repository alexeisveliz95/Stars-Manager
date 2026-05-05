# Stars Manager Project

Stars-Manager/
├── src/
│   ├── agents/
│   │   ├── writer_agent.py       # Tweet generation (Groq/LLaMA)
│   │   ├── image_agent.py        # Image prompt + Flux generation
│   │   ├── reply_agent.py        # (planned) Auto-reply engine
│   │   ├── twitter_trends.py     # (planned) X trends monitor
│   │   └── scout_agent.py        # (planned) Gem hunter by language
│   ├── processors/
│   │   ├── classifier.py         # Category + score engine
│   │   └── markdown_gen.py       # Obsidian-ready report generator
│   ├── scrapers/
│   │   ├──hn_scraper.py
│   │   ├──reddit_scraper.py
│   │   ├──rss_scraper.py
│   │   ├── trending.py           # GitHub Trending HTML scraper
│   │   └── github_api.py         # GitHub REST API client
│   ├── social/
│   │   ├──telegram.py
│   │   ├──whatsapp.py
│   │   └── twitter_bot.py        # Tweepy v2 publisher
│   ├── config.py                 # Categories DB + environment
│   ├── models.py                 # Pydantic data models
│   └── main.py                   # Orchestrator
├── data/
│   ├──history_images
│   ├── top_repo_list.json        # Active repo pool (top 20)
│   └── history.json              # Published repos log
├── Categorias/                   # Per-category Markdown files
├── Tendencias/                   # Daily trending reports
├── DASHBOARD.md                  # Main index (Obsidian entry point)
└── .github/workflows/            # CI/CD automation