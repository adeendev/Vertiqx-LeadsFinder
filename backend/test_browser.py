import asyncio
import os
from services.scraper import GoogleMapsScraper

# Force load env to be sure
from dotenv import load_dotenv
load_dotenv()

async def test():
    print("🚀 Starting Standalone Browser Test...", flush=True)
    print(f"ENV HEADLESS_MODE: {os.getenv('HEADLESS_MODE')}", flush=True)
    
    # Force headless=False to test GUI
    scraper = GoogleMapsScraper(headless=False)
    
    print("Browser launching...", flush=True)
    await scraper.start()
    print("Browser launched! Navigating to Google...", flush=True)
    await scraper.page.goto("https://www.google.com")
    print("Navigated. Waiting 10 seconds...", flush=True)
    await asyncio.sleep(10)
    await scraper.stop()
    print("Test Complete.", flush=True)

if __name__ == "__main__":
    asyncio.run(test())
