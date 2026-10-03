import sys
sys.stdout.reconfigure(encoding='utf-8')
import asyncio
from playwright.async_api import async_playwright

async def audit_light():
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=True)
        page = await browser.new_page(viewport={"width": 1600, "height": 1100})
        await page.goto("http://localhost:8501/", wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # Inject Streamlit light theme in localStorage and reload
        await page.evaluate("""() => {
            window.localStorage.setItem("stActiveTheme", JSON.stringify({
                "base": "light",
                "primaryColor": "#29B5E8",
                "backgroundColor": "#FFFFFF",
                "secondaryBackgroundColor": "#F0F2F6",
                "textColor": "#31333F",
                "bodyFont": "Source Sans Pro"
            }));
            window.localStorage.setItem("stTheme", "light");
        }""")
        await page.reload(wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # Click Polity and Policy
        frame = [f for f in page.frames if 'streamlit_option_menu' in f.url][0]
        polity_btn = frame.locator('text="Polity and Policy"').first
        await polity_btn.click()
        await page.wait_for_timeout(3000)

        light_path = "C:/Users/Gaston Silva/.gemini/antigravity-ide/brain/629ccd83-c5a0-418a-a3f9-cd68c91b4f66/polity_cards_light_real.png"
        await page.screenshot(path=light_path)
        print(f"Saved {light_path}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(audit_light())
