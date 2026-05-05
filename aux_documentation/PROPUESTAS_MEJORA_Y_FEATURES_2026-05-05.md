# Propuestas de mejora y nuevas features (2026-05-05)

## 1) Mejoras prioritarias (impacto alto / esfuerzo medio)

### 1.1 Robustez del scraping y calidad de datos
- **Problema:** `get_trending_repos()` alimenta todo el pipeline; si falla o entrega datos vacíos, se frena el contenido.
- **Mejora:**
  - Agregar reintentos con backoff exponencial en scrapers (GitHub Trending, HN, Reddit, RSS).
  - Añadir validación de esquema por repo (campos obligatorios: `name`, `url`, `description`, `stars`, `growth`).
  - Introducir fallback de fuente secundaria cuando Trending falle.
- **Resultado esperado:** menos ejecuciones fallidas y menor riesgo de pool vacío.

### 1.2 Observabilidad y alertas reales
- **Problema:** hay logging, pero no panel unificado de salud del sistema.
- **Mejora:**
  - Registrar métricas por run en `data/metrics_history.json` (repos scrapeados, repos válidos, tiempo total, tweets publicados, errores por módulo).
  - Publicar resumen diario en `DASHBOARD.md` y opcionalmente en Telegram.
  - Definir umbrales (p.ej. `valid_repos < 10` = warning).
- **Resultado esperado:** detectar degradaciones antes de que afecten la publicación.

### 1.3 Calidad editorial controlada
- **Problema:** el estilo del writer puede variar entre runs.
- **Mejora:**
  - Añadir una etapa de **lint de copy** previa a publicar (longitud, CTA, tono, presencia de enlace, ausencia de claims dudosos).
  - Incluir score de calidad por post y gate mínimo para publicar.
- **Resultado esperado:** consistencia de marca y mejor rendimiento en engagement.

### 1.4 Dedupe inteligente de repos y temas
- **Problema:** se puede repetir tema/repositorio en ventanas cortas.
- **Mejora:**
  - Persistir embeddings ligeros o huellas por tópico para bloquear publicaciones demasiado parecidas.
  - Implementar “cooldown” por repo y por categoría.
- **Resultado esperado:** timeline más variado y menos fatiga de audiencia.

---

## 2) Nuevas features recomendadas

### 2.1 Feature: **Autopilot de A/B testing de formatos**
- Publicar variantes de hook/cierre para Single/List/Thread.
- Medir métricas por variante (CTR, likes, repost ratio, replies).
- Ajustar automáticamente plantillas ganadoras semanalmente.
- **Valor:** optimización continua del rendimiento sin intervención manual.

### 2.2 Feature: **Selector de repos por “oportunidad de conversación”**
- Además de `rank_score`, crear `conversation_score` con señales:
  - crecimiento reciente,
  - tamaño de comunidad,
  - controversia/tema caliente,
  - proximidad a tendencias de X.
- **Valor:** elegir no solo repos “buenos”, sino “posteables” para generar interacción.

### 2.3 Feature: **reply_agent en modo seguro (semi-autónomo)**
- Responder comentarios con plantillas verificadas y límites por hora.
- Modo “human-in-the-loop” opcional para cuentas nuevas.
- Lista de temas prohibidos y bloqueo de prompts inseguros.
- **Valor:** mejora community management sin comprometer reputación.

### 2.4 Feature: **Dashboard analítico temporal**
- Serie temporal por formato, categoría y hora de publicación.
- KPIs: impresiones, engagement rate, CTR, replies/post, follows/post.
- Recomendaciones automáticas de “mejor hora y mejor formato”.
- **Valor:** decisiones editoriales basadas en datos.

### 2.5 Feature: **Scout Agent por nicho/lenguaje**
- Explorar “hidden gems” por tags/lenguajes (Rust, Go, AI tooling, security).
- Cuota semanal dedicada a descubrimiento.
- **Valor:** diferenciación de contenido frente a cuentas que solo repiten Trending.

### 2.6 Feature: **Generación de carruseles/mini-hilos reutilizables**
- A partir del mismo dataset generar:
  - post para X,
  - markdown extendido,
  - guion corto para newsletter.
- **Valor:** estrategia multiformato con costo marginal bajo.

---

## 3) Quick wins (1–3 días)

1. Añadir validaciones de esquema en salida de scrapers.
2. Añadir cooldown simple por repo en `history.json`.
3. Crear comando de “preflight check” antes de publicar (`env + pool + API status`).
4. Escribir tests unitarios para scoring y clasificación.
5. Versionar prompts del writer/image agent para trazabilidad.

---

## 4) Plan sugerido por fases

### Fase 1 (semana 1)
- Robustez scraping + preflight + cooldown básico.

### Fase 2 (semanas 2–3)
- A/B testing + dashboard de métricas + quality gate.

### Fase 3 (semanas 4–6)
- reply_agent seguro + scout_agent + conversation_score.

---

## 5) Riesgos y mitigación
- **Riesgo:** sobre-automatizar respuestas públicas.
  - **Mitigación:** límites por hora, allowlist de temas, modo revisión manual.
- **Riesgo:** costos de APIs por features analíticas.
  - **Mitigación:** almacenamiento incremental local + agregaciones diarias.
- **Riesgo:** sesgo a métricas vanity.
  - **Mitigación:** priorizar KPIs de negocio (CTR/follows) sobre likes.

---

## 6) KPIs para validar mejoras
- % runs exitosas del pipeline.
- Tiempo medio de ejecución.
- % posts publicados sin intervención manual.
- Engagement rate por formato.
- CTR medio y follows por post.
- Diversidad temática semanal (entropía por categoría).
