import sys
sys.stdout.reconfigure(encoding='utf-8')
import asyncio
from playwright.async_api import async_playwright

async def inspect_element_at_point():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome", headless=True)
        page = await b.new_page(viewport={"width": 390, "height": 844})
        await page.goto("http://localhost:8501/", wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # Open sidebar
        expand_mobile = page.locator('button[data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapsedControl"] button').first
        await expand_mobile.click()
        await page.wait_for_timeout(1000)

        # Inspect element at collapse button location
        btn = page.locator('[data-testid="stSidebarCollapseButton"] button').first
        box = await btn.bounding_box()
        print("Button bounding box:", box)

        # Evaluate what element is at (box.x + 10, box.y + 10)
        cx = box['x'] + box['width'] / 2
        cy = box['y'] + box['height'] / 2
        top_el = await page.evaluate(f"""() => {{
            const el = document.elementFromPoint({cx}, {cy});
            const s = window.getComputedStyle(el);
            return {{
                tag: el.tagName,
                className: el.className,
                testid: el.getAttribute('data-testid'),
                id: el.id,
                zIndex: s.zIndex,
                outerHTML: el.outerHTML.substring(0, 300)
            }};
        }}""")
        print("Top element at button center point:", top_el)

        # Also get computed z-index of stSidebar, stSidebarHeader, stHeader, and banner
        z_indices = await page.evaluate("""() => {
            const getZ = sel => {
                const el = document.querySelector(sel);
                if (!el) return 'NOT_FOUND';
                return window.getComputedStyle(el).zIndex;
            };
            return {
                stHeader: getZ('[data-testid="stHeader"]'),
                stSidebar: getZ('[data-testid="stSidebar"]'),
                stSidebarHeader: getZ('[data-testid="stSidebarHeader"]'),
                stSidebarCollapseButton: getZ('[data-testid="stSidebarCollapseButton"]'),
                banner: getZ('#apocuna-hub-banner')
            };
        }""")
        print("Z-indices on mobile:", z_indices)

        await b.close()

if __name__ == "__main__":
    asyncio.run(inspect_element_at_point())
