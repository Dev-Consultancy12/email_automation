import asyncio
from playwright.async_api import async_playwright

async def debug():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = await context.new_page()
        
        print("Fetching YC...")
        await page.goto("https://www.ycombinator.com/companies/airbnb", timeout=60000)
        await asyncio.sleep(5)
        html = await page.content()
        with open("yc_debug.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        print("Fetching Product Hunt...")
        await page.goto("https://www.producthunt.com", timeout=60000)
        await asyncio.sleep(5)
        html = await page.content()
        with open("ph_debug.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        await browser.close()
        print("Done! Wrote yc_debug.html and ph_debug.html")

if __name__ == "__main__":
    asyncio.run(debug())
