# Changelog — Stars Manager

## [v1.0.230] — 2025-05-03

Primera versión estable. Se corrigieron bugs críticos que impedían el funcionamiento
real del sistema en producción, se mejoró la calidad del contenido generado y se
refactorizó el pipeline de imágenes para Flux.

---

### 🐛 Bugs críticos corregidos

#### `src/agents/writer_agent.py`
- **f-strings rotos en los 3 modos de publicación** — Las líneas que incluían
  `{repo['url']}` y `{repo['name']}` en los prompts de `thread`, `list` y `single`
  no tenían el prefijo `f`. El LLM recibía el texto literal `{repo['url']}` y todos
  los tweets publicados contenían `Link: {repo['url']}` en lugar de la URL real.

#### `src/social/twitter_bot.py`
- **`tweepy.Client` con argumentos posicionales en orden incorrecto** — El constructor
  recibe `bearer_token` como primer argumento posicional. El código pasaba `api_key`
  en ese slot, corriendo todas las credenciales un lugar. Tweepy no lanza error al
  construir el cliente — falla silenciosamente al intentar publicar con un 401.
- **Hilo sin guard en el segundo tweet** — Si el primer tweet fallaba,
  `first_tweet.data['id']` lanzaba `TypeError` con un mensaje confuso en lugar del
  error real.

#### `src/scrapers/github_api.py`
- **`r["name"]` en lugar de `r["full_name"]`** — La API de GitHub devuelve el nombre
  corto del repo en `"name"` (`Stars-Manager`) y el identificador completo en
  `"full_name"` (`alexeisveliz95/Stars-Manager`). Todo el sistema usa `owner/repo`
  como identificador. Los links generados en Markdown apuntaban a URLs incorrectas.

#### `src/main.py`
- **Pool sobreescrito con lista vacía si el scraper falla** — Si `get_trending_repos()`
  devolvía `[]` por timeout o error de red, `top_repo_list.json` se sobreescribía con
  una lista vacía, borrando el pool de la semana anterior sin ningún error visible.

---

### ⚠️ Bugs menores corregidos

#### `src/processors/classifier.py`
- **Matching por substring en lugar de word boundary** — `"ml" in "html"` → `True`,
  `"ai" in "email"` → `True`, `"bot" in "robot"` → `True`. Se reemplazó el operador
  `in` por `re.search()` con `\b` (word boundary). Se añadió `_matches_keyword()` como
  función centralizada con `re.escape()` para keywords con caracteres especiales.

#### `src/models.py`
- **`topics: List[str]` sin default** — Repos sin topics lanzaban `ValidationError` al
  construir el objeto `Repo`. Se añadió `Field(default_factory=list)`.
- **`description` sin default** — Repos sin descripción en la API lanzaban error.
  Se añadió `Optional[str] = None`.

#### `src/scrapers/trending.py`
- **`stars` y `growth` guardados como strings** — El scraper devolvía `"2227"` y `"482"`
  como strings. `calculate_score` los convertía internamente con `int()`, pero formatos
  como `"1.2k"` (que GitHub ya usa en mobile) rompían la conversión silenciosamente.
- **Sin validación del tag de estrellas** — Si `stars_tag` no encontraba el selector,
  `stars_str` podía quedar como texto parcial del elemento HTML.
- **HTTP status sin código en el log** — El log de error no mostraba el código recibido,
  imposibilitando distinguir 429 (rate limit) de 503 (GitHub caído).

#### `src/scrapers/github_api.py`
- **Sin timeout en requests** — El loop de paginación podía colgar el workflow de
  Actions indefinidamente.
- **HTTP 403 no diferenciado del resto** — El rate limit de GitHub devuelve 403, no 429.
  Se maneja explícitamente con el header `X-RateLimit-Remaining`.

#### `.github/workflows/stars_sync.yml`
- **`actions/checkout@v3` y `setup-python@v4` desactualizados** — Actualizados a `@v4`
  y `@v5` respectivamente, en línea con el resto de workflows.
- **`git add .` en el commit** — Podía commitear `__pycache__/`, `.pyc`, archivos
  temporales de Flux y cualquier archivo generado en el workspace. Cambiado a
  `git add data/*.json`.

#### `.github/workflows/*.yml` (todos)
- **Sin bloque `permissions: contents: write`** — En repos con configuración estricta,
  el `GITHUB_TOKEN` por defecto es read-only y el `git push` falla silenciosamente.

#### `.github/workflows/post_thread.yml.yml`
- **Doble extensión** — Creado `post_thread.yml` limpio. El archivo con doble extensión
  debe eliminarse manualmente del repo con `git rm`.

---

### ✨ Mejoras

#### `src/agents/image_agent.py` — Refactor completo para Flux
- `ESTILOS_VISUALES` rediseñado como dict de tuplas `(descripción, keywords)`.
  Las descripciones completas ahora llegan al LLM — antes solo se pasaban las keys.
- Criterio de selección de estilo explícito con keywords por categoría temática.
- Sistema de metáforas concretas con 10 plantillas por tipo de historia
  (`"X superó a Y"`, `"top N repos"`, `"nuevo release"`, etc.).
- Output forzado a 40-70 palabras con `max_tokens=120` y `temperature=0.4`.
  Flux.1-schnell rinde mejor con prompts cortos y densos.
- `VISUAL_IDENTITY` como sufijo fijo — identidad visual consistente entre posts.
- Dimensiones corregidas a `1344×768` (16:9) para X. El default del modelo
  era 1024×1024, que X recorta o centra mal en el timeline.
- 6 estilos visuales (antes 4): añadidos `wave_signal` y `topology_map`.
- Log de auditoría: muestra qué estilo eligió el LLM para cada tweet.

#### `src/main.py`
- Pool expandido de **5 a 20 repos** — 5 repos duraba menos de una semana con
  6 posts semanales. 20 repos dan ~3 semanas de margen.

#### `src/scrapers/trending.py`
- Extracción ampliada de **15 a 25 repos** — GitHub siempre muestra exactamente 25
  en trending. Se estaban dejando 10 fuera sin razón.
- `_parse_number()` centraliza todo el parsing numérico: maneja comas, sufijos `k`/`m`
  y devuelve `0` en lugar de explotar ante formatos inesperados.

#### `src/config.py`
- Keywords problemáticos removidos con documentación del motivo:
  `"ml"` (matchea en `"html"`), `"bot"` (matchea en `"robot"`),
  `"api"` (matchea en `"capability"`), `"aws"` (matchea en `"password"`).
- Keywords con guión de PlayStation reemplazados por versiones sin guión,
  más compatibles con `\b` en topics de GitHub.
- Comentario de orden de prioridad de categorías documentado.

#### `src/processors/markdown_gen.py` — Rediseño visual completo
- **Obsidian callouts** (`> [!info]`, `> [!tip]`, `> [!note]`) en todos los archivos
  generados. Renderizan como bloques coloreados en Obsidian; degradan a blockquotes
  limpios en GitHub.
- **Key Insight** al inicio del reporte de tendencias: bloque destacado con el repo #1,
  su crecimiento absoluto y el porcentaje sobre su total de estrellas.
- **DASHBOARD con top 3 inline** — tabla de los 3 repos más calientes del día
  directamente en el dashboard, sin necesidad de abrir el reporte de tendencias.
- **Categorías con estrellas acumuladas** — el resumen de cada categoría muestra
  el total de estrellas de todos sus repos, no solo el top.
- Guard contra secciones duplicadas en `DASHBOARD.md` al hacer append desde
  `save_trends()`.

---

### 📁 Archivos modificados

| Archivo | Tipo de cambio |
| :--- | :--- |
| `src/agents/writer_agent.py` | Bug crítico |
| `src/agents/image_agent.py` | Refactor + mejora |
| `src/social/twitter_bot.py` | Bug crítico + mejora |
| `src/scrapers/github_api.py` | Bug crítico + mejora |
| `src/scrapers/trending.py` | Bug menor + mejora |
| `src/processors/classifier.py` | Bug menor |
| `src/processors/markdown_gen.py` | Mejora visual |
| `src/main.py` | Bug menor + mejora |
| `src/models.py` | Bug menor |
| `src/config.py` | Mejora |
| `.github/workflows/stars_sync.yml` | Bug menor |
| `.github/workflows/post_dialy.yml` | Bug menor |
| `.github/workflows/post_list.yml` | Bug menor |
| `.github/workflows/post_thread.yml` | Creado (reemplaza `.yml.yml`) |

---

### 🗑️ Acción manual requerida

```bash
git rm .github/workflows/post_thread.yml.yml
git commit -m "fix: remove double-extension workflow file"
git push
```

---

## [v0.x.x] — Historial previo

Más de 200 commits de desarrollo iterativo, construcción del pipeline base,
integración de APIs (Groq, HuggingFace, Twitter), scraper de GitHub trending,
sistema de categorización y generación de reportes Markdown.
