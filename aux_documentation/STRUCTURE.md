# Stars Manager — Project Structure

```
Stars-Manager/
├── src/
│   ├── agents/
│   │   ├── writer_agent.py         # Tweet generation via Groq/LLaMA (3 formats: single, list, thread)
│   │   ├── image_agent.py          # Visual prompt builder + Flux.1-schnell image generation
│   │   ├── news_orquestador.py     # News pipeline orchestrator (HN + Reddit + RSS → X)
│   │   ├── scout_agent.py          # Gem hunter: finds hidden repos by language via GitHub API
│   │   ├── reply_agent.py          # (planned) Auto-reply engine
│   │   └── twitter_trends.py       # (planned) X trends monitor
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── classifier.py           # Category + momentum score engine (word-boundary matching)
│   │   └── markdown_gen.py         # Obsidian-ready report generator (Dashboard + Categorias + Tendencias)
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── trending.py             # GitHub Trending HTML scraper (top 25 repos)
│   │   ├── github_api.py           # GitHub REST API client (starred repos, paginated)
│   │   ├── hn_scraper.py           # Hacker News top stories scraper
│   │   ├── reddit_scraper.py       # Reddit top posts scraper (tech subreddits)
│   │   └── rss_scraper.py          # RSS feed scraper (TechCrunch, The Verge, Wired)
│   ├── social/
│   │   ├── __init__.py
│   │   └── twitter_bot.py          # Tweepy v2 publisher (text + image, thread support)
│   ├── utils/
│   │   ├── __init__.py
│   │   └── clean_history.py        # Purges oldest images from data/history_images/ (keeps last 30)
│   ├── webpage/
│   │   ├── index.html              # Stars Manager web dashboard (KPIs + growth chart)
│   │   ├── script.js               # Dashboard data loader (Chart.js, fetches JSON)
│   │   └── style.css               # Dashboard styles
│   ├── models.py                   # Pydantic data models (Repo)
│   └── main.py                     # Main orchestrator: sync stars + trending + export JSON
├── config/
│   ├── categories.py               # CATEGORIES_DB + ALL_KEYWORDS
│   └── settings.py                 # environment-backed application settings
├── data/
│   ├── history_images/             # Archived post images (timestamped .png files)
│   ├── top_repo_list.json          # Active repo pool (top 20 by momentum score)
│   ├── history.json                # Published repos log (deduplication guard)
│   └── news_history.json           # Published news IDs log (HN + Reddit deduplication)
├── Categorias/                     # Per-category Markdown files (Obsidian + GitHub)
├── Tendencias/                     # Daily trending reports (Obsidian + GitHub)
├── DASHBOARD.md                    # Main index: category summary + trending history
├── .github/
│   └── workflows/
│       ├── stars_sync.yml          # Weekly: sync stars + generate all Markdown reports
│       ├── post_dialy.yml          # Mon–Thu 10:00 UTC: single repo spotlight post
│       ├── post_list.yml           # Fri 17:00 UTC: top repos roundup post
│       ├── post_thread.yml         # Tue 15:00 UTC: deep dive two-tweet thread
│       ├── news_bot.yml            # Every 6h: news scrape + generate + post to X
│       └── weekly_cleanup.yml      # Sun 00:00 UTC: purge old images from history
├── requirements.txt
├── .gitignore
├── LICENSE
├── CHANGELOG.md
├── STRUCTURE.md
└── README.md
```