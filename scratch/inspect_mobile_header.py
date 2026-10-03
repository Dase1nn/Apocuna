import sys
sys.stdout.reconfigure(encoding='utf-8')
import asyncio
from playwright.async_api import async_playwright

async def inspect_mobile_header():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome", headless=True)
        # Mobile viewport
        page = await b.new_page(viewport={"width": 390, "height": 844})
        await page.goto("http://localhost:8501/", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # Check if sidebar is open or closed
        sidebar = page.locator('[data-testid="stSidebar"]').first
        sidebar_box = await sidebar.bounding_box()
        print("Sidebar bounding box:", sidebar_box)

        # Collapse button
        collapse_btn = page.locator('[data-testid="stSidebarCollapseButton"] button, [data-testid="stSidebar"] button[data-testid="stBaseButton-headerNoPadding"]').first
        print("Collapse button count:", await collapse_btn.count())
        if await collapse_btn.count() > 0:
            box = await collapse_btn.bounding_box()
            print("Collapse button bounding box:", box)
            is_vis = await collapse_btn.is_visible()
            print("Collapse button is_visible:", is_vis)
            styles = await collapse_btn.evaluate("""el => {
                const s = window.getComputedStyle(el);
                return {
                    display: s.display,
                    visibility: s.visibility,
                    opacity: s.opacity,
                    zIndex: s.zIndex,
                    background: s.backgroundColor,
                    color: s.color,
                    border: s.border,
                    position: s.position
                };
            }""")
            print("Collapse button computed styles:", styles)

            # Check if an element is covering it
            cx = box['x'] + box['width']/2
            cy = box['y'] + box['height']/2
            top_el = await page.evaluate(f"() => {{ const el = document.elementFromPoint({cx}, {cy}); return el ? el.outerHTML.substring(0, 200) : 'none'; }}")
            print("Element at button center point:", top_el)

        # Expand button (if closed)
        expand_btn = page.locator('button[data-testid="stExpandSidebarButton"]').first
        print("Expand button count:", await expand_btn.count())
        if await expand_btn.count() > 0:
            print("Expand button is_visible:", await expand_btn.is_visible())
            print("Expand button box:", await expand_btn.bounding_box())

        # Screenshot full page and header
        await page.screenshot(path="auditoria_tema/mobile_actual_load.png")

        # Let's toggle it: if open, click collapse; if closed, click expand
        if await collapse_btn.count() > 0 and (await collapse_btn.bounding_box())['x'] >= 0:
            print("Clicking collapse button to close sidebar...")
            await collapse_btn.click()
            await page.wait_for_timeout(1500)
            await page.screenshot(path="auditoria_tema/mobile_after_collapse_click.png")

            # Now check expand button
            if await expand_btn.count() > 0:
                print("Expand button visible after collapse:", await expand_btn.is_visible())
                print("Clicking expand button to re-open sidebar...")
                await expand_btn.click()
                await page.wait_for_timeout(1500)
                await page.screenshot(path="auditoria_tema/mobile_after_expand_click.png")

        await b.close()

if __name__ == "__main__":
    asyncio.run(inspect_mobile_header())
