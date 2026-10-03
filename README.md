# Apocuna Dashboard

**Apocuna Dashboard** es una plataforma analítica y hub de información pública orientada a estudiantes, investigadores y profesionales de Ciencia Política y Gestión Pública en el Perú. Reúne en un único entorno accesible, moderno y adaptable (con tema oscuro por defecto y soporte para modo claro) noticias sobre coyuntura política y gobernanza, seguimiento de normas legales, un catálogo auditado de fuentes y portales institucionales, insumos analíticos para formulación y evaluación de políticas públicas (*Polity and Policy*), recursos formativos y repositorios metodológicos, convocatorias a revistas académicas y notas de investigación.

---

## Estructura del Proyecto

```text
Apocuna/
├── .github/
│   └── workflows/
│       └── actualizar.yml       # Automatización periódica en GitHub Actions (cron y dispatch)
├── .streamlit/
│   └── config.toml              # Configuración de tema (oscuro por defecto) y servidor
├── assets/
│   └── style.css                # Sistema de diseño Snowsight (variables light-dark, tarjetas, botones y grids)
├── components/
│   ├── cards.py                 # Componentes visuales: carruseles horizontales, tarjetas, grids y botones
│   └── sidebar.py               # Menú lateral interactivo de navegación
├── data/
│   ├── fuentes.json             # Catálogo clasificado de fuentes institucionales y APIs oficiales
│   ├── eventos.json             # Convocatorias a revistas científicas y congresos académicos
│   ├── polity.json              # Insumos, repositorios y fuentes para diseño y evaluación de políticas
│   ├── estudiantes.json         # Repositorios de datos, microdatos y apuntes metodológicos
│   ├── cursos.json              # Catálogo de formación continua y cursos gratuitos oficiales
│   ├── becas.json               # Directorio de becas y oportunidades académicas verificadas
│   ├── sobre_el_sitio.md        # Manifiesto y fundamentación del proyecto
│   ├── notas/                   # Artículos de investigación y notas analíticas en Markdown
│   │   ├── G ESCOLAR.md
│   │   ├── nota2.md
│   │   └── nota3.md
│   └── generated/               # Datos sincronizados o generados por el pipeline de recolección
│       ├── noticias.json        # Noticias recientes clasificadas por categoría
│       ├── normas.json          # Dispositivos y notas sobre normas legales recientes
│       ├── ckan.json            # Datasets recopilados de portales CKAN
│       ├── academico.json       # Alertas de publicaciones y literatura científica
│       ├── polity_alertas.json  # Alertas institucionales y regulatorias
│       ├── eventos_alertas.json # Alertas de congresos y convocatorias
│       └── estado.json          # Diagnóstico, estado de portales, timestamps y trazabilidad
├── docs/
│   ├── AUTOMATIZACION.md        # Documentación técnica del pipeline, sincronización y auditoría
│   └── PROYECTO.md              # Mapeo exhaustivo de fuentes de información y bases de datos del sector
├── scripts/
│   ├── actualizar_datos.py      # Orquestador del flujo de extracción, deduplicación y resúmenes
│   ├── fuentes/
│   │   ├── noticias.py          # Extracción y filtrado de noticias desde feeds RSS
│   │   ├── normas.py            # Extracción de notas sobre normas legales desde feeds RSS
│   │   ├── ckan.py              # Integración y diagnóstico de portales de datos abiertos CKAN
│   │   ├── academico.py         # Extracción de literatura académica y convocatorias
│   │   ├── polity_alertas.py    # Recolección de alertas normativas e institucionales
│   │   └── eventos_alertas.py   # Monitoreo de convocatorias a congresos y eventos
│   ├── validar_datos.py         # Script de validación de estructura e integridad de archivos JSON
│   ├── verificar_links.py       # Auditoría de disponibilidad y respuesta HTTP de URLs
│   └── test_loaders.py          # Pruebas de integración de la capa de carga de datos
├── sections/
│   ├── home.py                  # Vista Inicio: radar de coyuntura, normas legales y catálogo de fuentes
│   ├── polity.py                # Vista Polity and Policy: insumos analíticos y alertas de modernización
│   ├── estudiantes.py           # Vista Estudiantes: microdatos, cursos, becas y apuntes simulados
│   ├── notas.py                 # Vista Notas: visor dinámico de publicaciones y ensayos Markdown
│   ├── eventos.py               # Vista Eventos: convocatorias permanentes y congresos del sector
│   └── sobre_el_sitio.py        # Vista Sobre el sitio: marco conceptual y oficio politológico
├── utils/
│   ├── api.py                   # Funciones para peticiones HTTP con control de excepciones y timeout
│   └── loaders.py               # Capa de datos con caché (@st.cache_data) y fallback remoto/local
├── app.py                       # Punto de entrada de la aplicación Streamlit y enrutador principal
├── config.py                    # Constantes operativas, banderas de portales y paleta de colores
├── requirements.txt             # Dependencias necesarias para ejecutar la aplicación web
└── requirements-actions.txt     # Dependencias requeridas por el workflow de GitHub Actions
```

---

## Ejecución Local (Windows)

Se recomienda utilizar **Python 3.12**.

1. **Clonar el repositorio:**
   ```powershell
   git clone https://github.com/Dase1nn/Apocuna.git
   cd Apocuna
   ```

2. **Crear y activar el entorno virtual:**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Instalar las dependencias de la aplicación:**
   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

4. **Iniciar la aplicación:**
   ```powershell
   .\.venv\Scripts\python.exe -m streamlit run app.py
   ```
   La aplicación se abrirá en el navegador web (por defecto en `http://localhost:8501`).

5. **Actualización manual de datos (Opcional):**
   Para ejecutar el proceso de recolección y sincronización localmente:
   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements-actions.txt
   .\.venv\Scripts\python.exe scripts/actualizar_datos.py --forzar
   ```

---

## Tema Visual y Experiencia de Usuario

La plataforma está configurada con **tema oscuro por defecto** (`base = "dark"`) en [`.streamlit/config.toml`](.streamlit/config.toml), complementado por la hoja de estilos [`assets/style.css`](assets/style.css). La paleta y tipografía se ajustan dinámicamente mediante variables CSS `light-dark()`, garantizando niveles de contraste WCAG AA/AAA (superiores a 4.5:1 tanto en tema oscuro como en claro) y diseño responsivo para pantallas móviles y de escritorio.

---

## Flujo de Datos y Automatización

El sistema implementa una arquitectura desacoplada para garantizar alta disponibilidad:

```text
[ Fuentes Externas ] 
  (Feeds RSS / Portales)
           │
           ▼
[ GitHub Actions: actualizar.yml ] (Ejecución periódica programada o manual)
           │
           ▼
[ Rama 'data' en GitHub ] (data/generated/*.json)
           │
           ▼  (Vía DATA_BASE_URL por HTTPS)
[ Aplicación Streamlit ] ──(Fallback local si no hay red o secrets)──> [ data/generated/*.json local ]
```

1. **Extracción y procesamiento:** El flujo de trabajo en GitHub Actions (`.github/workflows/actualizar.yml`) corre periódicamente. Ejecuta `scripts/actualizar_datos.py`, que recolecta, limpia, deduplica y formatea los datos.
2. **Persistencia en rama `data`:** Los archivos resultantes (`noticias.json`, `normas.json`, `ckan.json`, `academico.json`, `polity_alertas.json`, `eventos_alertas.json`, `estado.json`) se publican en una rama huérfana e independiente denominada `data`.
3. **Consumo en la aplicación:** La aplicación web intenta leer los datos remotos frescos desde la URL configurada en el secreto `DATA_BASE_URL`. Si dicho secreto no está presente o falla la conexión, la aplicación recurre de forma transparente a los datos estáticos locales guardados en `data/generated/`.

Para más detalles sobre la arquitectura del flujo, frecuencia de ejecución, manejo de errores y diagnóstico, revise [`docs/AUTOMATIZACION.md`](docs/AUTOMATIZACION.md).

---

## Límites Conocidos

- **Normas legales en Home:** Los registros mostrados provienen de agregadores de noticias y feeds RSS (Google News). **No constituyen el listado oficial ni reemplazan la publicación legal vinculante**, cuya única validez jurídica radica en el Diario Oficial El Peruano y el Sistema Peruano de Información Jurídica (SPIJ).
- **Portal CKAN MINSA:** Se encuentra deshabilitado preventivamente (`CKAN_MINSA_HABILITADO = False` en `config.py`) debido a problemas recurrentes de disponibilidad y tiempos de espera agotados (verificado 2026-10-02).
- **Portal CKAN PCM (Plataforma Nacional de Datos Abiertos):** Bloquea activamente peticiones automáticas mediante un Web Application Firewall (WAF emite respuesta HTTP 418, verificado 2026-10-02). Siguiendo las directrices de seguridad y honestidad técnica, no se emplean cabeceras falsificadas ni mecanismos de evasión. Se encuentra deshabilitado en el pipeline (`CKAN_PCM_HABILITADO = False`), mostrándose en la interfaz enlaces directos a los portales para su consulta manual.
- **Fuentes pendientes:** La integración automatizada de microdatos de INEI, indicadores del MEF, proyectos del Congreso de la República y publicaciones de think tanks nacionales (IEP, GRADE, IPE, CIES) está catalogada conceptualmente en `data/fuentes.json` y `docs/PROYECTO.md`, pero su extracción sistemática mediante API se encuentra en fase de diseño o sujeta a la disponibilidad técnica de dichos organismos.
- **Sección Estudiantes (Apuntes y Guías):** Las tarjetas correspondientes a apuntes de sistemas administrativos (SIAF, SIGA, Planeamiento Estratégico, etc.) son **demostraciones simuladas (Demo)** con fines de diseño de interfaz pedagógica, a la espera de la integración de contenidos de autoría propia o enlaces a repositorios institucionales de acceso libre.

---

## Despliegue en Streamlit Community Cloud

*(Instrucciones de carácter indicativo; la interfaz del servicio en la nube puede variar con el tiempo)*

1. Inicie sesión en [Streamlit Community Cloud](https://share.streamlit.io/) con su cuenta vinculada de GitHub.
2. Haga clic en **New app**.
3. Configure los datos del repositorio:
   - **Repository:** `Dase1nn/Apocuna`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. En **Advanced settings**:
   - **Python version:** Seleccione `3.12`.
   - En la sección **Secrets**, configure la URL base apuntando a la rama `data`:
     ```toml
     DATA_BASE_URL = "https://raw.githubusercontent.com/Dase1nn/Apocuna/refs/heads/data/data/generated"
     ```
5. Haga clic en **Deploy!**.

---

## Licencia

[POR COMPLETAR]

---

## Créditos y Agradecimientos

[POR COMPLETAR]
