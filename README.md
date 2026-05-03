<div align="center">

# ⭐ Stars Manager

### Automated Tech Intelligence · Content Engine · X Growth System

[![Sync Status](https://img.shields.io/github/actions/workflow/status/alexeisveliz95/Stars-Manager/stars_sync.yml?label=Weekly%20Sync&style=for-the-badge&logo=github&logoColor=white)](https://github.com/alexeisveliz95/Stars-Manager/actions)
[![Daily Post](https://img.shields.io/github/actions/workflow/status/alexeisveliz95/Stars-Manager/post_dialy.yml?label=Daily%20Post&style=for-the-badge&logo=x&logoColor=white)](https://github.com/alexeisveliz95/Stars-Manager/actions)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Automated-2671E5?style=for-the-badge&logo=githubactions&logoColor=white)](https://github.com/features/actions)

[![Groq](https://img.shields.io/badge/Groq-LLaMA%203.3-F55036?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com)
[![Flux](https://img.shields.io/badge/Flux-Image%20Gen-000000?style=for-the-badge&logo=huggingface&logoColor=yellow)](https://huggingface.co/black-forest-labs)
[![Tweepy](https://img.shields.io/badge/Tweepy-X%20API%20v2-1DA1F2?style=for-the-badge&logo=x&logoColor=white)](https://tweepy.org)
[![Obsidian](https://img.shields.io/badge/Obsidian-PKM%20Ready-483699?style=for-the-badge&logo=obsidian&logoColor=white)](https://obsidian.md)

[![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-F59E0B?style=for-the-badge)](CHANGELOG.md)
[![Status](https://img.shields.io/badge/Status-Production-22C55E?style=for-the-badge)]()

---

*🇪🇸 [Leer en Español](#-en-español) · 🇬🇧 English below*

</div>

---

## 🧠 What is Stars Manager?

Stars Manager started as a GitHub stars organizer. It evolved into a **full autonomous content engine** that monitors the open source ecosystem, thinks about it, and publishes professional tech content on X — completely on autopilot.

Every week, the system wakes up, scans GitHub Trending, ranks repositories by momentum, writes tweets in three formats, generates technical art images with Flux, and publishes to X. All without human intervention.

---

## ⚡ Pipeline Overview

```
GitHub Trending ──► Scraper ──► Scorer ──► Pool (top 20 repos)
                                                    │
                    ┌───────────────────────────────┘
                    │
                    ▼
           Writer Agent (Groq/LLaMA 3.3)
           Generates tweet in selected format
                    │
                    ▼
           Image Agent (Groq + Flux.1-schnell)
           Generates 1344×768 technical art image
                    │
                    ▼
           Twitter Bot (Tweepy v2)
           Posts to X with image
                    │
                    ▼
           Markdown Generator
           Updates DASHBOARD.md + Categorias/ + Tendencias/
```

---

## 🔧 Core Modules

| Module | File | Purpose |
| :--- | :--- | :--- |
| 🕷️ Trending Scraper | `src/scrapers/trending.py` | Scrapes GitHub Trending (top 25 repos) |
| 🔗 GitHub API | `src/scrapers/github_api.py` | Fetches starred repos via API |
| 🏷️ Classifier | `src/processors/classifier.py` | Categorizes repos using word-boundary matching |
| 📝 Writer Agent | `src/agents/writer_agent.py` | Generates tweets via Groq (3 formats) |
| 🎨 Image Agent | `src/agents/image_agent.py` | Builds Flux prompts + generates images |
| 🐦 Twitter Bot | `src/social/twitter_bot.py` | Posts to X with media via Tweepy v2 |
| 📊 Markdown Gen | `src/processors/markdown_gen.py` | Generates reports for Obsidian + GitHub |

---

## 📣 Content Formats

The system publishes three types of content, each triggered by its own workflow:

| Format | Workflow | Schedule | Description |
| :--- | :--- | :--- | :--- |
| **Single** | `post_dialy.yml` | Mon–Thu · 10:00 UTC | One repo spotlight with context + link |
| **List** | `post_list.yml` | Fri · 17:00 UTC | Top repos roundup, list format |
| **Thread** | `post_thread.yml` | Tue · 15:00 UTC | Deep dive in two connected tweets |

Each post includes a **generated technical art image** (1344×768, 16:9) with a consistent visual identity: deep navy `#000814` background, white and electric cyan `#00F5FF` lines, flat vector style.

---

## 🏗️ Architecture

```
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
│   │   ├── trending.py           # GitHub Trending HTML scraper
│   │   └── github_api.py         # GitHub REST API client
│   ├── social/
│   │   └── twitter_bot.py        # Tweepy v2 publisher
│   ├── config.py                 # Categories DB + environment
│   ├── models.py                 # Pydantic data models
│   └── main.py                   # Orchestrator
├── data/
│   ├── top_repo_list.json        # Active repo pool (top 20)
│   └── history.json              # Published repos log
├── Categorias/                   # Per-category Markdown files
├── Tendencias/                   # Daily trending reports
├── DASHBOARD.md                  # Main index (Obsidian entry point)
└── .github/workflows/            # CI/CD automation
```

---

## 🚀 Setup & Deployment

### 1. Clone & install

```bash
git clone https://github.com/alexeisveliz95/Stars-Manager.git
cd Stars-Manager
pip install -r requirements.txt
```

### 2. Configure GitHub Secrets

Go to **Settings → Secrets and variables → Actions** and add:

| Secret | Description |
| :--- | :--- |
| `STARS_TOKEN` | GitHub Personal Access Token (scope: `read:user`, `public_repo`) |
| `GROQ_API_KEY` | Groq API key — [get one free](https://console.groq.com) |
| `HF_TOKEN` | Hugging Face token — [get one free](https://huggingface.co/settings/tokens) |
| `X_API_KEY` | X Developer App API Key |
| `X_API_SECRET` | X Developer App API Secret |
| `X_ACCESS_TOKEN` | X Access Token (your account) |
| `X_ACCESS_TOKEN_SECRET` | X Access Token Secret |

> [!important]
> Your X app must have **Read and Write** permissions enabled.
> Regenerate your access tokens after changing permissions.

### 3. First run

Trigger the sync manually from the **Actions** tab to populate the repo pool:

```
Actions → 🌟 Stars Sync → Run workflow
```

After that, all other workflows run on their configured schedules automatically.

---

## 📊 Explore the Data

The classified and updated data lives in the main index:

<div align="center">

### 👉 **[GO TO THE DASHBOARD](DASHBOARD.md)** 👈

</div>

---

## 🗺️ Roadmap

- [x] GitHub stars sync + categorization
- [x] GitHub Trending scraper with momentum scoring
- [x] Automated tweet generation (3 formats)
- [x] Flux image generation with consistent visual identity
- [x] Full X publishing pipeline (text + image)
- [x] Obsidian-ready Markdown reports with callouts
- [ ] `reply_agent.py` — auto-reply to comments on posts
- [ ] `twitter_trends.py` — monitor X trends to align content
- [ ] `scout_agent.py` — discover hidden gems by language/topic
- [ ] Analytics dashboard — track impressions per post format

---

## 🛡️ License

MIT — use it, fork it, build on it.

---

<div align="center">
<sub>Built with Python · Powered by Groq, Flux & GitHub Actions · Made in Cuba 🇨🇺</sub>
</div>

---
---

<div align="center">

# 🇪🇸 En Español

### Sistema de Inteligencia Tech · Motor de Contenido · Crecimiento en X

</div>

---

## 🧠 ¿Qué es Stars Manager?

Stars Manager comenzó como un organizador de repos favoritos de GitHub. Evolucionó hasta convertirse en un **motor de contenido completamente autónomo** que monitorea el ecosistema open source, lo analiza, y publica contenido tech profesional en X — en piloto automático.

Cada semana el sistema despierta, escanea GitHub Trending, rankea repositorios por momentum, redacta tweets en tres formatos, genera imágenes de arte técnico con Flux, y publica en X. Todo sin intervención humana.

---

## ⚡ Flujo del Pipeline

```
GitHub Trending ──► Scraper ──► Scorer ──► Pool (top 20 repos)
                                                    │
                    ┌───────────────────────────────┘
                    │
                    ▼
           Writer Agent (Groq/LLaMA 3.3)
           Genera el tweet en el formato seleccionado
                    │
                    ▼
           Image Agent (Groq + Flux.1-schnell)
           Genera imagen técnica 1344×768
                    │
                    ▼
           Twitter Bot (Tweepy v2)
           Publica en X con imagen
                    │
                    ▼
           Markdown Generator
           Actualiza DASHBOARD.md + Categorias/ + Tendencias/
```

---

## 🔧 Módulos principales

| Módulo | Archivo | Función |
| :--- | :--- | :--- |
| 🕷️ Trending Scraper | `src/scrapers/trending.py` | Scraping de GitHub Trending (top 25 repos) |
| 🔗 GitHub API | `src/scrapers/github_api.py` | Repos starred via API REST |
| 🏷️ Clasificador | `src/processors/classifier.py` | Categorización con word-boundary matching |
| 📝 Writer Agent | `src/agents/writer_agent.py` | Tweets via Groq (3 formatos) |
| 🎨 Image Agent | `src/agents/image_agent.py` | Prompts para Flux + generación de imágenes |
| 🐦 Twitter Bot | `src/social/twitter_bot.py` | Publicación en X con media via Tweepy v2 |
| 📊 Markdown Gen | `src/processors/markdown_gen.py` | Reportes para Obsidian + GitHub |

---

## 📣 Formatos de Contenido

El sistema publica tres tipos de contenido, cada uno con su propio workflow:

| Formato | Workflow | Horario | Descripción |
| :--- | :--- | :--- | :--- |
| **Single** | `post_dialy.yml` | Lun–Jue · 10:00 UTC | Spotlight de un repo con contexto + link |
| **List** | `post_list.yml` | Vie · 17:00 UTC | Resumen de top repos en formato lista |
| **Thread** | `post_thread.yml` | Mar · 15:00 UTC | Deep dive en dos tweets enlazados |

Cada post incluye una **imagen de arte técnico generada** (1344×768, 16:9) con identidad visual consistente: fondo navy `#000814`, líneas blancas y cyan eléctrico `#00F5FF`, estilo flat vector.

---

## 🚀 Setup & Despliegue

### 1. Clonar e instalar

```bash
git clone https://github.com/alexeisveliz95/Stars-Manager.git
cd Stars-Manager
pip install -r requirements.txt
```

### 2. Configurar GitHub Secrets

Ve a **Settings → Secrets and variables → Actions** y añade:

| Secret | Descripción |
| :--- | :--- |
| `STARS_TOKEN` | GitHub Personal Access Token (scopes: `read:user`, `public_repo`) |
| `GROQ_API_KEY` | API key de Groq — [obtener gratis](https://console.groq.com) |
| `HF_TOKEN` | Token de Hugging Face — [obtener gratis](https://huggingface.co/settings/tokens) |
| `X_API_KEY` | API Key de tu app en X Developer Portal |
| `X_API_SECRET` | API Secret de tu app en X Developer Portal |
| `X_ACCESS_TOKEN` | Access Token de tu cuenta en X |
| `X_ACCESS_TOKEN_SECRET` | Access Token Secret de tu cuenta en X |

> [!important]
> Tu app de X debe tener permisos **Read and Write** activados.
> Regenera los access tokens después de cambiar los permisos.

### 3. Primera ejecución

Dispara la sincronización manual desde la pestaña **Actions** para poblar el pool:

```
Actions → 🌟 Stars Sync → Run workflow
```

Después de eso, todos los workflows corren en sus horarios configurados automáticamente.

---

## 📊 Explora los Datos

Toda la información clasificada y actualizada vive en el índice principal:

<div align="center">

### 👉 **[IR AL DASHBOARD](DASHBOARD.md)** 👈

</div>

---

## 🗺️ Roadmap

- [x] Sync de repos starred + categorización
- [x] Scraper de GitHub Trending con scoring de momentum
- [x] Generación automatizada de tweets (3 formatos)
- [x] Generación de imágenes con Flux e identidad visual consistente
- [x] Pipeline completo de publicación en X (texto + imagen)
- [x] Reportes Markdown con callouts para Obsidian
- [ ] `reply_agent.py` — respuestas automáticas a comentarios
- [ ] `twitter_trends.py` — monitor de tendencias en X para alinear contenido
- [ ] `scout_agent.py` — descubridor de gems por lenguaje/topic
- [ ] Dashboard de analytics — impresiones por formato de post

---

## 🛡️ Licencia

MIT — úsalo, forkéalo, constrúyelo.

---

<div align="center">
<sub>Construido con Python · Impulsado por Groq, Flux y GitHub Actions · Hecho en Cuba 🇨🇺</sub>
</div>