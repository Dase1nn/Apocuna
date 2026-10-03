import asyncio
from playwright.async_api import async_playwright

async def audit():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            channel="chrome",
            headless=True
        )
        context = await browser.new_context(
            viewport={"width": 1600, "height": 1100}
        )
        page = await context.new_page()
        print("Navigating to http://localhost:8501/...")
        await page.goto("http://localhost:8501/", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # Find option menu in iframe
        print("Clicking Polity and Policy in option_menu iframe...")
        frame = page.frame_locator('iframe[title="streamlit_option_menu.option_menu"]').first
        polity_item = frame.locator('span:has-text("Polity and Policy")')
        await polity_item.click()
        await page.wait_for_timeout(3000)

        # Check expander if needed
        expander = page.locator('text="1. Actualización normativa y regulatoria"').first
        if await expander.is_visible():
            # Check if cards are already visible
            card1 = page.locator('.card:has-text("Boletines de Normas Legales")').first
            if not await card1.is_visible():
                print("Clicking expander...")
                await expander.click()
                await page.wait_for_timeout(1500)

        # Read cards details
        card1 = page.locator('.card:has-text("Boletines de Normas Legales")').first
        card2 = page.locator('.card:has-text("Gestión Pública (PCM)")').first

        print("=== CARD 1 ===")
        print("Visible:", await card1.is_visible())
        print("Text:", await card1.inner_text())
        btn1 = card1.locator('a, button, span')
        print("Card 1 links:", await card1.locator('a').all_inner_texts(), "hrefs:", [await a.get_attribute('href') for a in await card1.locator('a').all()])

        print("=== CARD 2 ===")
        print("Visible:", await card2.is_visible())
        print("Text:", await card2.inner_text())
        print("Card 2 links:", await card2.locator('a').all_inner_texts(), "hrefs:", [await a.get_attribute('href') for a in await card2.locator('a').all()])

        # Anchor icons check
        anchors = await page.locator('.card a[href^="#"], .card [data-testid="stHeaderActionElements"]').all()
        visible_anchors = [a for a in anchors if await a.is_visible()]
        print(f"Visible anchor icons in cards: {len(visible_anchors)}")

        # Screenshot Dark Mode
        dark_path = "C:/Users/Gaston Silva/.gemini/antigravity-ide/brain/629ccd83-c5a0-418a-a3f9-cd68c91b4f66/polity_dark_verified.png"
        await page.screenshot(path=dark_path, full_page=False)
        print(f"Dark mode screenshot saved: {dark_path}")

        # Switch to Light Mode via Streamlit UI
        print("Switching to light theme via Streamlit settings...")
        # Close any toasts or help dialogs
        close_btn = page.locator('button:has-text("Don\'t show again"), [aria-label="Close"]').first
        if await close_btn.is_visible():
            await close_btn.click()
            await page.wait_for_timeout(500)

        # Open main menu
        menu_btn = page.locator('button[aria-label="Main menu"], [data-testid="stMainMenu"] button, #MainMenu button').first
        if await menu_btn.is_visible():
            await menu_btn.click()
            await page.wait_for_timeout(800)
            settings_item = page.locator('[role="menuitem"]:has-text("Settings"), button:has-text("Settings")').first
            if await settings_item.is_visible():
                await settings_item.click()
                await page.wait_for_timeout(1000)
                
                # In settings modal, select Light theme
                # Usually there's a theme selector
                theme_select = page.locator('div[role="dialog"] div[data-baseweb="select"]').first
                if await theme_select.is_visible():
                    await theme_select.click()
                    await page.wait_for_timeout(500)
                    light_option = page.locator('[role="option"]:has-text("Light")').first
                    if await light_option.is_visible():
                        await light_option.click()
                        await page.wait_for_timeout(1000)
                
                # Close modal
                modal_close = page.locator('div[role="dialog"] button[aria-label="Close"]').first
                if await modal_close.is_visible():
                    await modal_close.click()
                    await page.wait_for_timeout(1000)

        light_path = "C:/Users/Gaston Silva/.gemini/antigravity-ide/brain/629ccd83-c5a0-418a-a3f9-cd68c91b4f66/polity_light_verified.png"
        await page.screenshot(path=light_path, full_page=False)
        print(f"Light mode screenshot saved: {light_path}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(audit())
