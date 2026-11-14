# Automatización del Flujo de Datos (GitHub Actions)

Este documento detalla el funcionamiento, operación y mantenimiento del pipeline automatizado de recolección y actualización de datos de **Apocuna**.

---

## 1. Funcionamiento y Frecuencia del Workflow

El flujo principal de portales y RSS está definido en [`.github/workflows/actualizar.yml`](file:///.github/workflows/actualizar.yml).
- **Frecuencia programada:** Se ejecuta automáticamente cada 3 horas mediante cron (`0 */3 * * *`).
- **Runner:** Ejecuta en entorno Linux `ubuntu-24.04`.
- **Mecanismo de preservación:** 
  1. Descarga el histórico previo desde la rama huérfana `data` (directorio `data/generated/`).
  2. Ejecuta diagnóstico de conectividad HTTP contra los portales CKAN.
  3. Ejecuta el script recolector [`scripts/actualizar_datos.py`](file:///scripts/actualizar_datos.py).
  4. Publica los JSON resultantes de vuelta en la rama `data` con `--force`.

### 1.1 Workflow Diario de Normas Legales (`normas_diario.yml`)

El monitoreo directo de Normas Legales de *El Peruano* opera en un workflow independiente: [`.github/workflows/normas_diario.yml`](file:///.github/workflows/normas_diario.yml).
- **Frecuencia programada:** Dos pasadas diarias en UTC: `15 11 * * *` (06:15 PET) y `15 23 * * *` (18:15 PET).
- **Idempotencia y almacenamiento:** Consulta el listado `NL` del día con `User-Agent: ApocunaBot/1.0 (+https://github.com/Dase1nn/Apocuna)` (pausa `>= 2.2 s`), filtra exclusiones sin almacenar nombres de personas ni textos íntegros ni PDFs, calcula el `SHA-256` del texto oficial en memoria y guarda fichas acumuladas por mes en `data/generated/normas_oficiales/AAAA-MM.json`.
- **Interruptor e IA verificada:** `NORMAS_IA_HABILITADA` en [`config.py`](file:///config.py) está activo (`True`) para invocar Gemini (`gemini-2.5-flash` vía SDK oficial `google-genai`) con las instrucciones versionadas de [`scripts/prompts/norma_v1.md`](file:///scripts/prompts/norma_v1.md); si se cambia a `False`, publica únicamente el radar determinístico sin IA.
- **Términos de Gemini API (nivel gratuito vs. pago):** Según las condiciones de servicio de Google AI (`ai.google.dev`), el nivel gratuito (*Unpaid Services*) puede utilizar entradas y respuestas para mejorar los productos y modelos de Google (y revisores humanos pueden auditarlas), mientras que los servicios de pago (*Paid Services*) no entrenan con las entradas. Este pipeline envía únicamente texto público de normas legales ya filtrado sin nombres de personas.
- **Verificación bloqueante y fail-safe:** [`scripts/normas/verificador_ia.py`](file:///scripts/normas/verificador_ia.py) comprueba que cada número de norma citado, artículo y extracto (`<= 25` palabras) exista literalmente en el texto fuente y prohíbe juicios o superación de topes (`NORMAS_TOPE_DIARIO_IA`, `NORMAS_TOPE_LLAMADAS_IA`). Si la IA o la verificación fallan, **no se publica ninguna ficha nueva** y se registra el fallo únicamente en `data/generated/estado.json`.
- **Revisión humana prioritaria:** Si existe `data/normas_comentadas/<id>.md`, prevalece sobre el borrador automático con estado `"revisado por persona"`.

---

## 2. Secrets Requeridos y Opcionales

- **`GITHUB_TOKEN`:** Proporcionado automáticamente por GitHub Actions. Requiere permisos de escritura (`contents: write`) para publicar en la rama `data`.
- **`GEMINI_API_KEY` (Opcional):** Si está configurada en los Secrets del repositorio, se utiliza para generar resúmenes breves y directos de noticias cuando el texto del artículo lo amerita. Si no está configurada, el pipeline continúa su ejecución normal conservando el texto original sin resumir.

---

## 3. Ejecución Manual

Para forzar una actualización manual sin esperar al cron de 3 horas:
1. Ir a la pestaña **Actions** en el repositorio de GitHub.
2. En la lista izquierda, seleccionar el workflow **Actualizar Datos**.
3. Hacer clic en el menú desplegable **Run workflow**.
4. Seleccionar la rama principal (`main`) y pulsar **Run workflow**.

Al ejecutarse manualmente (`workflow_dispatch`), el workflow inyecta el flag `--forzar` a [`scripts/actualizar_datos.py`](file:///scripts/actualizar_datos.py), ignorando los umbrales de tiempo y forzando la recolección en todas las fuentes.

---

## 4. Lectura de Logs y Diagnóstico de CKAN

Para auditar una ejecución:
1. En la pestaña **Actions**, hacer clic en la ejecución correspondiente y abrir el trabajo `update-data`.
2. Desplegar el paso **Diagnóstico CKAN desde GitHub**:
   - Este paso prueba con `curl` (timeout de 15 segundos) los endpoints de la PCM y del MINSA.
   - Observar el código HTTP devuelto:
     - `HTTP 404` o `HTTP 418`: Confirma que la ruta del endpoint no existe o está bloqueada por el WAF del portal.
     - `HTTP 000` / `curl falló`: Confirma falla de conexión o tiempo de espera agotado (timeout).
   - El paso tiene `continue-on-error: true` para no abortar el flujo general si los portales externos están caídos.

---

## 5. Qué hacer si una fuente falla

Si alguna fuente no actualiza o entrega 0 ítems:
1. Inspeccionar el archivo [`data/generated/estado.json`](file:///data/generated/estado.json).
2. Revisar el bloque de la fuente afectada (`noticias`, `normas`, `ckan`):
   - Contiene la marca temporal UTC de último éxito (`last_success`).
   - La lista de errores recientes con el código HTTP y causa descriptiva comprobada (por ejemplo: `404: ruta de API CKAN inexistente` o `sin conexión: tiempo de espera agotado`).
3. Para noticias y normas, el recolector conserva los datos válidos previos para garantizar alta disponibilidad en el dashboard.
4. Para CKAN, ante falla o indisponibilidad de API estructurada, se escribe una lista vacía `[]` en `ckan.json` para no mostrar datos ficticios o demos obsoletos, desplegando en su lugar los enlaces directos a los portales en la app.

---

## 6. Desactivación Automática de GitHub Actions

GitHub desactiva automáticamente los flujos programados (`schedule`) si el repositorio no registra actividad o commits durante **60 días consecutivos**.
- **Cómo detectarlo:** GitHub envía una notificación por correo al propietario advirtiendo la suspensión del cron.
- **Cómo reactivarlo:** Ingresar a la pestaña **Actions**, seleccionar el workflow marcado como suspendido y hacer clic en el botón **Enable workflow**. Alternativamente, cualquier nuevo commit en el repositorio reactiva el temporizador.

---

## 7. Fuentes Pendientes de Integración

Quedan identificadas para futuras fases de recolección automatizada:
- **INEI:** Consulta automatizada al Sistema SIGA y microdatos ENAHO/ENDES.
- **MEF:** Consulta presupuestal y de ejecución de inversiones (SIAF/Consulta Amigable).
- **Congreso de la República:** Estado situacional de proyectos de ley y agendas de comisiones.
- **Think Tanks:** Scraping o APIs de repositorios académicos (IEP, GRADE, CIES, IPE).

---

## 8. Límites Conocidos del Sistema

1. **Normas Legales:** El bloque de **Inicio** consume noticias regulatorias agregadas vía Google News RSS (`normas.json`). En **Polity and Policy → Normas comentadas**, el radar diario consulta directamente `busquedas.elperuano.pe` respetando `robots.txt` y pausas mínimas de `2.2 s`; no almacena PDFs ni textos íntegros ni reemplaza la fuente oficial. Cuando se habilite IA (`NORMAS_IA_HABILITADA = True`), los borradores se muestran bajo advertencia visible y requieren verificación en el diario oficial.
2. **Portal CKAN MINSA (`datos.minsa.gob.pe`):** No se encuentra disponible en la red (produce timeout de conexión verificado al 2026-10-02). Se encuentra desactivado por defecto mediante `CKAN_MINSA_HABILITADO = False` en [`config.py`](file:///config.py).
3. **Portal CKAN PCM (`www.datosabiertos.gob.pe`):** Es una instalación CMS Drupal 7 que no expone la API estándar de CKAN (`/api/3/action/package_search` devuelve 404). Además, su `robots.txt` prohíbe el acceso a rutas `/search/` y exige un delay de 10 segundos entre peticiones, por lo que no se realiza scraping de su interfaz HTML.
