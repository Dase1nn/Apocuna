import os

# Colores (Estilo Snowsight)
COLOR_PRIMARY = "#29B5E8"
COLOR_DARK = "#11567F"
BG_LIGHT = "#FFFFFF"

# URLs base - Sin prefijos de Google
URL_JNE = "https://www.jne.gob.pe/"
URL_ONPE = "https://www.onpe.gob.pe/"

# Constantes de configuración
TIMEOUT_RED = 10  # segundos
EXCLUDED_DOMAINS = ["facebook.com", "youtube.com", "tiktok.com", "instagram.com"]

# Indicador para reactivar portal CKAN MINSA si vuelve a estar en línea (inactivo por timeout verificado 2026-10-02)
CKAN_MINSA_HABILITADO = False

# Indicador para reactivar portal CKAN PCM si vuelve a estar accesible para clientes automáticos (bloqueado por WAF HTTP 418 verificado 2026-10-02)
CKAN_PCM_HABILITADO = False

# Automatización diaria de Normas Legales (El Peruano)
NORMAS_IA_HABILITADA = True
GEMINI_MODELO_NORMAS = "gemini-3.5-flash-lite"
GEMINI_MODELOS_RESPALDO_NORMAS = ["gemini-3.6-flash", "gemini-3.8-flash"]
NORMAS_PROMPT_VERSION = "norma_v1"
NORMAS_TOPE_DIARIO_IA = 15
NORMAS_TOPE_LLAMADAS_IA = 25
NORMAS_MAX_REINTENTOS_IA = 3
NORMAS_TOPE_EJECUCION = 80

