import sys
sys.stdout.reconfigure(encoding='utf-8')
import asyncio
from playwright.async_api import async_playwright

async def audit_all_pages_mobile():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome", headless=True)
        page = await b.new_page(viewport={"width": 390, "height": 844})
        await page.goto("http://localhost:8501/", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # 1. Mobile Home Top
        await page.screenshot(path="auditoria_tema/mobile_v2_home_top.png")

        # Scroll .stMain
        main_el = page.locator('.stMain, [data-testid="stMain"]').first
        await main_el.evaluate("el => el.scrollBy(0, 500)")
        await page.wait_for_timeout(600)
        await page.screenshot(path="auditoria_tema/mobile_v2_home_cards.png")

        # 2. Open Sidebar
        expand_btn = page.locator('button[data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapsedControl"] button').first
        await expand_btn.click()
        await page.wait_for_timeout(1000)
        await page.screenshot(path="auditoria_tema/mobile_v2_sidebar_open.png")

        # 3. Navigate to Polity and Policy
        iframe = page.frame_locator('iframe').first
        pol_btn = iframe.locator('text=Polity and Policy')
        await pol_btn.click()
        await page.wait_for_timeout(1500)
        # Close sidebar to view page
        collapse_btn = page.locator('[data-testid="stSidebarCollapseButton"] button').first
        if await collapse_btn.is_visible():
            await collapse_btn.click()
            await page.wait_for_timeout(1000)
        await page.screenshot(path="auditoria_tema/mobile_v2_polity_page.png")

        # 4. Navigate to Estudiantes (DEMO)
        await expand_btn.click()
        await page.wait_for_timeout(1000)
        est_btn = iframe.locator('text=Estudiantes (DEMO)')
        await est_btn.click()
        await page.wait_for_timeout(1500)
        if await collapse_btn.is_visible():
            await collapse_btn.click()
            await page.wait_for_timeout(1000)
        await page.screenshot(path="auditoria_tema/mobile_v2_estudiantes_page.png")

        # 5. Navigate to Sobre el sitio
        await expand_btn.click()
        await page.wait_for_timeout(1000)
        sobre_btn = iframe.locator('text=Sobre el sitio')
        await sobre_btn.click()
        await page.wait_for_timeout(1500)
        if await collapse_btn.is_visible():
            await collapse_btn.click()
            await page.wait_for_timeout(1000)
        await page.screenshot(path="auditoria_tema/mobile_v2_sobre_el_sitio_page.png")

        print("All mobile page screenshots captured successfully!")
        await b.close()

if __name__ == "__main__":
    asyncio.run(audit_all_pages_mobile())
