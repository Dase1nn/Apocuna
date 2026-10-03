import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            channel="chrome",
            headless=True
        )
        # 1. Dark theme context
        context_dark = await browser.new_context(
            viewport={"width": 1600, "height": 1000},
            color_scheme="dark"
        )
        page = await context_dark.new_page()
        print("Navigating to http://localhost:8501/ (Dark mode)...")
        await page.goto("http://localhost:8501/", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # Click Polity and Policy in sidebar
        polity_button = page.locator('span:has-text("Polity and Policy")').first
        if await polity_button.is_visible():
            await polity_button.click()
            print("Clicked Polity and Policy")
            await page.wait_for_timeout(3000)

        # Ensure first expander is open or check cards
        # Check text of cards
        normas_card = page.locator('.card:has-text("Boletines de Normas Legales")').first
        pcm_card = page.locator('.card:has-text("Gestión Pública (PCM)")').first

        if await normas_card.is_visible():
            print("Normas card found!")
            print("Normas card text:", await normas_card.inner_text())
        else:
            # Maybe inside an expander that needs clicking
            expander = page.locator('text=1. Actualización normativa y regulatoria').first
            if await expander.is_visible():
                await expander.click()
                await page.wait_for_timeout(1500)
            if await normas_card.is_visible():
                print("Normas card found after expander click!")
                print("Normas card text:", await normas_card.inner_text())

        if await pcm_card.is_visible():
            print("PCM card found!")
            print("PCM card text:", await pcm_card.inner_text())

        # Check for anchor icons
        anchors = await page.locator('.card a[href^="#"], .card [data-testid="stHeaderActionElements"]').all()
        visible_anchors = []
        for a in anchors:
            if await a.is_visible():
                visible_anchors.append(a)
        print(f"Visible anchor icons in cards: {len(visible_anchors)}")

        # Take screenshot of dark mode
        dark_screenshot_path = "C:/Users/Gaston Silva/.gemini/antigravity-ide/brain/629ccd83-c5a0-418a-a3f9-cd68c91b4f66/polity_dark_audit.png"
        await page.screenshot(path=dark_screenshot_path)
        print(f"Dark mode screenshot saved to {dark_screenshot_path}")

        # 2. Light theme context
        context_light = await browser.new_context(
            viewport={"width": 1600, "height": 1000},
            color_scheme="light"
        )
        page_light = await context_light.new_page()
        # Streamlit settings localStorage or streamlit url params
        await page_light.goto("http://localhost:8501/?theme=light", wait_until="networkidle")
        await page_light.wait_for_timeout(3000)

        polity_button_light = page_light.locator('span:has-text("Polity and Policy")').first
        if await polity_button_light.is_visible():
            await polity_button_light.click()
            await page_light.wait_for_timeout(3000)

        expander_light = page_light.locator('text=1. Actualización normativa y regulatoria').first
        if await expander_light.is_visible():
            # expanders might be collapsed or open
            normas_l = page_light.locator('.card:has-text("Boletines de Normas Legales")').first
            if not await normas_l.is_visible():
                await expander_light.click()
                await page_light.wait_for_timeout(1500)

        light_screenshot_path = "C:/Users/Gaston Silva/.gemini/antigravity-ide/brain/629ccd83-c5a0-418a-a3f9-cd68c91b4f66/polity_light_audit.png"
        await page_light.screenshot(path=light_screenshot_path)
        print(f"Light mode screenshot saved to {light_screenshot_path}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
