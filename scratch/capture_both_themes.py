import sys
sys.stdout.reconfigure(encoding='utf-8')
import asyncio
import os
from playwright.async_api import async_playwright

async def capture():
    os.makedirs("auditoria_tema", exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome", headless=True)
        # Context with explicit light color_scheme
        context = await b.new_context(
            viewport={"width": 1600, "height": 1100},
            color_scheme="light"
        )
        page = await context.new_page()
        await page.goto("http://localhost:8501/", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        light_path = os.path.abspath("auditoria_tema/inicio_light.png")
        await page.screenshot(path=light_path)
        print(f"Saved light screenshot: {light_path}")

        # Narrow viewport
        await page.set_viewport_size({"width": 420, "height": 950})
        await page.wait_for_timeout(1000)
        narrow_path = os.path.abspath("auditoria_tema/inicio_narrow.png")
        await page.screenshot(path=narrow_path)
        print(f"Saved narrow screenshot: {narrow_path}")

        # Now test Dark context
        context_dark = await b.new_context(
            viewport={"width": 1600, "height": 1100},
            color_scheme="dark"
        )
        page_dark = await context_dark.new_page()
        await page_dark.goto("http://localhost:8501/", wait_until="networkidle")
        await page_dark.wait_for_timeout(3000)

        dark_path = os.path.abspath("auditoria_tema/inicio_dark.png")
        await page_dark.screenshot(path=dark_path)
        print(f"Saved dark screenshot: {dark_path}")

        # Test button click in dark context
        btn = page_dark.locator('button:has-text("Conocer el sitio")').first
        await btn.click()
        await page_dark.wait_for_timeout(2500)
        sobre_title = page_dark.locator('text=Sobre Apocuna').first
        print("Llegó a 'Sobre el sitio' tras click?:", await sobre_title.is_visible())

        await b.close()

if __name__ == "__main__":
    asyncio.run(capture())
