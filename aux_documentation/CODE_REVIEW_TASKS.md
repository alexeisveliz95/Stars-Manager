# Revisión rápida: problemas detectados y tareas propuestas

Fecha: 2026-05-04

## 1) Tarea (error tipográfico)
**Título:** Corregir typo en el nombre del workflow `post_dialy.yml`.

- **Problema detectado:** En el README se hace referencia al workflow `post_dialy.yml` ("dialy"), que aparenta ser un typo de `post_daily.yml`.
- **Impacto:** Confusión para mantenimiento, documentación inconsistente y potencial error si se copia/pega el nombre al crear o renombrar workflows.
- **Propuesta:**
  1. Verificar el nombre real en `.github/workflows/`.
  2. Unificar en README, badges y cualquier referencia interna al nombre correcto.
  3. Si se decide renombrar el archivo real, actualizar también referencias en Actions y documentación.

## 2) Tarea (solución de fallo)
**Título:** Arreglar ruta incorrecta del Twitter Bot en `news_orquestador.py`.

- **Problema detectado:** El orquestador construye la ruta `src/utils/twitter_bot.py`, pero el archivo existente está en `src/social/twitter_bot.py`.
- **Impacto:** Fallo en runtime cuando intenta ejecutar el subproceso de publicación en X.
- **Propuesta:**
  1. Cambiar `os.path.join(BASE_DIR, "src", "utils", "twitter_bot.py")` por `os.path.join(BASE_DIR, "src", "social", "twitter_bot.py")`.
  2. Añadir una validación previa de existencia de script para emitir error claro (`FileNotFoundError`) antes de ejecutar `subprocess.run`.
  3. Cubrir el caso con prueba unitaria (ver tarea 4).

## 3) Tarea (comentario/documentación)
**Título:** Actualizar comentarios desfasados sobre scripts "_3.py".

- **Problema detectado:** Hay comentarios que mencionan `image_agent_3.py` y `twitter_bot_3.py`, pero actualmente se invocan `image_agent.py` y `twitter_bot.py`.
- **Impacto:** Deuda de documentación en código, onboarding más lento y riesgo de errores al refactorizar.
- **Propuesta:**
  1. Reescribir comentarios para que describan el flujo real actual.
  2. Evitar referencias a nombres legacy en comentarios si ya no existen en repo.
  3. Añadir una nota breve en README/changelog si hubo migración de nombres.

## 4) Tarea (mejora de prueba)
**Título:** Añadir pruebas para validación de rutas y ejecución de subprocesos del orquestador.

- **Problema detectado:** No hay cobertura visible para el flujo de `ejecutar_noticias()` ante rutas inválidas y fallos de subprocess.
- **Impacto:** Errores de integración se detectan tarde (en ejecución real o CI tardío).
- **Propuesta:**
  1. Crear tests (por ejemplo con `pytest` + `monkeypatch`) que mockeen `subprocess.run`.
  2. Verificar que se construyen rutas correctas a `image_agent.py` y `social/twitter_bot.py`.
  3. Verificar comportamiento cuando `fetch_news()` devuelve `None` y cuando lanza excepciones.
  4. Verificar que ante error en Image Agent el flujo continúe con publicación solo texto.
