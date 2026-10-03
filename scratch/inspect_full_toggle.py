import sys
sys.stdout.reconfigure(encoding='utf-8')
import asyncio
from playwright.async_api import async_playwright

async def inspect_dom():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome", headless=True)
        page = await b.new_page(viewport={"width": 1400, "height": 900})
        await page.goto("http://localhost:8501/", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # 1. Desktop - Sidebar OPEN
        print("--- DESKTOP: SIDEBAR OPEN ---")
        collapse_container = page.locator('[data-testid="stSidebarCollapseButton"]').first
        if await collapse_container.count() > 0:
            html = await collapse_container.evaluate("el => el.outerHTML")
            print("stSidebarCollapseButton HTML:\n", html)
            styles = await collapse_container.evaluate("""el => {
                const s = window.getComputedStyle(el);
                const btn = el.querySelector('button') || el;
                const bs = window.getComputedStyle(btn);
                return {
                    container_vis: s.visibility,
                    container_opacity: s.opacity,
                    container_display: s.display,
                    btn_bg: bs.backgroundColor,
                    btn_color: bs.color,
                    btn_border: bs.border,
                    btn_box_shadow: bs.boxShadow,
                    btn_vis: bs.visibility,
                    btn_opacity: bs.opacity
                };
            }""")
            print("Desktop Collapse button computed styles:\n", styles)

        # Move mouse away to 500, 500
        await page.mouse.move(500, 500)
        await page.wait_for_timeout(1000)
        await page.screenshot(path="auditoria_tema/desktop_sidebar_open_unhovered.png")

        # Click collapse button to close sidebar on desktop
        btn_collapse = page.locator('[data-testid="stSidebarCollapseButton"] button').first
        if await btn_collapse.count() > 0:
            await btn_collapse.click()
            await page.wait_for_timeout(1000)
            print("--- DESKTOP: SIDEBAR COLLAPSED ---")
            expand_btn = page.locator('button[data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapsedControl"] button').first
            if await expand_btn.count() > 0:
                html = await expand_btn.evaluate("el => el.outerHTML")
                print("stExpandSidebarButton HTML:\n", html)
                styles = await expand_btn.evaluate("""el => {
                    const bs = window.getComputedStyle(el);
                    return {
                        btn_vis: bs.visibility,
                        btn_opacity: bs.opacity,
                        btn_display: bs.display,
                        btn_bg: bs.backgroundColor,
                        btn_color: bs.color,
                        btn_border: bs.border,
                        btn_box_shadow: bs.boxShadow
                    };
                }""")
                print("Desktop Expand button computed styles:\n", styles)
            await page.mouse.move(500, 500)
            await page.screenshot(path="auditoria_tema/desktop_sidebar_collapsed_unhovered.png")

        # 2. Mobile view (390 x 844 - iPhone / standard mobile)
        print("\n--- MOBILE VIEW (390 x 844) ---")
        await page.set_viewport_size({"width": 390, "height": 844})
        await page.reload(wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # Mobile starts collapsed by default in Streamlit
        expand_mobile = page.locator('button[data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapsedControl"] button').first
        print("Mobile expand button count:", await expand_mobile.count())
        if await expand_mobile.count() > 0:
            box = await expand_mobile.bounding_box()
            print("Mobile expand button bounding box:", box)
            styles = await expand_mobile.evaluate("""el => {
                const bs = window.getComputedStyle(el);
                return {
                    btn_vis: bs.visibility,
                    btn_opacity: bs.opacity,
                    btn_display: bs.display,
                    btn_bg: bs.backgroundColor,
                    btn_color: bs.color,
                    btn_border: bs.border,
                    btn_box_shadow: bs.boxShadow,
                    zIndex: bs.zIndex
                };
            }""")
            print("Mobile expand button styles:\n", styles)
            await page.screenshot(path="auditoria_tema/mobile_sidebar_collapsed.png")

            # Click it to OPEN the sidebar on mobile!
            await expand_mobile.click()
            await page.wait_for_timeout(1500)
            print("Mobile sidebar opened!")

            collapse_mobile = page.locator('[data-testid="stSidebarCollapseButton"] button').first
            if await collapse_mobile.count() > 0:
                box_c = await collapse_mobile.bounding_box()
                print("Mobile collapse button bounding box:", box_c)
                styles_c = await collapse_mobile.evaluate("""el => {
                    const bs = window.getComputedStyle(el);
                    return {
                        btn_vis: bs.visibility,
                        btn_opacity: bs.opacity,
                        btn_display: bs.display,
                        btn_bg: bs.backgroundColor,
                        btn_color: bs.color,
                        btn_border: bs.border,
                        btn_box_shadow: bs.boxShadow
                    };
                }""")
                print("Mobile collapse button styles:\n", styles_c)
            await page.screenshot(path="auditoria_tema/mobile_sidebar_open.png")

            # Check Estudiantes (DEMO) navigation
            est_nav = page.locator('text=Estudiantes (DEMO)')
            print("Estudiantes (DEMO) option visible in mobile menu?", await est_nav.count() > 0)
            if await est_nav.count() > 0:
                await est_nav.first.click()
                await page.wait_for_timeout(2000)
                await page.screenshot(path="auditoria_tema/mobile_estudiantes_demo.png")

        await b.close()

if __name__ == "__main__":
    asyncio.run(inspect_dom())
