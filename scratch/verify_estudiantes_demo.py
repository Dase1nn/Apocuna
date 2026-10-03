import sys
sys.stdout.reconfigure(encoding='utf-8')
import asyncio
from playwright.async_api import async_playwright

async def verify_estudiantes_and_toggles():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome", headless=True)

        # 1. Test Desktop Navigation to Estudiantes (DEMO)
        print("--- Testing Desktop ---")
        page = await b.new_page(viewport={"width": 1400, "height": 900})
        await page.goto("http://localhost:8501/", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # Locate iframe for option_menu
        iframe = page.frame_locator('iframe').first
        est_btn = iframe.locator('text=Estudiantes (DEMO)')
        print("Found Estudiantes (DEMO) in menu?", await est_btn.count() > 0)
        await est_btn.click()
        await page.wait_for_timeout(2500)

        # Check page title
        h1 = page.locator('h1').all()
        for header in await h1:
            txt = await header.inner_text()
            print("Found h1:", txt)

        await page.screenshot(path="auditoria_tema/desktop_estudiantes_demo.png")

        # 2. Test Mobile View
        print("\n--- Testing Mobile ---")
        await page.set_viewport_size({"width": 390, "height": 844})
        await page.wait_for_timeout(1500)

        # In mobile, let's collapse then expand to test both states
        collapse_btn = page.locator('[data-testid="stSidebarCollapseButton"] button').first
        if await collapse_btn.is_visible():
            await collapse_btn.click()
            await page.wait_for_timeout(1000)
            await page.screenshot(path="auditoria_tema/mobile_estudiantes_collapsed.png")

            expand_btn = page.locator('button[data-testid="stExpandSidebarButton"]').first
            print("Expand button visible on mobile?", await expand_btn.is_visible())
            await expand_btn.click()
            await page.wait_for_timeout(1000)
            await page.screenshot(path="auditoria_tema/mobile_estudiantes_expanded.png")

        print("Done verification!")
        await b.close()

if __name__ == "__main__":
    asyncio.run(verify_estudiantes_and_toggles())
