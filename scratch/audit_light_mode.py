import sys
sys.stdout.reconfigure(encoding='utf-8')
import asyncio
from playwright.async_api import async_playwright

async def audit_light_mode():
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=True)
        page = await browser.new_page(viewport={"width": 1600, "height": 1100})
        await page.goto("http://localhost:8501/", wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # Click Polity and Policy
        frame = [f for f in page.frames if 'streamlit_option_menu' in f.url][0]
        polity_btn = frame.locator('text="Polity and Policy"').first
        await polity_btn.click()
        await page.wait_for_timeout(2500)

        # Set color-scheme: light on document
        await page.evaluate("""() => {
            document.documentElement.style.colorScheme = 'light';
            document.body.style.colorScheme = 'light';
            const main = document.querySelector('.stApp');
            if (main) {
                main.style.backgroundColor = '#FFFFFF';
                main.style.color = '#0F172A';
            }
        }""")
        await page.wait_for_timeout(1000)

        light_screenshot = "C:/Users/Gaston Silva/.gemini/antigravity-ide/brain/629ccd83-c5a0-418a-a3f9-cd68c91b4f66/polity_cards_light_evaluated.png"
        await page.screenshot(path=light_screenshot)
        print(f"Saved light evaluated screenshot to {light_screenshot}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(audit_light_mode())
