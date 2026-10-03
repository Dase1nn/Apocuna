import sys
sys.stdout.reconfigure(encoding='utf-8')
import asyncio
from playwright.async_api import async_playwright

async def verify_mobile_estudiantes_view():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome", headless=True)
        page = await b.new_page(viewport={"width": 390, "height": 844})
        await page.goto("http://localhost:8501/", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # Open sidebar
        expand_btn = page.locator('button[data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapsedControl"] button').first
        await expand_btn.click()
        await page.wait_for_timeout(1000)

        # Click Estudiantes (DEMO)
        iframe = page.frame_locator('iframe').first
        await iframe.locator('text=Estudiantes (DEMO)').click()
        await page.wait_for_timeout(2000)

        # Close sidebar
        collapse_btn = page.locator('[data-testid="stSidebarCollapseButton"] button').first
        await collapse_btn.click()
        await page.wait_for_timeout(1000)

        await page.screenshot(path="auditoria_tema/mobile_estudiantes_direct.png")

        # Scroll down
        main_el = page.locator('.stMain, [data-testid="stMain"]').first
        await main_el.evaluate("el => el.scrollBy(0, 400)")
        await page.wait_for_timeout(600)
        await page.screenshot(path="auditoria_tema/mobile_estudiantes_scroll.png")

        print("Mobile Estudiantes views captured!")
        await b.close()

if __name__ == "__main__":
    asyncio.run(verify_mobile_estudiantes_view())
