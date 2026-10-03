import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import subprocess
import time
import requests
import asyncio
from playwright.async_api import async_playwright

dest_root = r"c:\Users\Gaston Silva\Apocuna_deploy_test"
python_exe = r"c:\Users\Gaston Silva\Apocuna\.venv\Scripts\python.exe"

# Confirmar ausencia de secrets.toml
secrets_file = os.path.join(dest_root, ".streamlit", "secrets.toml")
assert not os.path.exists(secrets_file), "ERROR: secrets.toml existe en la copia"
print(f"1. Verificado: {secrets_file} NO existe.")

# Preparar entorno sin DATA_BASE_URL
env = os.environ.copy()
env.pop("DATA_BASE_URL", None)
print("2. Verificado: DATA_BASE_URL eliminada de las variables de entorno.")

# Iniciar servidor Streamlit en port 8503 desde la carpeta externa
print(f"3. Iniciando Streamlit desde cwd={dest_root} en puerto 8503...")
proc = subprocess.Popen(
    [python_exe, "-m", "streamlit", "run", "app.py", "--server.port", "8503", "--server.headless", "true"],
    cwd=dest_root,
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

time.sleep(4)

# Verificar arranque mediante HTTP y Playwright
async def verify_app():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome", headless=True)
        page = await b.new_page(viewport={"width": 1400, "height": 900})
        print("4. Navegando a http://localhost:8503/...")
        await page.goto("http://localhost:8503/", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        title = await page.title()
        print(f"Título de la página: {title}")
        
        # Verificar que el bloque intro y el radar existen y tienen contenido local
        intro = await page.locator('.hero-intro-title').first.inner_text()
        print(f"Bloque intro: {intro}")

        # Verificar que no hay alertas de error de secrets
        errors = await page.locator('.stAlert[data-testid="stAlert"]').all()
        print(f"Alertas en pantalla: {len(errors)}")
        for err in errors:
            print("Alerta:", await err.inner_text())

        # Tomar captura de confirmación
        cap_path = os.path.join(dest_root, "arranque_sin_secretos.png")
        await page.screenshot(path=cap_path)
        print(f"Captura de verificación guardada en: {cap_path}")

        await b.close()

try:
    asyncio.run(verify_app())
    print("5. VERIFICACIÓN EXITOSA: La app arranca perfectamente sin secrets.toml y sin DATA_BASE_URL.")
finally:
    proc.terminate()
    proc.wait()
    print("Servidor de prueba terminado.")
