import sys
sys.stdout.reconfigure(encoding='utf-8')
import asyncio
from playwright.async_api import async_playwright

async def run_full_mobile_audit():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome", headless=True)

        # ---------------------------------------------------------
        # 1. MOBILE AUDIT (390 x 844)
        # ---------------------------------------------------------
        print("=== 1. MOBILE INITIAL LOAD (390 x 844) ===")
        page = await b.new_page(viewport={"width": 390, "height": 844})
        await page.goto("http://localhost:8501/", wait_until="networkidle")
        await page.wait_for_timeout(3500)

        # Confirm old JS banner is completely GONE
        banner = page.locator('#apocuna-hub-banner')
        print("Is old #apocuna-hub-banner in DOM?", await banner.count() > 0)
        assert await banner.count() == 0, "Old banner should be removed!"

        # Header check
        header = page.locator('header[data-testid="stHeader"]').first
        print("Header exists?", await header.is_visible())
        h_styles = await header.evaluate("""el => {
            const s = window.getComputedStyle(el);
            const before = window.getComputedStyle(el, '::before');
            return {
                bg: s.backgroundColor,
                borderBottom: s.borderBottom,
                before_content: before.content,
                before_color: before.color,
                before_fontSize: before.fontSize,
                before_fontWeight: before.fontWeight
            };
        }""")
        print("Header styles:", h_styles)

        # Check expand button (Menú pill)
        expand_btn = page.locator('button[data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapsedControl"] button').first
        print("Expand button visible?", await expand_btn.is_visible())
        btn_info = await expand_btn.evaluate("""el => {
            const s = window.getComputedStyle(el);
            const after = window.getComputedStyle(el, '::after');
            return {
                box: el.getBoundingClientRect(),
                bg: s.backgroundColor,
                border: s.border,
                borderRadius: s.borderRadius,
                color: s.color,
                after_content: after.content,
                after_color: after.color,
                after_fontWeight: after.fontWeight
            };
        }""")
        print("Expand button info:", btn_info)

        # Capture mobile home top
        await page.screenshot(path="auditoria_tema/mobile_final_home.png")

        # Scroll down to check typography, button, tabs and cards
        await page.evaluate("() => window.scrollBy(0, 450)")
        await page.wait_for_timeout(500)
        await page.screenshot(path="auditoria_tema/mobile_final_radar_cards.png")

        # Scroll to top and click the Menú pill
        await page.evaluate("() => window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)
        print("Clicking Menú button to open sidebar...")
        await expand_btn.click()
        await page.wait_for_timeout(1500)
        await page.screenshot(path="auditoria_tema/mobile_final_sidebar_open.png")

        # Check collapse button in open sidebar
        collapse_btn = page.locator('[data-testid="stSidebarCollapseButton"] button').first
        print("Collapse button visible in sidebar?", await collapse_btn.is_visible())

        # Click Estudiantes (DEMO) in the sidebar
        iframe = page.frame_locator('iframe').first
        est_opt = iframe.locator('text=Estudiantes (DEMO)')
        if await est_opt.count() > 0:
            print("Clicking 'Estudiantes (DEMO)' in mobile sidebar...")
            await est_opt.click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path="auditoria_tema/mobile_final_estudiantes.png")

        # Click Polity and Policy
        if await est_opt.count() > 0:
            pol_opt = iframe.locator('text=Polity and Policy')
            print("Clicking 'Polity and Policy' in mobile sidebar...")
            await pol_opt.click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path="auditoria_tema/mobile_final_polity.png")

        # ---------------------------------------------------------
        # 2. DESKTOP AUDIT (1400 x 900)
        # ---------------------------------------------------------
        print("\n=== 2. DESKTOP VIEW AUDIT (1400 x 900) ===")
        page_d = await b.new_page(viewport={"width": 1400, "height": 900})
        await page_d.goto("http://localhost:8501/", wait_until="networkidle")
        await page_d.wait_for_timeout(3000)
        await page_d.screenshot(path="auditoria_tema/desktop_final_home.png")
        print("Desktop screenshot captured!")

        await b.close()
        print("\n=== AUDIT COMPLETED SUCCESSFULLY! ===")

if __name__ == "__main__":
    asyncio.run(run_full_mobile_audit())
