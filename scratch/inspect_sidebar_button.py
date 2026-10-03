import sys
sys.stdout.reconfigure(encoding='utf-8')
import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome", headless=True)
        page = await b.new_page(viewport={"width": 1400, "height": 900})
        await page.goto("http://localhost:8501/", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        print("=== 1. DESKTOP VIEW ===")
        # Look for buttons in header and sidebar
        collapse_btn = page.locator('[data-testid="stSidebarCollapseButton"], [data-testid="stSidebar"] button').first
        print("Sidebar button in desktop exists?", await collapse_btn.count())
        if await collapse_btn.count() > 0:
            print("Visible:", await collapse_btn.is_visible())
            print("Bounding box:", await collapse_btn.bounding_box())
            styles = await collapse_btn.evaluate("""el => {
                const s = window.getComputedStyle(el);
                return {
                    color: s.color,
                    background: s.backgroundColor,
                    opacity: s.opacity,
                    visibility: s.visibility,
                    display: s.display,
                    zIndex: s.zIndex
                };
            }""")
            print("Styles:", styles)

        print("\n=== 2. MOBILE VIEW (400px width) ===")
        await page.set_viewport_size({"width": 400, "height": 850})
        await page.wait_for_timeout(2000)

        # On mobile, Streamlit collapses sidebar by default
        collapsed_control = page.locator('[data-testid="collapsedControl"], [data-testid="stSidebarCollapsedControl"]').first
        print("Collapsed control exists?", await collapsed_control.count())
        if await collapsed_control.count() > 0:
            print("Visible:", await collapsed_control.is_visible())
            print("Bounding box:", await collapsed_control.bounding_box())
            styles = await collapsed_control.evaluate("""el => {
                const s = window.getComputedStyle(el);
                const btn = el.querySelector('button') || el;
                const bs = window.getComputedStyle(btn);
                return {
                    el_display: s.display,
                    el_visibility: s.visibility,
                    el_opacity: s.opacity,
                    el_zIndex: s.zIndex,
                    btn_color: bs.color,
                    btn_bg: bs.backgroundColor,
                    btn_opacity: bs.opacity
                };
            }""")
            print("Styles of collapsed control:", styles)

        # Look at all buttons on mobile
        all_buttons = await page.locator('button').all()
        print(f"Total buttons on mobile: {len(all_buttons)}")
        for i, btn in enumerate(all_buttons):
            label = await btn.get_attribute('aria-label')
            testid = await btn.get_attribute('data-testid')
            text = (await btn.inner_text()).strip()
            vis = await btn.is_visible()
            box = await btn.bounding_box()
            if vis:
                print(f"Button {i}: label={label!r}, testid={testid!r}, text={text!r}, box={box}")

        await b.close()

if __name__ == "__main__":
    asyncio.run(inspect())
