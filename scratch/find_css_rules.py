import sys
sys.stdout.reconfigure(encoding='utf-8')
import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome", headless=True)
        page = await b.new_page(viewport={"width": 1400, "height": 900})
        await page.goto("http://localhost:8501/")
        await page.wait_for_timeout(2000)

        info = await page.evaluate("""() => {
            let el = document.querySelector('[data-testid="stSidebarCollapseButton"] button');
            const chain = [];
            while (el && el !== document.body) {
                const s = window.getComputedStyle(el);
                chain.push({
                    tag: el.tagName,
                    id: el.id,
                    className: el.className,
                    testid: el.getAttribute('data-testid'),
                    visibility: s.visibility,
                    opacity: s.opacity,
                    display: s.display
                });
                el = el.parentElement;
            }
            return chain;
        }""")
        print("PARENT CHAIN:")
        for item in info:
            print(item)
        await b.close()

if __name__ == '__main__':
    asyncio.run(inspect())
