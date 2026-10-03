import sys
sys.stdout.reconfigure(encoding='utf-8')
import asyncio
from playwright.async_api import async_playwright

async def test_theme_switch():
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=True)
        page = await browser.new_page(viewport={"width": 1600, "height": 1100})
        await page.goto("http://localhost:8501/", wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # Close any toasts or popups
        for b in await page.locator('button:has-text("Don\'t show again")').all():
            if await b.is_visible():
                await b.click()

        # Click top right menu
        menu = page.locator('#MainMenu button, [data-testid="stMainMenu"] button').first
        await menu.click()
        await page.wait_for_timeout(1000)

        # Click settings
        settings = page.locator('li:has-text("Settings"), button:has-text("Settings"), div:has-text("Settings")').last
        await settings.click()
        await page.wait_for_timeout(1000)

        # Print all text in dialog
        dialog = page.locator('div[role="dialog"]').first
        print("Dialog text:\n", await dialog.inner_text())

        # Select light theme: look for selectbox or radio
        select = dialog.locator('div[data-baseweb="select"]').first
        if await select.is_visible():
            await select.click()
            await page.wait_for_timeout(500)
            opt = page.locator('li[role="option"]:has-text("Light")').first
            await opt.click()
            await page.wait_for_timeout(1000)

        # Close dialog
        close_btn = dialog.locator('button[aria-label="Close"]').first
        await close_btn.click()
        await page.wait_for_timeout(1500)

        # Click Polity and Policy
        frame = [f for f in page.frames if 'streamlit_option_menu' in f.url][0]
        polity_btn = frame.locator('text="Polity and Policy"').first
        await polity_btn.click()
        await page.wait_for_timeout(2000)

        light_screenshot = "C:/Users/Gaston Silva/.gemini/antigravity-ide/brain/629ccd83-c5a0-418a-a3f9-cd68c91b4f66/polity_cards_light_switched.png"
        await page.screenshot(path=light_screenshot)
        print(f"Saved light switched screenshot to {light_screenshot}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_theme_switch())
