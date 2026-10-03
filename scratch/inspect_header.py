import sys
sys.stdout.reconfigure(encoding='utf-8')
import asyncio
from playwright.async_api import async_playwright

async def inspect_header():
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=True)
        page = await browser.new_page(viewport={"width": 1600, "height": 1100})
        await page.goto("http://localhost:8501/", wait_until="networkidle")
        await page.wait_for_timeout(2000)

        header_buttons = await page.locator('[data-testid="stHeader"] button, header button').all()
        print(f"Header buttons: {len(header_buttons)}")
        for b in header_buttons:
            print("Button:", await b.get_attribute("aria-label"), await b.get_attribute("data-testid"), await b.inner_text())

        # Click the last header button (usually the 3 dots menu)
        if header_buttons:
            await header_buttons[-1].click()
            await page.wait_for_timeout(1000)
            menu_items = await page.locator('[role="menu"] [role="menuitem"], ul[role="menu"] li').all()
            print(f"Menu items: {len(menu_items)}")
            for mi in menu_items:
                print("Item:", await mi.inner_text())

        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_header())
