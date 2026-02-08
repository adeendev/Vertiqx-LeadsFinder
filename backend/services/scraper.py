import asyncio
import random
import time
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import os
from dotenv import load_dotenv

load_dotenv()

from urllib.parse import urlparse, parse_qs

from services.browser_manager import BrowserManager

class GoogleMapsScraper:
    def __init__(self, headless=None, status_callback=None):
        # Load from env if not provided
        if headless is None:
            self.headless = os.getenv("HEADLESS_MODE", "True").lower() == "true"
        else:
            self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        self.status_callback = status_callback
        self.is_shared = False

    def log(self, message, type="info"):
        logger.info(message)
        if self.status_callback:
            self.status_callback(message, type)

    async def start(self):
        logger.info("Starting Playwright...")
        self.playwright = await async_playwright().start()
        logger.info(f"Acquiring Browser Context...")
        
        try:
            self.context, self.browser, self.is_shared = await BrowserManager.get_browser_context(self.playwright)
            
            if self.is_shared:
                logger.info("Connected to Shared Browser Server.")
            else:
                logger.info("Launched Standalone Browser.")

            # Get or create page
            if self.context.pages:
                # If shared, we might want to create a NEW page to avoid messing with existing ones?
                # But 'leads taker' (searcher) is the main task.
                # Let's create a new page for the search to be safe and clean.
                self.page = await self.context.new_page()
            else:
                self.page = await self.context.new_page()
            
            # Apply stealth
            stealth = Stealth()
            await stealth.apply_stealth_async(self.page)
            
            logger.info("Browser Ready")
            
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            raise e

    async def stop(self):
        # If shared, do NOT close the context or browser. Just close the page.
        if self.is_shared:
            logger.info("Closing search page (Shared Browser remains active)...")
            if self.page:
                await self.page.close()
            # Do NOT stop playwright if we want to keep using it? 
            # Actually, we started playwright in this process. We should stop it?
            # If we stop playwright, the CDP connection closes. The remote browser stays open.
            await self.playwright.stop()
        else:
            logger.info("Closing standalone browser...")
            if self.context:
                await self.context.close()
            await self.playwright.stop()

    async def search_business(self, keyword, location, limit=120, on_lead_found=None):
        MAX_SCROLLS = 30
        
        query = f"{keyword} {location}"
        self.log(f"Searching for: {query} (Limit: {limit})")
        
        # 1. Go to Google Maps Home
        try:
            await self.page.goto("https://www.google.com/maps", timeout=60000)
            await self.random_delay(3, 6)
            
            # CAPTCHA Detection
            is_captcha = False
            try:
                page_title = await self.page.title()
                if "sorry" in page_title.lower() or "captcha" in page_title.lower():
                    is_captcha = True
            except: pass

            if not is_captcha:
                if await self.page.locator('text="Before you continue to Google"').count() > 0 or \
                   await self.page.locator('form[action*="Captcha"]').count() > 0 or \
                   await self.page.locator('iframe[src*="google.com/recaptcha"]').count() > 0 or \
                   await self.page.locator('text="Our systems have detected unusual traffic"').count() > 0:
                    is_captcha = True

            if is_captcha:
                self.log("CAPTCHA / Unusual Traffic detected! Pausing for manual interaction...", "warning")
                print("\n" + "="*50)
                print("!!! CAPTCHA DETECTED !!!")
                print("Please solve the CAPTCHA in the browser window manually.")
                print("The system will resume automatically once solved.")
                print("="*50 + "\n")
                
                # Wait for user to solve it manually
                # We check every second if the search box appears OR if results appear (indicating success)
                # Wait up to 10 minutes (600 seconds)
                for i in range(600):
                    # Check for Search Box
                    search_box_visible = False
                    if await self.page.locator('input#searchboxinput').count() > 0 or \
                       await self.page.locator('input[name="q"]').count() > 0:
                        search_box_visible = True
                    
                    # Check for Feed/Results
                    results_visible = False
                    if await self.page.locator('div[role="feed"]').count() > 0 or \
                       await self.page.locator('.hfpxzc').count() > 0:
                        results_visible = True

                    # Check URL (if we are back on maps/search and not sorry)
                    url = self.page.url
                    url_ok = "google.com/maps" in url or "google.com/search" in url
                    url_bad = "sorry" in url or "captcha" in url

                    if (search_box_visible or results_visible) and url_ok and not url_bad:
                        self.log("CAPTCHA solved! Resuming...", "success")
                        print("CAPTCHA SOLVED - RESUMING...")
                        await self.random_delay(2, 4) # Extra buffer
                        break
                    
                    if i % 10 == 0:
                        self.log(f"Waiting for CAPTCHA solution... ({i}s)", "warning")
                        
                    await asyncio.sleep(1)
            
            # Check for consent dialog (Before you continue to Google Maps)
            try:
                # Look for "Accept all" or "Reject all" buttons
                # Common aria-labels or text
                consent_btn = self.page.locator('button[aria-label="Accept all"]')
                if await consent_btn.count() > 0:
                     self.log("Consent dialog detected. Clicking 'Accept all'...")
                     await consent_btn.click()
                     await self.random_delay(2, 4)
                else:
                    # Try text based
                    text_btn = self.page.get_by_text("Accept all", exact=True)
                    if await text_btn.count() > 0:
                        self.log("Consent dialog detected (text). Clicking...")
                        await text_btn.click()
                        await self.random_delay(2, 4)
            except Exception as e:
                self.log(f"Consent check warning: {e}", "warning")
            
            # 2. Type keyword + city
            # Wait for search box to be ready
            try:
                search_box = self.page.locator("input#searchboxinput")
                await search_box.wait_for(state="visible", timeout=10000)
                await search_box.fill(query)
                await self.random_delay(1, 2)
            except:
                self.log("Search box not found by ID. Trying generic input...", "warning")
                search_box = self.page.locator('input[name="q"]') # Fallback
                await search_box.wait_for(state="visible", timeout=10000)
                await search_box.fill(query)
                await self.random_delay(1, 2)
            
            # 3. Press Enter
            await self.page.keyboard.press("Enter")
            
            # Click search button as backup
            try:
                search_btn = self.page.locator("button#searchbox-searchbutton")
                if await search_btn.count() > 0:
                    await search_btn.click()
            except: pass
            
            # 4. Wait 8-12 sec
            self.log("Waiting for results to load...")
            await self.random_delay(10, 15)
            
        except Exception as e:
            self.log(f"Navigation/Search failed: {e}", "error")
            return []

        try:
            await self.page.wait_for_selector('div[role="feed"]', timeout=30000)
        except:
            self.log("Could not find feed, checking if single result or error...", "warning")
            pass
        
        self.log(f"Starting extraction loop (Limit: {limit} SAVED leads, Max Scrolls: 30)")
        
        saved_count = 0
        current_index = 0
        scroll_count = 0
        
        # Keep track of processed indices to avoid re-processing
        # Note: DOM elements might change, so we rely on finding all elements again
        # but skipping the first 'processed_count' items is risky if list refreshes.
        # Safer strategy: Scroll to load enough, then process. 
        # But user wants "Scroll results panel slowly" then "Extract businesses one by one".
        # We will try to maintain the list.
        
        while saved_count < limit:
            # Scroll Phase (Load more if needed)
            # We check if we have enough elements loaded to cover the next batch
            current_elements_count = await self.page.locator('.hfpxzc').count()
            
            if current_elements_count <= current_index and scroll_count < MAX_SCROLLS:
                self.log(f"Scrolling... (Scroll {scroll_count+1}/{MAX_SCROLLS})")
                try:
                    await self.page.evaluate('if(document.querySelector("div[role=\'feed\']")) document.querySelector("div[role=\'feed\']").scrollBy(0, 5000)')
                    await self.random_delay(3, 6) # Scroll slowly
                    scroll_count += 1
                except Exception as e:
                    self.log(f"Scroll failed: {e}", "error")
            elif current_elements_count <= current_index and scroll_count >= MAX_SCROLLS:
                 self.log("MAX_SCROLLS limit reached. Stopping search.", "warning")
                 break
            
            # Re-fetch elements
            elements = await self.page.locator('.hfpxzc').all()
            total_available = len(elements)
            
            if current_index >= total_available:
                # No new elements found after scroll
                if scroll_count < MAX_SCROLLS:
                    # Try scrolling again
                    continue
                else:
                    break
            
            # Extract One by One
            # Process next available element
            try:
                el = elements[current_index]
                
                # Scroll to it
                await el.scroll_into_view_if_needed()
                
                # Get name from the result item directly (more reliable)
                try:
                    name_from_list = await el.get_attribute('aria-label')
                except:
                    name_from_list = None
                
                # Click it
                await el.click()
                
                # Wait for details
                try:
                    await self.page.wait_for_selector('div[role="main"] h1', timeout=5000)
                except:
                    self.log(f"Details panel didn't load for item {processed_count}", "warning")
                    processed_count += 1
                    continue
                
                await self.random_delay(2, 5)
                
                details = await self.extract_details(name_hint=name_from_list)
                if details and details['business_name'] and "Results" not in details['business_name']:
                    # We found a valid lead structure, let's try to save it.
                    # IMPORTANT: We need to know if it was a duplicate or not to increment 'processed_count'
                    # But the callback is async and we don't have a direct return value easily unless we change the interface.
                    # For now, let's keep the existing logic: we processed this *slot* in the list.
                    # BUT the user wants 120 *saved* leads. 
                    # If we skip duplicates, we are still consuming 'processed_count' (the index in the list).
                    # If we don't increment 'processed_count', we will loop forever on the same index unless we move the index pointer (i) separately.
                    
                    # Correction: 'processed_count' here is actually acting as 'saved_count' limit check, 
                    # BUT it is ALSO used as the index `elements[processed_count]`. This is the BUG.
                    # We are using one variable for two things: 
                    # 1. Which element to click (index)
                    # 2. How many leads we have found (limit check)
                    
                    # We need to separate them.
                    # Let's rename 'processed_count' to 'current_index' for the loop, and add a 'saved_count'.
                    # Wait, the loop structure is `while processed_count < limit`. 
                    # Refactoring loop structure.
                    
                    result_status = "unknown"
                    if on_lead_found:
                         # We expect on_lead_found to return True if saved, False if duplicate/error
                         result_status = await on_lead_found(details)
                    
                    self.log(f"Extracted ({saved_count + 1}/{limit}): {details['business_name']}")
                    
                    if result_status == True:
                        saved_count += 1
                    
                    # Always move to next element index
                    current_index += 1
                else:
                    self.log(f"Skipping invalid result", "warning")
                    current_index += 1
                    
                # Check Limit based on SAVED count
                if saved_count >= limit:
                    self.log(f"Limit of {limit} SAVED leads reached. Stopping.", "success")
                    break
                    
            except Exception as e:
                self.log(f"Error processing element {current_index}: {e}", "error")
                current_index += 1
                continue
                
        return []

    def clean_google_url(self, url):
        if not url: return None
        
        # Handle Google redirection URLs
        if 'google.com/url' in url or '/url?q=' in url:
            try:
                parsed = urlparse(url)
                query = parse_qs(parsed.query)
                if 'q' in query:
                    return query['q'][0]
            except:
                pass
        
        return url

    async def extract_details(self, name_hint=None):
        try:
            # Use Playwright locators for better reliability
            data = {
                'business_name': name_hint if name_hint else '',
                'address': '',
                'phone': '',
                'website': '',
                'rating': 0.0,
                'reviews': 0
            }
            
            # Name
            # If name_hint is missing or suspicious (e.g. "Sponsored"), try to extract from h1
            if not data['business_name'] or "Sponsored" in data['business_name']:
                 # Iterate through h1s to find the business name, ignoring "Results" and "Sponsored"
                h1s = await self.page.locator('div[role="main"] h1').all()
                for header in h1s:
                    text = await header.inner_text()
                    if not text: continue
                    text = text.strip()
                    
                    # Filter out unwanted strings
                    if "Results" in text: continue
                    if text.lower() == "sponsored": continue
                    
                    data['business_name'] = text
                    break
            
            # If still no name, try aria-label on the main role div
            if not data['business_name']:
                try:
                    main_div = self.page.locator('div[role="main"]')
                    if await main_div.count() > 0:
                        label = await main_div.first.get_attribute('aria-label')
                        if label and "Results" not in label and label.lower() != "sponsored":
                            data['business_name'] = label
                except: pass
            
            # Website - Look for the specific button
            # Usually has data-item-id="authority"
            website_btn = self.page.locator('a[data-item-id="authority"]')
            raw_url = None
            if await website_btn.count() > 0:
                raw_url = await website_btn.get_attribute('href')
            else:
                # Fallback: Find link with "Website" text
                website_btn = self.page.locator('a[aria-label*="Website"]')
                if await website_btn.count() > 0:
                    raw_url = await website_btn.get_attribute('href')
            
            if raw_url:
                data['website'] = self.clean_google_url(raw_url)

            # Phone
            # Look for button with data-item-id starting with "phone"
            phone_btn = self.page.locator('button[data-item-id*="phone"]')
            if await phone_btn.count() > 0:
                aria = await phone_btn.get_attribute('aria-label')
                if aria:
                    data['phone'] = aria.replace('Phone:', '').strip()
            
            # SCROLLING FOR MORE INFO (Web Results / Socials)
            # The user requested to scroll the profile to find related web results or social links.
            try:
                # Scroll the main div
                main_div = self.page.locator('div[role="main"]')
                if await main_div.count() > 0:
                    # Scroll down a few times
                    for _ in range(3):
                        await main_div.evaluate('element => element.scrollBy(0, 500)')
                        await self.random_delay(1, 2)
                    
                    # Look for social links or other websites in the content
                    # Google sometimes lists "Profiles" section with icons
                    # We look for links containing facebook, instagram, linkedin
                    
                    # Get all links in the main div
                    links = await main_div.locator('a[href]').all()
                    
                    social_map = {
                        'facebook.com': 'facebook',
                        'instagram.com': 'instagram',
                        'linkedin.com': 'linkedin'
                    }
                    
                    for link in links:
                        href = await link.get_attribute('href')
                        if not href: continue
                        
                        # Check for socials
                        for domain, key in social_map.items():
                            if domain in href and not data.get(key):
                                data[key] = href
                        
                        # Check for "Web results" (if main website is missing)
                        # Sometimes Google lists "Web results" with links
                        if not data['website'] and href.startswith('http'):
                            # Filter out google/maps links
                            if 'google.com' not in href and 'goo.gl' not in href:
                                # This is a guess, but if we don't have a website, any external link in the profile is a good candidate
                                data['website'] = self.clean_google_url(href)

            except Exception as e:
                # Non-critical failure
                pass

            return data
        except Exception as e:
            self.log(f"Extraction failed: {e}", "error")
            return None

    async def random_delay(self, min_seconds=2, max_seconds=5):
        await asyncio.sleep(random.uniform(min_seconds, max_seconds))