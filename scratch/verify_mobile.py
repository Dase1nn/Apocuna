import sys
sys.stdout.reconfigure(encoding='utf-8')
import asyncio
from playwright.async_api import async_playwright

async def verify_mobile():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome", headless=True)
        # Create fresh mobile page
        page = await b.new_page(viewport={"width": 390, "height": 844})
        await page.goto("http://localhost:8501/", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # On initial load on 390px, check if sidebar is collapsed or open
        expand_btn = page.locator('button[data-testid="stExpandSidebarButton"]').first
        collapse_btn = page.locator('[data-testid="stSidebarCollapseButton"] button').first

        is_collapsed = await expand_btn.is_visible()
        print(f"Mobile start state: collapsed={is_collapsed}")

        if is_collapsed:
            print("Taking screenshot of mobile with collapsed sidebar (showing >> button)...")
            await page.screenshot(path="auditoria_tema/mobile_sidebar_closed.png")

            print("Clicking expand button (>>)...")
            await expand_btn.click()
            await page.wait_for_timeout(1500)
            await page.screenshot(path="auditoria_tema/mobile_sidebar_opened.png")

            # Check that collapse button is now visible
            print("Is collapse button (<<) now visible?", await collapse_btn.is_visible())
            print("Clicking collapse button (<<)...")
            await collapse_btn.click()
            await page.wait_for_timeout(1500)
            print("Is expand button (>>) visible again?", await expand_btn.is_visible())
            await page.screenshot(path="auditoria_tema/mobile_sidebar_reclosed.png")
        else:
            print("Mobile sidebar started open.")
            await page.screenshot(path="auditoria_tema/mobile_sidebar_opened.png")
            print("Clicking collapse button (<<)...")
            await collapse_btn.click()
            await page.wait_for_timeout(1500)
            await page.screenshot(path="auditoria_tema/mobile_sidebar_closed.png")

        await b.close()

if __name__ == "__main__":
    asyncio.run(verify_mobile())
