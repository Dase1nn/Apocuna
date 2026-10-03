import sys
sys.stdout.reconfigure(encoding='utf-8')
import asyncio
from playwright.async_api import async_playwright

async def audit_all_mobile():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome", headless=True)
        # Standard mobile viewport (iPhone 14 / modern Android: 390 x 844)
        page = await b.new_page(viewport={"width": 390, "height": 844})
        await page.goto("http://localhost:8501/", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # 1. Audit Header & Expand button visibility
        print("=== 1. AUDIT MOBILE HEADER & MENU TOGGLE ===")
        banner = page.locator('#apocuna-hub-banner')
        print("Is #apocuna-hub-banner in DOM?", await banner.count() > 0)
        if await banner.count() > 0:
            box_b = await banner.bounding_box()
            print("Banner bounding box:", box_b)
            styles_b = await banner.evaluate("""el => {
                const s = window.getComputedStyle(el);
                return {
                    pos: s.position, top: s.top, left: s.left, right: s.right,
                    width: s.width, height: s.height, bg: s.backgroundColor,
                    backdrop: s.backdropFilter, zIndex: s.zIndex, pointerEvents: s.pointerEvents
                };
            }""")
            print("Banner computed styles:", styles_b)

        expand_btn = page.locator('button[data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapsedControl"] button').first
        print("Expand button count:", await expand_btn.count())
        if await expand_btn.count() > 0:
            box_e = await expand_btn.bounding_box()
            vis_e = await expand_btn.is_visible()
            print("Expand button visible?", vis_e, "Box:", box_e)
            top_el = await page.evaluate(f"""() => {{
                const el = document.elementFromPoint({box_e['x'] + 10}, {box_e['y'] + 10});
                return el ? el.outerHTML.substring(0, 150) : 'none';
            }}""")
            print("Element directly above expand button:", top_el)

        # 2. Check overflow and font sizing on Inicio
        print("\n=== 2. AUDIT INICIO PAGE SIZING & OVERFLOW ===")
        # Check horizontal overflow
        scroll_w = await page.evaluate("() => document.documentElement.scrollWidth")
        client_w = await page.evaluate("() => document.documentElement.clientWidth")
        print(f"Viewport width: {client_w}, Scroll width: {scroll_w}. Horizontal overflow: {scroll_w > client_w}")

        await page.screenshot(path="auditoria_tema/mobile_audit_inicio_top.png")
        await page.evaluate("() => window.scrollBy(0, 600)")
        await page.wait_for_timeout(500)
        await page.screenshot(path="auditoria_tema/mobile_audit_inicio_middle.png")
        await page.evaluate("() => window.scrollBy(0, 600)")
        await page.wait_for_timeout(500)
        await page.screenshot(path="auditoria_tema/mobile_audit_inicio_cards.png")

        # 3. Test Sidebar open on mobile
        print("\n=== 3. AUDIT SIDEBAR OPEN ON MOBILE ===")
        if await expand_btn.count() > 0 and await expand_btn.is_visible():
            await expand_btn.click()
            await page.wait_for_timeout(1500)
            await page.screenshot(path="auditoria_tema/mobile_audit_sidebar_open.png")

            # Check sidebar width and collapse button
            sidebar = page.locator('[data-testid="stSidebar"]').first
            s_box = await sidebar.bounding_box()
            print("Sidebar box when open:", s_box)

            collapse_btn = page.locator('[data-testid="stSidebarCollapseButton"] button').first
            print("Collapse button visible in open sidebar?", await collapse_btn.is_visible())
            if await collapse_btn.is_visible():
                c_box = await collapse_btn.bounding_box()
                print("Collapse button box:", c_box)

        await b.close()

if __name__ == "__main__":
    asyncio.run(audit_all_mobile())
