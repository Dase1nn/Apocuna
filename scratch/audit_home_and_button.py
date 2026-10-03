import sys
sys.stdout.reconfigure(encoding='utf-8')
import asyncio
import os
from playwright.async_api import async_playwright

async def audit():
    os.makedirs("auditoria_tema", exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=True)
        page = await browser.new_page(viewport={"width": 1600, "height": 1100})
        
        print("1. Cargando http://localhost:8501/ en tema oscuro...")
        await page.goto("http://localhost:8501/", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # 2. Verificar bloque superior en Inicio
        intro_block = page.locator('.hero-intro-block').first
        is_intro_visible = await intro_block.is_visible()
        print(f"Bloque de introducción visible: {is_intro_visible}")

        title_el = page.locator('.hero-intro-title').first
        title_text = await title_el.inner_text() if await title_el.is_visible() else "NO VISIBLE"
        print(f"Título del bloque: {title_text}")

        desc_el = page.locator('.hero-intro-text').first
        desc_text = await desc_el.inner_text() if await desc_el.is_visible() else "NO VISIBLE"
        print(f"Texto del bloque: {desc_text}")
        word_count = len(desc_text.split())
        print(f"Conteo de palabras: {word_count}")

        # Comprobar posición respecto a st.title
        radar_title = page.locator('text=🌐 Inicio: Radar de Coyuntura, Normas y Fuentes').first
        intro_box = await intro_block.bounding_box()
        radar_box = await radar_title.bounding_box()
        print(f"Posición Y bloque intro: {intro_box['y']}, Posición Y radar title: {radar_box['y']}")
        assert intro_box['y'] < radar_box['y'], "El bloque intro debe estar ARRIBA del título de inicio"

        # Comprobar ausencia de 🔗 ancla
        anchors = await intro_block.locator('a[href^="#"], [data-testid="stHeaderActionElements"]').all()
        visible_anchors = [a for a in anchors if await a.is_visible()]
        print(f"Iconos de ancla visibles en el bloque: {len(visible_anchors)}")

        # Captura de Inicio en tema oscuro
        dark_cap = os.path.abspath("auditoria_tema/inicio_dark.png")
        await page.screenshot(path=dark_cap)
        print(f"Captura guardada en: {dark_cap}")

        # 3. Comprobar botón 'Conocer el sitio'
        btn = page.locator('button:has-text("Conocer el sitio")').first
        print(f"Botón 'Conocer el sitio' visible: {await btn.is_visible()}")
        btn_text = await btn.inner_text()
        print(f"Texto literal del botón: '{btn_text}'")
        assert "↗" not in btn_text, "El botón no debe mostrar el icono ↗"

        print("Haciendo click en 'Conocer el sitio'...")
        await btn.click()
        await page.wait_for_timeout(2500)

        # Verificar navegación a 'Sobre el sitio'
        sobre_title = page.locator('text=Sobre Apocuna').first
        is_sobre_visible = await sobre_title.is_visible()
        print(f"¿Navegó a 'Sobre el sitio'?: {is_sobre_visible}")
        if is_sobre_visible:
            print("Contenido visible en 'Sobre el sitio':", (await page.locator('.stMain').inner_text())[:200])

        # 4. Captura de Inicio en tema claro
        print("\n4. Evaluando tema claro...")
        # Volvemos a Inicio
        frame = [f for f in page.frames if 'streamlit_option_menu' in f.url][0]
        inicio_menu = frame.locator('span:has-text("Inicio")').first
        await inicio_menu.click()
        await page.wait_for_timeout(2000)

        # Aplicar color-scheme light
        await page.evaluate("""() => {
            document.documentElement.style.colorScheme = 'light';
            document.body.style.colorScheme = 'light';
            const main = document.querySelector('.stApp');
            if (main) {
                main.style.backgroundColor = '#FFFFFF';
                main.style.color = '#0F172A';
            }
        }""")
        await page.wait_for_timeout(1000)

        light_cap = os.path.abspath("auditoria_tema/inicio_light.png")
        await page.screenshot(path=light_cap)
        print(f"Captura en tema claro guardada en: {light_cap}")

        # 5. Prueba responsiva en pantalla angosta (400px ancho)
        await page.set_viewport_size({"width": 420, "height": 900})
        await page.wait_for_timeout(1000)
        narrow_cap = os.path.abspath("auditoria_tema/inicio_narrow.png")
        await page.screenshot(path=narrow_cap)
        print(f"Captura en pantalla angosta guardada en: {narrow_cap}")

        await browser.close()
        print("Auditoría completada exitosamente.")

if __name__ == "__main__":
    asyncio.run(audit())
