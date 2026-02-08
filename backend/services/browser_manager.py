import os
import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

CDP_URL = "http://localhost:9222"

class BrowserManager:
    @staticmethod
    async def get_browser_context(playwright_instance):
        """
        Attempts to connect to the shared browser via CDP.
        Returns (context, browser_obj, is_shared)
        - context: The BrowserContext to use.
        - browser_obj: The Browser object (if connected via CDP) or None (if persistent context).
        - is_shared: Boolean indicating if we are using the shared server.
        """
        # Try to connect to shared browser with retries
        # Reduced retries for faster feedback
        for i in range(2):
            try:
                print(f"Connecting to shared browser at {CDP_URL} (Attempt {i+1}/2)...")
                browser = await playwright_instance.chromium.connect_over_cdp(CDP_URL)
                
                # Always create a new incognito context to avoid leaking user session/email
                # Do NOT reuse browser.contexts[0] as it might be the user's main logged-in profile
                context = await browser.new_context()
                    
                return context, browser, True
                
            except Exception as e:
                if i == 1:
                    print(f"Connection to shared browser failed: {e}")
                else:
                    await asyncio.sleep(0.5)

        print("Shared browser unreachable. Launching standalone instance (Fallback)...")
            
        # Fallback: Launch persistent context locally
        # Use a unique directory per process to avoid lock contention
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user_data_dir = os.path.join(os.getcwd(), "chrome_data", f"worker_{unique_id}")
        os.makedirs(user_data_dir, exist_ok=True)
        
        args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-infobars",
            "--start-maximized",
            "--disable-extensions",
            "--window-position=0,0",
            "--disable-features=IsolateOrigins,site-per-process",
            "--exclude-switches=enable-automation"
        ]
        
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"

        try:
            context = await playwright_instance.chromium.launch_persistent_context(
                user_data_dir,
                headless=False,
                args=args,
                viewport={'width': 1920, 'height': 1080},
                user_agent=user_agent,
                ignore_default_args=["--enable-automation"]
            )
            return context, None, False
        except Exception as launch_err:
            print(f"Failed to launch standalone browser: {launch_err}")
            print("Likely 'chrome_data' is locked by another process (maybe the browser server is running but unreachable?).")
            raise launch_err
