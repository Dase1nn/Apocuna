import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=True)
        page = await browser.new_page()
        await page.goto("http://localhost:8501/", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        frames = page.frames
        print(f"Total frames: {len(frames)}")
        for idx, f in enumerate(frames):
            print(f"Frame {idx}: name='{f.name}', url='{f.url}'")
            try:
                text = await f.locator('body').inner_text()
                print(f"  Frame {idx} text preview: {text[:100]!r}")
            except Exception as e:
                print(f"  Frame {idx} error: {e}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect())
