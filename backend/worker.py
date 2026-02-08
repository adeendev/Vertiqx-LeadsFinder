import asyncio
import sys
import os
from sqlmodel import Session, select
from database import engine
from models import Lead
from services.scraper import GoogleMapsScraper
from services.analyzer import WebsiteAnalyzer
from services.scoring import Scorer
from services.status import status_manager
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

sys.path.append(os.getcwd())

async def run_search_worker(keyword: str, location: str, limit: int, project_name: str):
    status_manager.add_log(f"Worker process started for {keyword} in {location} (Project: {project_name})", "info")
    
    # Force headless=False for visibility
    scraper = GoogleMapsScraper(headless=False, status_callback=status_manager.add_log)
    await scraper.start()
    
    try:
        status_manager.add_log("Worker: Browser launched", "info")
        
        async def process_lead(raw):
            with Session(engine) as session:
                # Check duplication
                # 1. By Domain (if exists)
                if raw.get('website'):
                    existing = session.exec(select(Lead).where(Lead.domain == raw['website'])).first()
                    if existing:
                        status_manager.add_log(f"Skipping duplicate (domain): {raw['business_name']}", "warning")
                        return
                
                # 2. By Name + Phone (if website missing, or just to be safe)
                # This prevents adding the same business multiple times if they have no website
                if raw.get('phone'):
                     existing = session.exec(select(Lead).where(
                         (Lead.business_name == raw['business_name']) & 
                         (Lead.phone == raw['phone'])
                     )).first()
                     if existing:
                        status_manager.add_log(f"Skipping duplicate (name+phone): {raw['business_name']}", "warning")
                        return

                # Initial Save
                lead = Lead(
                    business_name=raw['business_name'],
                    domain=raw.get('website'),
                    phone=raw.get('phone'),
                    tier="New Lead", # Changed from Processing...
                    final_priority=0,
                    city=location,
                    keyword=keyword,
                    project_name=project_name,
                    notes="Pending Analysis",
                    facebook=raw.get('facebook'),
                    instagram=raw.get('instagram'),
                    linkedin=raw.get('linkedin')
                )
                
                if not raw.get('website'):
                    lead.tier = "No Website"
                    lead.final_priority = 10
                    lead.notes = "No website found on Maps"

                session.add(lead)
                session.commit()
                status_manager.add_log(f"Found: {raw['business_name']}", "success")
                return True # Indicate success
            
        # Start search
        await scraper.search_business(keyword, location, limit, on_lead_found=process_lead)
        status_manager.add_log("Worker: Scan completed", "success")
                
    except Exception as e:
        status_manager.add_log(f"Worker failed: {str(e)}", "error")
    finally:
        await scraper.stop()
        # Cooldown period to avoid detection/spamming
        status_manager.add_log("Cooling down for 5-10 minutes...", "info")
        import random
        # Using a shorter cooldown for testing purposes if needed, but user asked for 5-10 min
        # We'll stick to 5-10 min (300-600 seconds)
        # Note: This keeps the process alive.
        await asyncio.sleep(random.randint(300, 600))
        status_manager.add_log("Cooldown complete. Worker exiting.", "success")

from services.browser_manager import BrowserManager

async def run_analysis_worker(lead_id: int):
    status_manager.add_log(f"Starting analysis for Lead #{lead_id}", "info")
    
    analyzer = WebsiteAnalyzer()
    scorer = Scorer()
    
    async with async_playwright() as p:
        try:
            context, browser, is_shared = await BrowserManager.get_browser_context(p)
            
            # Use a new page for analysis
            page = await context.new_page()
            page.set_default_timeout(60000)
            
            stealth = Stealth()
            await stealth.apply_stealth_async(page)
            
            try:
                with Session(engine) as session:
                    lead = session.get(Lead, lead_id)
                    if not lead:
                        status_manager.add_log(f"Lead #{lead_id} not found", "error")
                        return
                    
                    analysis = None

                    if lead.domain:
                        status_manager.add_log(f"Visiting {lead.domain}...", "info")
                        analysis = await analyzer.analyze(lead.domain, page)
                    else:
                        status_manager.add_log(f"No website provided. Searching Google for {lead.business_name}...", "info")

                    # Fallback / Discovery Search
                    if not analysis or (analysis and not analysis.get('primary_email')):
                        status_manager.add_log(f"Attempting discovery search for {lead.business_name}...", "warning")
                        fallback_data = await analyzer.fallback_search(lead.business_name, page, location=lead.city)
                        
                        if fallback_data:
                            if not analysis: analysis = {}
                            
                            if fallback_data.get('email'):
                                cleaned_email = analyzer.email_extractor.clean_email(fallback_data['email'])
                                if cleaned_email:
                                    status_manager.add_log(f"Discovery found email: {cleaned_email}", "success")
                                    analysis['primary_email'] = cleaned_email
                                    analysis['email_quality'] = "External/Search"
                                
                            if fallback_data.get('facebook'):
                                status_manager.add_log(f"Discovery found Facebook: {fallback_data['facebook']}", "success")
                                analysis['facebook'] = fallback_data['facebook']
                            
                            if fallback_data.get('instagram'):
                                analysis['instagram'] = fallback_data['instagram']
                            if fallback_data.get('linkedin'):
                                analysis['linkedin'] = fallback_data['linkedin']

                            if fallback_data.get('potential_website') and not lead.domain:
                                 status_manager.add_log(f"Discovery found potential website: {fallback_data['potential_website']}", "success")
                                 lead.domain = fallback_data['potential_website']
                                 
                                 # IMMEDIATELY ANALYZE this new website within the same session
                                 # This ensures the lead gets a proper score instead of just a domain
                                 status_manager.add_log(f"Analyzing newly discovered website...", "info")
                                 try:
                                     # We use the same page instance
                                     new_analysis = await analyzer.analyze(lead.domain, page)
                                     if new_analysis:
                                         # Merge with existing analysis if any, or set it
                                         if not analysis: analysis = {}
                                         analysis.update(new_analysis)
                                         status_manager.add_log(f"Website analysis merged.", "success")
                                 except Exception as e:
                                     status_manager.add_log(f"Failed to analyze new website: {e}", "error")
                                
                            if not analysis.get('builder'):
                                 analysis['builder'] = "Unknown (Fallback)"
                    
                    raw = {
                        'business_name': lead.business_name,
                        'website': lead.domain,
                        'phone': lead.phone
                    }
                    
                    score_data = scorer.calculate_score(raw, analysis)
                    
                    lead.email = analysis['primary_email'] if analysis else None
                    lead.email_quality = analysis['email_quality'] if analysis else None
                    lead.builder = analysis['builder'] if analysis else None
                    lead.builder_type = "AI" if analysis and analysis['is_ai_builder'] else "Standard"
                    lead.technical_score = score_data['breakdown']['bad_website_score']
                    lead.business_score = score_data['breakdown']['review_score']
                    lead.final_priority = score_data['final_priority']
                    lead.tier = score_data['tier']
                    lead.notes = str(score_data['breakdown'])
                    lead.facebook = analysis.get('facebook') if analysis else None
                    lead.instagram = analysis.get('instagram') if analysis else None
                    lead.linkedin = analysis.get('linkedin') if analysis else None
                    
                    if analysis and analysis.get('pain_points'):
                        # Join list into string
                        lead.pain_points = " | ".join(analysis['pain_points'])
                    
                    session.add(lead)
                    session.commit()
                    status_manager.add_log(f"Analysis complete for {lead.business_name}", "success")
            except Exception as e:
                status_manager.add_log(f"Analysis failed: {str(e)}", "error")
            finally:
                if page:
                    await page.close()
                if not is_shared and context:
                    await context.close()
                    
        except Exception as e:
             status_manager.add_log(f"Browser launch failed: {e}", "error")

async def run_enrich_worker(lead_id: int):
    status_manager.add_log(f"Starting enrichment for Lead #{lead_id}", "info")
    
    analyzer = WebsiteAnalyzer()
    
    async with async_playwright() as p:
        try:
            context, browser, is_shared = await BrowserManager.get_browser_context(p)
            
            page = await context.new_page()
            page.set_default_timeout(60000)
            
            stealth = Stealth()
            await stealth.apply_stealth_async(page)
            
            try:
                with Session(engine) as session:
                    lead = session.get(Lead, lead_id)
                    if not lead:
                        return
                    
                    status_manager.add_log(f"Searching Google for missing details: {lead.business_name}", "info")
                    
                    # Perform Search
                    fallback_data = await analyzer.fallback_search(
                        lead.business_name, 
                        page, 
                        location=lead.city,
                        phone=lead.phone
                    )
                    
                    updated = False
                    if fallback_data:
                        if fallback_data.get('email') and not lead.email:
                            cleaned_email = analyzer.email_extractor.clean_email(fallback_data['email'])
                            if cleaned_email:
                                lead.email = cleaned_email
                                lead.email_quality = "Enriched"
                                status_manager.add_log(f"Enriched email: {lead.email}", "success")
                                updated = True
                            
                        if fallback_data.get('facebook') and not lead.facebook:
                            lead.facebook = fallback_data['facebook']
                            status_manager.add_log(f"Enriched Facebook: {lead.facebook}", "success")
                            updated = True

                        if fallback_data.get('instagram') and not lead.instagram:
                            lead.instagram = fallback_data['instagram']
                            status_manager.add_log(f"Enriched Instagram: {lead.instagram}", "success")
                            updated = True

                        if fallback_data.get('linkedin') and not lead.linkedin:
                            lead.linkedin = fallback_data['linkedin']
                            status_manager.add_log(f"Enriched LinkedIn: {lead.linkedin}", "success")
                            updated = True
                            
                        if fallback_data.get('potential_website') and not lead.domain:
                            lead.domain = fallback_data['potential_website']
                            status_manager.add_log(f"Enriched Website: {lead.domain}", "success")
                            updated = True
                            
                            # IMMEDIATELY ANALYZE the newly found website
                            # The user wants to score it right away if it was missing
                            status_manager.add_log(f"Analyzing newly found website: {lead.domain}...", "info")
                            try:
                                analysis = await analyzer.analyze(lead.domain, page)
                                if analysis:
                                    raw = {
                                        'business_name': lead.business_name,
                                        'website': lead.domain,
                                        'phone': lead.phone
                                    }
                                    score_data = scorer.calculate_score(raw, analysis)
                                    
                                    lead.technical_score = score_data['breakdown']['bad_website_score']
                                    lead.business_score = score_data['breakdown']['review_score']
                                    lead.final_priority = score_data['final_priority']
                                    lead.tier = score_data['tier']
                                    lead.notes = str(score_data['breakdown'])
                                    lead.builder = analysis.get('builder')
                                    lead.builder_type = "AI" if analysis.get('is_ai_builder') else "Standard"
                                    
                                    if analysis.get('pain_points'):
                                        lead.pain_points = " | ".join(analysis['pain_points'])
                                        
                                    status_manager.add_log(f"Scored new website: {lead.final_priority}/100", "success")
                            except Exception as score_err:
                                status_manager.add_log(f"Failed to score new website: {score_err}", "error")
                
                    if updated:
                        session.add(lead)
                        session.commit()
                    else:
                        status_manager.add_log(f"No new details found for {lead.business_name}", "warning")
                        
            except Exception as e:
                status_manager.add_log(f"Enrichment failed: {str(e)}", "error")
            finally:
                if page:
                    await page.close()
                if not is_shared and context:
                    await context.close()

        except Exception as e:
             status_manager.add_log(f"Browser launch failed: {e}", "error")

if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            print("Usage: python worker.py <mode> [args...]")
            sys.exit(1)
            
        mode = sys.argv[1]
        
        if mode == "search":
            # python worker.py search <keyword> <location> <limit> <project_name>
            if len(sys.argv) < 6:
                print("Usage: python worker.py search <keyword> <location> <limit> <project_name>")
                sys.exit(1)
            k = sys.argv[2]
            l = sys.argv[3]
            lim = int(sys.argv[4])
            p = sys.argv[5]
            asyncio.run(run_search_worker(k, l, lim, p))
            
        elif mode == "analyze":
            # python worker.py analyze <lead_id>
            if len(sys.argv) < 3:
                print("Usage: python worker.py analyze <lead_id>")
                sys.exit(1)
            lid = int(sys.argv[2])
            asyncio.run(run_analysis_worker(lid))

        elif mode == "enrich":
            # python worker.py enrich <lead_id>
            if len(sys.argv) < 3:
                print("Usage: python worker.py enrich <lead_id>")
                sys.exit(1)
            lid = int(sys.argv[2])
            asyncio.run(run_enrich_worker(lid))
            
        else:
            # Backward compatibility for old calls (just in case)
            # Old sig: python worker.py <keyword> <location> <limit> <project_name>
            if len(sys.argv) >= 5:
                k = sys.argv[1]
                l = sys.argv[2]
                lim = int(sys.argv[3])
                p = sys.argv[4]
                asyncio.run(run_search_worker(k, l, lim, p))
            else:
                print("Unknown mode")

    except Exception as critical_error:
        print(f"\n{'='*50}")
        print(f"CRITICAL WORKER ERROR: {critical_error}")
        print(f"{'='*50}\n")
        import traceback
        traceback.print_exc()
        print("\nKeeping window open for diagnosis...")
        input("Press Enter to exit...")
        sys.exit(1)
