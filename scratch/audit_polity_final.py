import sys
sys.stdout.reconfigure(encoding='utf-8')
import asyncio
from playwright.async_api import async_playwright

async def audit():
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=True)
        page = await browser.new_page(viewport={"width": 1600, "height": 1100})
        print("Navigating to http://localhost:8501/...")
        await page.goto("http://localhost:8501/", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # Click Polity and Policy in option_menu iframe
        frame = [f for f in page.frames if 'streamlit_option_menu' in f.url][0]
        polity_btn = frame.locator('text="Polity and Policy"').first
        await polity_btn.click()
        print("Clicked Polity and Policy!")
        await page.wait_for_timeout(3000)

        # Inspect cards (class is .fuente-card)
        card1 = page.locator('.fuente-card:has-text("Boletines de Normas Legales")').first
        card2 = page.locator('.fuente-card:has-text("Gestión Pública (PCM)")').first

        print("\n--- CARD 1 (Boletines de Normas Legales) ---")
        print("Visible:", await card1.is_visible())
        c1_text = await card1.inner_text()
        print("Inner text:\n", c1_text)
        c1_links = await card1.locator('a').all()
        for l in c1_links:
            print("Link text:", await l.inner_text(), "href:", await l.get_attribute("href"))

        print("\n--- CARD 2 (Gestión Pública PCM) ---")
        print("Visible:", await card2.is_visible())
        c2_text = await card2.inner_text()
        print("Inner text:\n", c2_text)
        c2_links = await card2.locator('a').all()
        for l in c2_links:
            print("Link text:", await l.inner_text(), "href:", await l.get_attribute("href"))

        # Anchor icons
        anchors = await page.locator('.fuente-card a[href^="#"], .fuente-card [data-testid="stHeaderActionElements"]').all()
        visible_anchors = [a for a in anchors if await a.is_visible()]
        print(f"\nVisible anchor icons in cards: {len(visible_anchors)}")

        # Screenshot Dark Mode
        dark_path = "C:/Users/Gaston Silva/.gemini/antigravity-ide/brain/629ccd83-c5a0-418a-a3f9-cd68c91b4f66/polity_cards_dark.png"
        await page.screenshot(path=dark_path)
        print(f"Saved {dark_path}")

        # Open Streamlit Settings to change to Light theme
        print("\nSwitching to Light theme...")
        main_menu = page.locator('[data-testid="stMainMenu"] button, #MainMenu button, button[aria-label="Main menu"]').first
        if await main_menu.is_visible():
            await main_menu.click()
            await page.wait_for_timeout(800)
            settings_item = page.locator('[role="menuitem"]:has-text("Settings"), span:has-text("Settings")').first
            if await settings_item.is_visible():
                await settings_item.click()
                await page.wait_for_timeout(1000)
                
                # Check selectbox for theme
                theme_dropdown = page.locator('div[role="dialog"] [data-baseweb="select"]').first
                if await theme_dropdown.is_visible():
                    await theme_dropdown.click()
                    await page.wait_for_timeout(500)
                    light_option = page.locator('li[role="option"]:has-text("Light"), [role="option"]:has-text("Light")').first
                    if await light_option.is_visible():
                        await light_option.click()
                        await page.wait_for_timeout(1500)
                        print("Selected Light theme!")
                
                # Close modal
                close_modal = page.locator('div[role="dialog"] button[aria-label="Close"]').first
                if await close_modal.is_visible():
                    await close_modal.click()
                    await page.wait_for_timeout(1000)

        # Screenshot Light Mode
        light_path = "C:/Users/Gaston Silva/.gemini/antigravity-ide/brain/629ccd83-c5a0-418a-a3f9-cd68c91b4f66/polity_cards_light.png"
        await page.screenshot(path=light_path)
        print(f"Saved {light_path}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(audit())
