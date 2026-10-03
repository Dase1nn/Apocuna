import sys
sys.stdout.reconfigure(encoding='utf-8')
import asyncio
import os
from playwright.async_api import async_playwright

async def capture():
    os.makedirs("auditoria_tema", exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome", headless=True)
        page = await b.new_page(viewport={"width": 1600, "height": 1100})
        await page.goto("http://localhost:8501/", wait_until="networkidle")
        await page.wait_for_timeout(2500)

        # Apply light mode
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

        light_path = os.path.abspath("auditoria_tema/inicio_light.png")
        await page.screenshot(path=light_path)
        print(f"Saved: {light_path}")

        # Test mobile / narrow viewport
        await page.set_viewport_size({"width": 420, "height": 950})
        await page.wait_for_timeout(1000)
        narrow_path = os.path.abspath("auditoria_tema/inicio_narrow.png")
        await page.screenshot(path=narrow_path)
        print(f"Saved: {narrow_path}")

        # Restore desktop width and test button click
        await page.set_viewport_size({"width": 1600, "height": 1100})
        await page.wait_for_timeout(500)
        btn = page.locator('button:has-text("Conocer el sitio")').first
        await btn.click()
        await page.wait_for_timeout(2500)

        # Check navigation
        sobre_title = page.locator('text=Sobre Apocuna').first
        print("Llegó a 'Sobre el sitio' tras click?:", await sobre_title.is_visible())
        
        # Save screenshot of Sobre el sitio
        sobre_path = os.path.abspath("auditoria_tema/sobre_el_sitio_navigated.png")
        await page.screenshot(path=sobre_path)
        print(f"Saved: {sobre_path}")

        await b.close()

if __name__ == "__main__":
    asyncio.run(capture())
