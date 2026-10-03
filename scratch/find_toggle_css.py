import sys
sys.stdout.reconfigure(encoding='utf-8')
import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome", headless=True)
        page = await b.new_page(viewport={"width": 1400, "height": 900})
        await page.goto("http://localhost:8501/")
        await page.wait_for_timeout(2500)

        # Inspect collapse button inside sidebar
        res = await page.evaluate('''() => {
            const btns = Array.from(document.querySelectorAll('button'));
            return btns.map(b => ({
                text: b.innerText,
                aria: b.getAttribute('aria-label'),
                testid: b.getAttribute('data-testid'),
                parentTestid: b.parentElement ? b.parentElement.getAttribute('data-testid') : null,
                classes: b.className,
                computed: {
                    display: window.getComputedStyle(b).display,
                    visibility: window.getComputedStyle(b).visibility,
                    opacity: window.getComputedStyle(b).opacity,
                    color: window.getComputedStyle(b).color,
                    background: window.getComputedStyle(b).backgroundColor,
                }
            }));
        }''')
        print("=== ALL BUTTONS IN DESKTOP ===")
        for r in res:
            print(r)

        # Now collapse sidebar by clicking the collapse button
        col_btn = page.locator('[data-testid="stSidebarCollapseButton"] button, [data-testid="stSidebar"] button').first
        if await col_btn.is_visible():
            await col_btn.click()
            await page.wait_for_timeout(1000)
            
        print("\n=== BUTTONS AFTER COLLAPSE / IN HEADER ===")
        res2 = await page.evaluate('''() => {
            const btns = Array.from(document.querySelectorAll('button'));
            return btns.map(b => ({
                text: b.innerText,
                aria: b.getAttribute('aria-label'),
                testid: b.getAttribute('data-testid'),
                parentTestid: b.parentElement ? b.parentElement.getAttribute('data-testid') : null,
                classes: b.className,
                computed: {
                    display: window.getComputedStyle(b).display,
                    visibility: window.getComputedStyle(b).visibility,
                    opacity: window.getComputedStyle(b).opacity,
                    color: window.getComputedStyle(b).color,
                    background: window.getComputedStyle(b).backgroundColor,
                }
            }));
        }''')
        for r in res2:
            print(r)

        await b.close()

if __name__ == '__main__':
    asyncio.run(inspect())
