import asyncio
from playwright.async_api import async_playwright
import os
import sys

async def main():
    async with async_playwright() as p:
        user_data_dir = os.path.join(os.getcwd(), "chrome_data")
        os.makedirs(user_data_dir, exist_ok=True)
        
        # Args to enable CDP and stealth-like behavior
        args = [
            "--remote-debugging-port=9222",
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-infobars",
            "--start-maximized",
            "--disable-extensions",
            "--window-position=0,0",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-features=IsolateOrigins,site-per-process",
            "--use-fake-ui-for-media-stream",
            "--exclude-switches=enable-automation"
        ]
        
        # Latest Chrome User Agent (Windows 10)
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"

        print("===================================================")
        print("   SHARED BROWSER SERVER (Port 9222)")
        print("===================================================")
        print("Launching Chrome...")
        
        try:
            context = await p.chromium.launch_persistent_context(
                user_data_dir,
                headless=False,
                args=args,
                viewport=None, # Allow window to be resized freely
                accept_downloads=True,
                user_agent=user_agent,
                ignore_default_args=["--enable-automation"],
                # stealth=True # Note: persistent context doesn't support 'stealth' param directly in basic playwright, 
                # but we use playwright-stealth in workers.
            )
            
            print("Browser Running.")
            print("Keep this window OPEN.")
            print("Workers will connect to this instance.")
            print("===================================================")
            
            # Open a status page
            if not context.pages:
                page = await context.new_page()
            else:
                page = context.pages[0]
                
            await page.goto("about:blank")
            await page.evaluate("document.body.innerHTML = '<h1>Lead Intelligence Browser Server</h1><p>Running on port 9222. Do not close.</p>'")
            
            # Keep alive forever
            await asyncio.Future()
            
        except Exception as e:
            print(f"Error launching browser: {e}")
            print("Check if another Chrome instance is already using 'chrome_data' or port 9222.")
            input("Press Enter to exit...")

if __name__ == "__main__":
    try:
        # Check if port 9222 is in use? Playwright will fail if so.
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
