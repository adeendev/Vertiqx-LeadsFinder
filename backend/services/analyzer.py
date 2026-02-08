import time
import asyncio
import random
from bs4 import BeautifulSoup
import logging
import difflib
import urllib.parse
import re
from .builder_detector import BuilderDetector
from .email_extractor import EmailExtractor
from database import engine
from sqlmodel import Session, select
from models import Settings
from services.apify_scraper import ApifyService

logger = logging.getLogger(__name__)

class WebsiteAnalyzer:
    def __init__(self):
        self.builder_detector = BuilderDetector()
        self.email_extractor = EmailExtractor()
        
        # Initialize Apify Service and load ignore list from Settings
        self.apify_service = None
        try:
            with Session(engine) as session:
                self.apify_service = ApifyService(session)
                
                # Auto-ignore the user's own email if configured
                settings = session.exec(select(Settings)).all()
                config = {s.key: s.value for s in settings}
                
                if config.get("SMTP_USER"):
                    self.email_extractor.add_ignore(config["SMTP_USER"])
                if config.get("SMTP_FROM"):
                    self.email_extractor.add_ignore(config["SMTP_FROM"])
                    
        except Exception as e: 
            logger.warning(f"Failed to initialize Analyzer dependencies: {e}")

    async def random_delay(self, min_seconds=2.0, max_seconds=5.0):
        """Add a random delay to simulate human behavior"""
        delay = random.uniform(min_seconds, max_seconds)
        logger.debug(f"Sleeping for {delay:.2f}s")
        await asyncio.sleep(delay)

    async def analyze(self, url, page):
        if not url:
            return None

        if not url.startswith('http'):
            url = 'http://' + url

        start_time = time.time()
        try:
            # Random delay before starting
            await self.random_delay(2, 4)

            # Use Playwright page to navigate
            try:
                await page.goto(url, timeout=30000, wait_until='domcontentloaded')
            except Exception as e:
                logger.warning(f"Page load warning for {url}: {e}")
                # Continue if partial load or just proceed to analyze what we have
            
            # Wait a bit for dynamic content if needed
            await self.random_delay(3, 6)
            
            # Simulate human scrolling
            try:
                await page.evaluate("window.scrollBy(0, 300)")
                await self.random_delay(1, 2)
                await page.evaluate("window.scrollBy(0, 300)")
            except: pass
            
            content = await page.content()
            load_time = time.time() - start_time
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Builder Detection
            builder_info = self.builder_detector.detect(content)
            
            # Email Extraction
            emails = self.email_extractor.extract(content)
            primary_email = emails[0] if emails else None
            email_quality = self.email_extractor.rate_quality(primary_email)
            
            # Technical Signals
            has_https = page.url.startswith('https')
            # Check viewport meta
            viewport = await page.query_selector('meta[name="viewport"]')
            has_mobile_viewport = bool(viewport)
            
            # UX Signals
            has_cta = False
            for btn in soup.find_all(['button', 'a']):
                text = btn.text.lower()
                if any(x in text for x in ['contact', 'book', 'call', 'get quote', 'schedule']):
                    has_cta = True
                    break
                    
            # Business Signals
            has_social = False
            facebook_link = None
            instagram_link = None
            linkedin_link = None
            
            social_domains = ['facebook.com', 'instagram.com', 'linkedin.com', 'twitter.com']
            for a in soup.find_all('a', href=True):
                href = a['href']
                if any(d in href for d in social_domains):
                    has_social = True
                
                # Extract Socials
                if 'facebook.com' in href and not facebook_link:
                    if 'sharer' not in href:
                        facebook_link = href
                elif 'instagram.com' in href and not instagram_link:
                    instagram_link = href
                elif 'linkedin.com' in href and not linkedin_link:
                    linkedin_link = href
            
            # Identify Pain Points
            pain_points = []
            
            # 1. Speed
            if load_time > 3.0:
                pain_points.append("Slow Loading Speed (>3s)")
                
            # 2. Security
            if not has_https:
                pain_points.append("Not Secure (No HTTPS)")
                
            # 3. Mobile / UX
            if not has_mobile_viewport:
                pain_points.append("Not Mobile Friendly")
                
            if not has_cta:
                pain_points.append("Missing Call-to-Action")
                
            # 4. SEO
            page_title = await page.title()
            if not page_title or len(page_title) < 10:
                pain_points.append("Bad SEO: Title too short or missing")
            
            meta_desc = await page.query_selector('meta[name="description"]')
            if not meta_desc:
                pain_points.append("Bad SEO: Missing Meta Description")
                
            h1_count = len(soup.find_all('h1'))
            if h1_count == 0:
                pain_points.append("Bad SEO: Missing H1 Tag")
            elif h1_count > 1:
                pain_points.append("Bad SEO: Multiple H1 Tags")

            # Deep SEO Analysis
            # Canonical
            if not soup.find('link', rel='canonical'):
                pain_points.append("SEO: Missing Canonical Tag")
            
            # Open Graph
            og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
            if not og_tags:
                pain_points.append("Social: Missing Open Graph Tags")
                
            # Alt Text
            images = soup.find_all('img')
            # Check for missing alt attribute (alt="" is valid for decorative)
            missing_alt = sum(1 for img in images if not img.has_attr('alt'))
            if images and (missing_alt / len(images) > 0.5):
                pain_points.append(f"Accessibility: {missing_alt} images missing alt text")

            # Structured Data
            json_ld = soup.find('script', type='application/ld+json')
            if not json_ld:
                pain_points.append("SEO: Missing Structured Data (Schema.org)")

            # 5. Performance & Tech
            scripts = soup.find_all('script', src=True)
            if len(scripts) > 25:
                pain_points.append(f"Performance: High script count ({len(scripts)})")
                
            stylesheets = soup.find_all('link', rel='stylesheet')
            if len(stylesheets) > 15:
                pain_points.append(f"Performance: High stylesheet count ({len(stylesheets)})")
                
            # Favicon
            favicon = soup.find('link', rel=lambda x: x and 'icon' in x.lower())
            if not favicon:
                pain_points.append("Branding: Missing Favicon")

            # 6. Content / Contact
            text_content = soup.get_text()
            
            # Text to HTML Ratio
            if len(content) > 0:
                ratio = len(text_content) / len(content)
                if ratio < 0.1:
                    pain_points.append("Performance: Low Text-to-HTML ratio (Code Bloat)")

            word_count = len(text_content.split())
            if word_count < 300:
                pain_points.append("Content: Low word count (Thin Content)")

            if not primary_email:
                pain_points.append("No Email Found")
                
            if not has_social:
                pain_points.append("No Social Media Links")

            return {
                'url': page.url,
                'load_time': load_time,
                'https': has_https,
                'mobile_responsive': has_mobile_viewport,
                'builder': builder_info['builder'],
                'is_ai_builder': builder_info['is_ai'],
                'emails': emails,
                'primary_email': primary_email,
                'email_quality': email_quality,
                'has_cta': has_cta,
                'has_social': has_social,
                'facebook': facebook_link,
                'instagram': instagram_link,
                'linkedin': linkedin_link,
                'title': page_title,
                'pain_points': pain_points,
                'seo_metrics': {
                    'word_count': word_count,
                    'image_count': len(images),
                    'script_count': len(scripts),
                    'h1_count': h1_count,
                    'has_schema': bool(json_ld),
                    'has_og': bool(og_tags)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze {url}: {e}")
            return None

    def _is_relevant(self, business_name, url):
        """
        Check if the URL is relevant to the business name using fuzzy matching.
        """
        if not url or not business_name:
            return False
            
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Remove TLD (approximate)
            domain_parts = domain.split('.')
            if len(domain_parts) > 1:
                core_domain = domain_parts[0]
            else:
                core_domain = domain
                
            # Clean business name
            # Remove common words
            stop_words = ['llc', 'ltd', 'inc', 'services', 'solutions', 'group', 'company', 'dubai', 'uae', 'uk', 'usa']
            cleaned_name = business_name.lower()
            for word in stop_words:
                cleaned_name = cleaned_name.replace(f" {word} ", " ").replace(f" {word}", "").replace(f"{word} ", "")
            
            cleaned_name = "".join(c for c in cleaned_name if c.isalnum())
            core_domain = "".join(c for c in core_domain if c.isalnum())
            
            if not cleaned_name or not core_domain:
                return False # Cannot compare
                
            # 1. Direct containment
            if core_domain in cleaned_name or cleaned_name in core_domain:
                return True
                
            # 2. Sequence Matcher
            ratio = difflib.SequenceMatcher(None, cleaned_name, core_domain).ratio()
            return ratio > 0.65 # Threshold
            
        except:
            return True # If check fails, be permissive but cautious? No, safest to be permissive if we can't parse.

    async def _extract_from_facebook(self, fb_url, page, business_name=None):
        """
        Visit the Facebook page to extract official website and email from the Intro/About section.
        Robust deep dive implementation.
        """
        logger.info(f"Visiting Facebook page to extract details: {fb_url}")
        extracted = {'website': None, 'email': None}
        
        try:
            # Clean URL
            fb_url = fb_url.strip()
            if 'm.facebook.com' in fb_url:
                fb_url = fb_url.replace('m.facebook.com', 'www.facebook.com')
            
            # Base URL cleanup (remove query params if not profile.php)
            if 'profile.php' not in fb_url:
                fb_url = fb_url.split('?')[0]

            # 1. Visit Main Page first (often contains Intro with website)
            try:
                await page.goto(fb_url, timeout=45000, wait_until='domcontentloaded')
                await asyncio.sleep(5) # Wait for dynamic content (React hydration)
                
                # Close login popup if present
                try:
                    # Try clicking the "X" on the login modal if it appears
                    close_button = await page.locator('div[aria-label="Close"]').first
                    if await close_button.is_visible():
                        await close_button.click()
                        await asyncio.sleep(1)
                except: pass
                
                # Verify Title if business_name is provided
                if business_name:
                    try:
                        title = await page.title()
                        if title and "Facebook" in title:
                            # Clean title (e.g. "Business Name | Facebook" or "Business Name - Home")
                            clean_title = title.replace("| Facebook", "").replace("- Home", "").replace("Facebook", "").strip()
                            # Check relevance
                            # We use a lower threshold here because FB names often have suffixes/prefixes
                            is_relevant = self._is_relevant(business_name, f"http://{clean_title}.com") # Hack to reuse _is_relevant
                            
                            # Better: direct fuzzy match
                            ratio = difflib.SequenceMatcher(None, business_name.lower(), clean_title.lower()).ratio()
                            if ratio < 0.4: # Low threshold but catches completely wrong pages
                                logger.warning(f"Facebook page title '{title}' does not match business '{business_name}'. Skipping.")
                                return extracted
                    except: pass
                
                # Scroll a bit to trigger loading of "Intro" section
                try:
                    await page.evaluate("window.scrollBy(0, 500)")
                    await asyncio.sleep(2)
                except: pass

            except Exception as nav_err:
                logger.warning(f"Failed to load Facebook page {fb_url}: {nav_err}")
                return extracted

            
            # Helper to extract from current page state
            async def scan_page_content():
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract Email - Look for mailto links first
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if 'mailto:' in href:
                        email = href.replace('mailto:', '').split('?')[0]
                        # Clean email
                        email = self.email_extractor.clean_email(email)
                        if email:
                            extracted['email'] = email
                            logger.info(f"Found email on Facebook: {email}")
                            
                # Fallback email extraction from visible text (Intro section often has it as text)
                if not extracted['email']:
                    # Look for text patterns in the page content
                    # We use a simple regex on the whole text content
                    text_content = soup.get_text(" ", strip=True)
                    emails = self.email_extractor.extract(text_content)
                    if emails:
                        extracted['email'] = emails[0]
                        logger.info(f"Found email in Facebook text: {emails[0]}")
                
                # Extract Website
                # Look for external links in the 'Intro' or 'About' area
                candidates = []
                
                # Facebook specific: Look for links in the Intro section
                # The Intro section usually has <ul> list items with icons.
                # We can look for all links that are NOT internal FB links.
                
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    
                    # Handle Facebook's redirect wrapper (l.facebook.com)
                    real_url = None
                    if 'l.facebook.com/l.php' in href:
                        try:
                            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                            if 'u' in parsed:
                                real_url = parsed['u'][0]
                        except: pass
                    elif not any(d in href for d in ['facebook.com', 'javascript:', 'mailto:', '#', 'messenger.com', 'whatsapp.com']):
                        if href.startswith('http'):
                            real_url = href
                            
                    if real_url:
                        # Ignore common non-business links
                        ignore_list = [
                            'instagram.com', 'linkedin.com', 'twitter.com', 'youtube.com', 
                            'whatsapp.com', 't.me', 'goo.gl', 'maps.google', 'google.com',
                            'bit.ly', 'linktr.ee' # Maybe linktr.ee is valid? Keep it for now.
                        ]
                        if any(x in real_url for x in ignore_list):
                            continue
                            
                        # If it looks like a valid website, add it
                        candidates.append(real_url)
                        
                # Prioritize candidates
                if candidates:
                    # Pick the first one that seems most legit (usually the first one in Intro is the website)
                    extracted['website'] = candidates[0]
                    logger.info(f"Found website on Facebook: {extracted['website']}")
            
            # Scan the main page first
            await scan_page_content()
            
            # If we missed something, try navigating to the About page explicitly
            if (not extracted['website'] or not extracted['email']):
                logger.info("Details missing, trying Facebook 'About' section...")
                
                about_url = None
                if 'profile.php' in fb_url:
                    about_url = fb_url + "&sk=about"
                else:
                    # Clean any trailing slashes
                    base_clean = fb_url.rstrip('/')
                    # Try /about
                    about_url = base_clean + '/about'
                    
                if about_url:
                    try:
                        await page.goto(about_url, timeout=30000, wait_until='domcontentloaded')
                        await asyncio.sleep(4)
                        await scan_page_content()
                        
                        # If still nothing, try /about_profile (sometimes used)
                        if not extracted['website'] and not extracted['email'] and 'profile.php' not in fb_url:
                            about_profile_url = base_clean + '/about_profile'
                            await page.goto(about_profile_url, timeout=30000, wait_until='domcontentloaded')
                            await asyncio.sleep(4)
                            await scan_page_content()
                            
                    except Exception as about_err:
                        logger.warning(f"Failed to check Facebook About page: {about_err}")
                
            return extracted
            
        except Exception as e:
            logger.error(f"Facebook extraction failed: {e}")
            return extracted

    async def fallback_search(self, business_name, page, location=None, phone=None):
        """
        Fallback mechanism: Search Google for business name to find Facebook/Socials/Email
        when website is missing or yields no results.
        """
        if not business_name:
            return None
            
        logger.info(f"Performing fallback search for: {business_name}")
        
        found_data = {
            'facebook': None,
            'instagram': None,
            'linkedin': None,
            'email': None,
            'potential_website': None
        }

        # Helper function to perform a single search query
        async def perform_query(query_text):
            logger.info(f"Running query: {query_text}")
            
            IGNORE_DOMAINS = [
                'instagram.com', 'linkedin.com', 'twitter.com', 'youtube.com',
                'yelp.com', 'yellowpages.com', 'tripadvisor.com', 'mapquest.com',
                'pinterest.com', 'tiktok.com', 'foursquare.com', 'zoominfo.com',
                'whitepages.com', 'bbb.org', 'chamberofcommerce.com', 'google.com',
                'facebook.com', 'wikipedia.org', 'checkatrade.com', 'trustpilot.com',
                'yell.com', 'thomsonlocal.com'
            ]
            
            # 1. Try Apify First (Bypass CAPTCHA)
            if self.apify_service and self.apify_service.client:
                try:
                    logger.info("Using Apify Google Search Scraper...")
                    apify_results = self.apify_service.run_google_search(query_text, num_results=5)
                    
                    if apify_results:
                        for res in apify_results:
                            href = res.get('link')
                            if not href: continue
                            
                            # Logic from original scraping to process links
                            # Socials
                            if 'facebook.com' in href and not found_data['facebook']:
                                if 'sharer' not in href and 'login' not in href: found_data['facebook'] = href
                            elif 'instagram.com' in href and not found_data['instagram']:
                                found_data['instagram'] = href
                            elif 'linkedin.com' in href and not found_data['linkedin']:
                                found_data['linkedin'] = href
                                    
                            # Potential Website
                            if not found_data['potential_website']:
                                is_ignored = any(d in href for d in IGNORE_DOMAINS)
                                if not is_ignored and href.startswith('http'):
                                    if self._is_relevant(business_name, href):
                                        found_data['potential_website'] = href
                        return # Success, skip local fallback
                except Exception as apify_err:
                    logger.warning(f"Apify search failed, falling back to local: {apify_err}")

            # 2. Try DuckDuckGo (Backup if Apify unavailable/failed)
            # This is safer than Google (less strict CAPTCHA)
            if not found_data['potential_website']:
                try:
                    logger.info("Attempting DuckDuckGo Search (Fallback)...")
                    await self.random_delay(2, 4)
                    
                    # Navigate to DDG
                    await page.goto(f"https://duckduckgo.com/?q={query_text}&kl=us-en", timeout=30000, wait_until='domcontentloaded')
                    await asyncio.sleep(2)
                    
                    # Extract Results (Try modern and legacy selectors)
                    ddg_links = await page.locator('a[data-testid="result-title-a"]').all()
                    if not ddg_links:
                        ddg_links = await page.locator('.result__a').all()
                        
                    for link in ddg_links[:6]: # Check top 6
                        href = await link.get_attribute('href')
                        if not href: continue
                        
                        # Socials
                        if 'facebook.com' in href and not found_data['facebook']:
                             if 'sharer' not in href and 'login' not in href: found_data['facebook'] = href
                        elif 'instagram.com' in href and not found_data['instagram']:
                             found_data['instagram'] = href
                        elif 'linkedin.com' in href and not found_data['linkedin']:
                             found_data['linkedin'] = href
                             
                        # Website
                        if not found_data['potential_website']:
                            is_ignored = any(d in href for d in IGNORE_DOMAINS)
                            if not is_ignored and href.startswith('http'):
                                if self._is_relevant(business_name, href):
                                    found_data['potential_website'] = href
                                    logger.info(f"Found website via DuckDuckGo: {href}")
                                    
                    if found_data['potential_website']:
                         return # Found it, skip Google
                         
                except Exception as ddg_err:
                    logger.warning(f"DuckDuckGo search failed: {ddg_err}")

            # 3. Local Fallback (Google)
            try:
                # Random delay before query
                await self.random_delay(3, 7)

                # Go to Google
                try:
                    await page.goto(f"https://www.google.com/search?q={query_text}", timeout=60000, wait_until='domcontentloaded')
                except Exception as nav_err:
                    logger.warning(f"Navigation timed out or failed: {nav_err}. Checking for CAPTCHA anyway...")
                
                await self.random_delay(3, 6) # Wait for results
                
                # Simulate scrolling to look "human"
                try:
                    await page.evaluate("window.scrollTo(0, 200)")
                    await self.random_delay(0.5, 1.5)
                except: pass

                # CAPTCHA Check (Reused logic)
                is_captcha = False
                try:
                    page_title = await page.title()
                    if "sorry" in page_title.lower() or "captcha" in page_title.lower():
                        is_captcha = True
                except: pass

                if not is_captcha:
                    if await page.locator('text="Before you continue to Google"').count() > 0 or \
                       await page.locator('text="unusual traffic"').count() > 0 or \
                       await page.locator('form[action*="Captcha"]').count() > 0 or \
                       await page.locator('iframe[src*="google.com/recaptcha"]').count() > 0:
                        is_captcha = True
                    
                if is_captcha:
                    logger.warning("CAPTCHA detected! Pausing...")
                    print("!!! CAPTCHA DETECTED - PLEASE SOLVE MANUALLY !!!")
                    max_wait = 600
                    waited = 0
                    while waited < max_wait:
                        if await page.locator('div.g').count() > 0 or await page.locator('#search').count() > 0:
                            logger.info("CAPTCHA solved! Resuming...")
                            print("CAPTCHA SOLVED - RESUMING...")
                            break
                        if waited % 5 == 0:
                            logger.info(f"Waiting... ({waited}s)")
                        await asyncio.sleep(1)
                        waited += 1

                # Parse Results
                # We need to look deeper into the result items, not just the main link.
                # Google results structure: div.g contains the result.
                results = await page.locator('div.g').all()
                
                # Knowledge Panel / Sidebar Extraction (NEW)
                # Website Button
                try:
                    kp_web_btns = await page.locator('a:has-text("Website")').all()
                    for btn in kp_web_btns:
                        href = await btn.get_attribute('href')
                        if href and href.startswith('http') and not 'google.com' in href:
                             # High confidence if in KP
                            found_data['potential_website'] = href
                            break
                except: pass

                # Socials in Knowledge Panel (often small icons or in "Profiles" section)
                try:
                    # Generic broad search for social links in the right hand side or main container
                    all_links = await page.locator('a').all()
                    # Limit to first 100 links to avoid perf issues
                    for i, link in enumerate(all_links):
                        if i > 150: break
                        href = await link.get_attribute('href')
                        if not href: continue
                        
                        if 'facebook.com' in href and not found_data['facebook']:
                             if 'sharer' not in href and 'login' not in href: found_data['facebook'] = href
                        elif 'instagram.com' in href and not found_data['instagram']:
                             found_data['instagram'] = href
                        elif 'linkedin.com' in href and not found_data['linkedin']:
                             found_data['linkedin'] = href
                except: pass
                
                for result in results:
                    # Get the main link
                    try:
                        link_el = result.locator('a').first
                        href = await link_el.get_attribute('href')
                        if not href: continue
                        
                        # Socials (Double check inside results)
                        if 'facebook.com' in href and not found_data['facebook']:
                            if 'sharer' not in href and 'login' not in href:
                                found_data['facebook'] = href
                        elif 'instagram.com' in href and not found_data['instagram']:
                            found_data['instagram'] = href
                        elif 'linkedin.com' in href and not found_data['linkedin']:
                            found_data['linkedin'] = href
                                
                        # Potential Website
                        # We ignore known directories and social platforms
                        if not found_data['potential_website']:
                            is_ignored = any(d in href for d in IGNORE_DOMAINS)
                            if not is_ignored and href.startswith('http'):
                                # Check relevance
                                if self._is_relevant(business_name, href):
                                    found_data['potential_website'] = href
                                
                    except:
                        continue
                
                # If we still don't have a website, try to extract from text/cite tags
                if not found_data['potential_website']:
                    cites = await page.locator('cite').all()
                    for cite in cites:
                        text = await cite.inner_text()
                        if text and '.' in text and ' ' not in text:
                            # Possible domain
                            if not any(d in text for d in IGNORE_DOMAINS):
                                url = f"https://{text}" if not text.startswith('http') else text
                                if self._is_relevant(business_name, url):
                                    found_data['potential_website'] = url
                                    break

                # Extract Email from Text
                # IMPROVED: Scan the entire Google result text for emails
                # This catches emails that appear in the meta description/snippet
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                text_content = soup.get_text(" ", strip=True)
                emails = self.email_extractor.extract(text_content)
                if emails and not found_data['email']:
                    found_data['email'] = emails[0]
                    logger.info(f"Found email in Google Search results: {found_data['email']}")
                    
            except Exception as e:
                logger.error(f"Query failed: {e}")

        try:
            # Strategy 1: Specific Contact Search
            # "{Business Name} {City} {Phone} email contact"
            base_query = f"{business_name}"
            if location:
                base_query += f" {location}"
            if phone:
                base_query += f" {phone}"
            
            await perform_query(f"{base_query} email contact")
            
            # Strategy 2: Social Media Search (Targeted)
            # We want to ensure we find ALL of them if possible.
            social_platforms = ['facebook', 'instagram', 'linkedin']
            
            for platform in social_platforms:
                if not found_data[platform]:
                    # targeted query for each missing platform
                    await perform_query(f"{base_query} {platform}")
            
            # Strategy 3: Facebook Deep Dive (User Requested)
            # If we found a Facebook page, visit it to extract the official website and email
            if found_data['facebook']:
                await self.random_delay(2, 5) # Delay before visiting FB
                logger.info("Executing Facebook Deep Dive...")
                fb_details = await self._extract_from_facebook(found_data['facebook'], page)
                
                if fb_details.get('website'):
                    # Strong signal: Use this as the primary potential website
                    # This overrides previous guesses from search results which might be directories or competitors
                    found_data['potential_website'] = fb_details['website']
                    logger.info(f"Updated website from Facebook: {found_data['potential_website']}")
                    
                if fb_details.get('email'):
                    found_data['email'] = fb_details['email']
                    logger.info(f"Updated email from Facebook: {found_data['email']}")

            # Final Override: If email domain is strong, use it as website
            if found_data['email']:
                email_domain = found_data['email'].split('@')[-1]
                ignore_emails = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com', 'aol.com', 'protonmail.com']
                if email_domain not in ignore_emails:
                    inferred_url = f"https://www.{email_domain}"
                    # If we have no website, OR the one we have is different and the email domain is relevant to business name
                    if not found_data['potential_website']:
                         found_data['potential_website'] = inferred_url
                    elif found_data['potential_website'] and email_domain not in found_data['potential_website']:
                         # If the inferred one is relevant, prefer it?
                         # E.g. found 'theantipest.com' but email is 'apcsuae.com'
                         if self._is_relevant(business_name, inferred_url):
                             found_data['potential_website'] = inferred_url

            return found_data
            
        except Exception as e:
            logger.error(f"Fallback search failed: {e}")
            return None
