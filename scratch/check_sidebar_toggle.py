import sys
sys.stdout.reconfigure(encoding='utf-8')
import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chrome', headless=True)
        page = await b.new_page(viewport={'width': 400, 'height': 850})
        await page.goto('http://localhost:8501/')
        await page.wait_for_timeout(2500)
        
        btn = page.locator('[data-testid="stExpandSidebarButton"]').first
        print('HTML:', await btn.evaluate('el => el.outerHTML'))
        print('Parent HTML:', await btn.evaluate('el => el.parentElement.outerHTML'))
        styles = await btn.evaluate('''el => {
            const s = window.getComputedStyle(el);
            return {
                visibility: s.visibility,
                opacity: s.opacity,
                color: s.color,
                backgroundColor: s.backgroundColor,
                border: s.border,
                borderRadius: s.borderRadius,
                boxShadow: s.boxShadow
            };
        }''')
        print('Styles:', styles)

        # Now test desktop (expanded sidebar collapse button)
        await page.set_viewport_size({'width': 1400, 'height': 900})
        await page.wait_for_timeout(1000)
        collapse_btn = page.locator('[data-testid="stSidebarCollapseButton"] button, [data-testid="stSidebar"] button[kind="header"]').first
        if await collapse_btn.count() > 0:
            print('Desktop collapse button HTML:', await collapse_btn.evaluate('el => el.outerHTML'))
            cstyles = await collapse_btn.evaluate('''el => {
                const s = window.getComputedStyle(el);
                return {
                    visibility: s.visibility,
                    opacity: s.opacity,
                    color: s.color,
                    backgroundColor: s.backgroundColor
                };
            }''')
            print('Desktop collapse button styles:', cstyles)

        await b.close()

if __name__ == '__main__':
    asyncio.run(run())
