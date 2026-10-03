import sys
sys.stdout.reconfigure(encoding='utf-8')
import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chrome', headless=True)
        page = await b.new_page(viewport={"width": 1600, "height": 1100})
        await page.goto('http://localhost:8501/', wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        main_html = await page.locator('.stMain').inner_html()
        with open("scratch/page_dump.html", "w", encoding="utf-8") as f:
            f.write(main_html)
        print("Wrote scratch/page_dump.html (length:", len(main_html), ")")

        # Check if hero-intro-block is in HTML
        print("hero-intro-block in html?", "hero-intro-block" in main_html)
        print("Bienvenido a Apocuna in html?", "Bienvenido a Apocuna" in main_html)
        print("Radar de Coyuntura in html?", "Radar de Coyuntura" in main_html)
        await b.close()

if __name__ == "__main__":
    asyncio.run(inspect())
