# Análisis técnico de mejoras y problemas a resolver (2026-05-05)

## Resumen ejecutivo

Se revisó la base de código para detectar inconsistencias, deuda técnica y riesgos operativos. El principal problema encontrado es una **regresión de integración**: aún existen referencias a `twitter_bot.py` aunque el flujo fue migrado a `post_runner.py` + `twitter_publisher.py`.

---

## Hallazgos prioritarios

### 1) Regresión crítica: referencias a `twitter_bot.py` inexistente

**Impacto:** Alto. El flujo `news_orquestador` puede fallar en producción con `FileNotFoundError` y no publicar contenido.

- `news_orquestador.py` intenta ejecutar `src/social/twitter_bot.py`.
- Ese archivo ya no existe en `src/social/`.
- La propia documentación interna en `post_runner.py` indica que reemplaza a `twitter_bot.py`.

**Evidencia:**
- `src/agents/news_orquestador.py` (líneas donde arma y valida ruta de `twitter_bot.py`).
- `src/social/post_runner.py` (documenta que sustituye a `twitter_bot.py`).
- Árbol actual de `src/social/` sin `twitter_bot.py`.

**Recomendación:**
- Cambiar `news_orquestador.py` para ejecutar `python src/social/post_runner.py single twitter`.
- Evitar nombres de archivo “hardcodeados” obsoletos; centralizar comandos en una constante compartida.

---

### 2) Documentación desalineada con el código actual

**Impacto:** Medio-Alto. Confunde onboarding y operación.

Se detectan múltiples referencias en docs a `src/social/twitter_bot.py`, pero el módulo real es `twitter_publisher.py` y el orquestador es `post_runner.py`.

**Evidencia:**
- `README.md` (tabla de módulos y arquitectura).
- `STRUCTURE.md` (estructura con `twitter_bot.py`).

**Recomendación:**
- Actualizar documentación para reflejar los módulos actuales.
- Añadir una sección “Migraciones internas” para evitar confusión en futuras refactorizaciones.

---

### 3) Falta de validaciones automáticas para detectar rutas obsoletas

**Impacto:** Medio. Problemas similares pueden reaparecer.

**Recomendación:**
- Añadir un check en CI que falle si aparece `twitter_bot.py` en código/documentación crítica.
- Añadir smoke test que valide que los scripts llamados por orquestadores existen.

---

### 4) Riesgo de fallos silenciosos por uso de `print` en vez de logging estructurado

**Impacto:** Medio. Dificulta observabilidad y alertas.

Aunque hay utilidades de monitoreo (`stellar_logger`), partes importantes de ejecución siguen en `print` sin niveles (`info`, `warning`, `error`) ni contexto uniforme.

**Recomendación:**
- Migrar los puntos de salida críticos a logger estructurado.
- Incluir ID de ejecución y plataforma en cada evento.

---

## Quick checks ejecutados

1. **Compilación estática de Python**: `python -m compileall -q src` ✅
2. **Búsqueda de referencias obsoletas**: `rg -n "twitter_bot|TODO|FIXME|NotImplemented" ...` ✅
3. **Inspección de módulos de publicación** (`post_runner`, `twitter_publisher`, `publisher`) ✅

---

## Plan de acción sugerido (ordenado)

1. **Corregir `news_orquestador.py`** para usar `post_runner.py`.
2. **Actualizar README + STRUCTURE** eliminando referencias a `twitter_bot.py`.
3. **Agregar check de CI** contra rutas obsoletas.
4. **Estandarizar logging** en orquestadores y publishers.

---

## Conclusión

El sistema tiene una base sólida, pero mantiene residuos de una migración incompleta. Resolver primero la referencia rota a `twitter_bot.py` reducirá fallos operativos inmediatos y mejorará la estabilidad del pipeline automático.
