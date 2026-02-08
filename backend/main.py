from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException, Query
from sqlmodel import Session, select, desc, or_
from typing import List, Optional
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from database import create_db_and_tables, get_session, engine
from models import Lead, Project, Settings
from services.scraper import GoogleMapsScraper
from services.analyzer import WebsiteAnalyzer
from services.scoring import Scorer
from services.apify_scraper import ApifyService

# Main application entry point
from fastapi.middleware.cors import CORSMiddleware
import csv
import io
from fastapi.responses import StreamingResponse

from pydantic import BaseModel
from services.status import status_manager
from services.emailer import EmailService

app = FastAPI(title="Lead Intelligence System")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    # Initialize default settings if they don't exist
    with Session(engine) as session:
        defaults = {
            "SMTP_HOST": "smtp.hostinger.com",
            "SMTP_PORT": "465",
            "SMTP_USER": "adeen@vertiqx.com",
            "SMTP_PASS": os.getenv("HOSTINGER_PASS", ""),
            "SMTP_FROM": "adeen@vertiqx.com",
            "COMPANY_NAME": "Vertiqx",
            "COMPANY_WEBSITE": "",
            "COMPANY_LOGO": "",
            "TEMPLATE_TYPE": "html",
            "TEMPLATE_NO_WEBSITE_SUBJECT": "Question about {business_name}",
            "TEMPLATE_NO_WEBSITE_BODY": "Hi {business_name},\n\nI noticed you don't have a website yet. In today's digital age, having an online presence is crucial.\n\nWe can help you build a professional website.",
            "TEMPLATE_NOT_WORKING_SUBJECT": "Issue with {business_name} website",
            "TEMPLATE_NOT_WORKING_BODY": "Hi {business_name},\n\nI tried to visit your website but it seems to be down or unreachable.\n\nWe can help you get it back online and improve its reliability.",
            "TEMPLATE_WITH_ISSUES_SUBJECT": "Improve {business_name} website performance",
            "TEMPLATE_WITH_ISSUES_BODY": "Hi {business_name},\n\nI visited your website and noticed a few things that could be improved:\n\n{diagnosis}\n\nWe can help you fix these issues to get more customers.",
            "TEMPLATE_AI_WEBSITE_SUBJECT": "Upgrade your website for {business_name}",
            "TEMPLATE_AI_WEBSITE_BODY": "Hi {business_name},\n\nI noticed your website appears to be built with a generic builder. While these are great for starting out, a custom professional site can significantly boost your credibility and conversions.\n\nWe specialize in upgrading businesses to modern, high-performance websites.",
            "APIFY_API_TOKEN": os.getenv("APIFY_API_TOKEN", "")
        }
        for key, val in defaults.items():
            existing = session.exec(select(Settings).where(Settings.key == key)).first()
            if not existing:
                session.add(Settings(key=key, value=val))
            elif key == "APIFY_API_TOKEN" and val and not existing.value:
                existing.value = val
                session.add(existing)
            elif key == "SMTP_PASS" and val and (not existing.value or existing.value == ""):
                # Update password if it's empty in DB but we have it in env
                existing.value = val
                session.add(existing)
        session.commit()
        
        # Initial load of settings into emailer
        emailer.reload_settings(session)

# Settings Endpoints
@app.get("/api/settings")
def get_settings(session: Session = Depends(get_session)):
    settings = session.exec(select(Settings)).all()
    return {s.key: s.value for s in settings}

class SettingsUpdate(BaseModel):
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASS: Optional[str] = None
    SMTP_FROM: Optional[str] = None
    COMPANY_NAME: Optional[str] = None
    COMPANY_WEBSITE: Optional[str] = None
    COMPANY_LOGO: Optional[str] = None
    TEMPLATE_TYPE: Optional[str] = None
    TEMPLATE_NO_WEBSITE_SUBJECT: Optional[str] = None
    TEMPLATE_NO_WEBSITE_BODY: Optional[str] = None
    TEMPLATE_NOT_WORKING_SUBJECT: Optional[str] = None
    TEMPLATE_NOT_WORKING_BODY: Optional[str] = None
    TEMPLATE_WITH_ISSUES_SUBJECT: Optional[str] = None
    TEMPLATE_WITH_ISSUES_BODY: Optional[str] = None
    TEMPLATE_AI_WEBSITE_SUBJECT: Optional[str] = None
    TEMPLATE_AI_WEBSITE_BODY: Optional[str] = None
    APIFY_API_TOKEN: Optional[str] = None

@app.post("/api/settings")
def update_settings(
    settings: SettingsUpdate,
    session: Session = Depends(get_session)
):
    updates = settings.dict(exclude_unset=True)
    for key, value in updates.items():
        if value is not None:
            setting = session.exec(select(Settings).where(Settings.key == key)).first()
            if setting:
                setting.value = str(value)
                session.add(setting)
            else:
                session.add(Settings(key=key, value=str(value)))
    
    session.commit()
    
    # Reload emailer settings
    emailer.reload_settings(session)
    
    return {"status": "updated", "message": "Settings saved successfully"}

class ProviderRequest(BaseModel):
    provider: str

@app.post("/api/settings/load_provider")
def load_provider_settings(
    request: ProviderRequest,
    session: Session = Depends(get_session)
):
    provider = request.provider.lower()
    updates = {}
    
    if provider == "gmail":
        updates = {
            "SMTP_HOST": os.getenv("GMAIL_HOST", "smtp.gmail.com"),
            "SMTP_PORT": os.getenv("GMAIL_PORT", "587"),
            "SMTP_USER": os.getenv("GMAIL_USER", ""),
            "SMTP_PASS": os.getenv("GMAIL_PASS", ""),
            "SMTP_FROM": os.getenv("GMAIL_FROM", "")
        }
    elif provider == "hostinger":
        updates = {
            "SMTP_HOST": os.getenv("HOSTINGER_HOST", "smtp.hostinger.com"),
            "SMTP_PORT": os.getenv("HOSTINGER_PORT", "465"),
            "SMTP_USER": os.getenv("HOSTINGER_USER", ""),
            "SMTP_PASS": os.getenv("HOSTINGER_PASS", ""),
            "SMTP_FROM": os.getenv("HOSTINGER_FROM", "")
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid provider")
        
    for key, val in updates.items():
        if val:
            setting = session.exec(select(Settings).where(Settings.key == key)).first()
            if setting:
                setting.value = str(val)
                session.add(setting)
            else:
                session.add(Settings(key=key, value=str(val)))
                
    session.commit()
    emailer.reload_settings(session)
    
    return {"status": "updated", "provider": provider, "settings": updates}

def run_apify_task(search_terms: List[str], location: str, max_places: int, project_name: str):
    with Session(engine) as session:
        service = ApifyService(session)
        try:
            status_manager.add_log(f"Apify: Starting search for {search_terms} in {location}...", "info")
            leads = service.run_google_places_scraper(search_terms, location, max_places, project_name)
            status_manager.add_log(f"Apify: Search completed. Found {len(leads)} leads.", "success")
        except Exception as e:
            status_manager.add_log(f"Apify Error: {str(e)}", "error")

class ApifyRunRequest(BaseModel):
    search_terms: List[str]
    location: str
    max_places: int = 50
    project_name: str = "Default Project"

@app.post("/api/apify/run")
def run_apify(request: ApifyRunRequest, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    # Check if token exists
    setting = session.exec(select(Settings).where(Settings.key == "APIFY_API_TOKEN")).first()
    if not setting or not setting.value:
        raise HTTPException(status_code=400, detail="Apify API Token not configured")
    
    background_tasks.add_task(run_apify_task, request.search_terms, request.location, request.max_places, request.project_name)
    
    return {"status": "started", "message": "Apify task started in background"}

# Services
analyzer = WebsiteAnalyzer()
scorer = Scorer()
emailer = EmailService()

import subprocess
import sys
import os

# Global process tracking
ACTIVE_PROCESSES = []
STOP_REQUESTED = False

def register_process(process):
    """Adds a process to the active list, cleaning up dead ones."""
    global ACTIVE_PROCESSES
    # Clean up finished processes
    ACTIVE_PROCESSES = [p for p in ACTIVE_PROCESSES if p.poll() is None]
    ACTIVE_PROCESSES.append(process)

def stop_all_processes():
    """Terminates all active worker processes."""
    global ACTIVE_PROCESSES, STOP_REQUESTED
    STOP_REQUESTED = True
    status_manager.add_log("Stopping all active tasks...", "warning")
    
    count = 0
    for p in ACTIVE_PROCESSES:
        if p.poll() is None: # If running
            try:
                p.terminate()
                count += 1
            except Exception as e:
                print(f"Error killing process: {e}")
    
    ACTIVE_PROCESSES = [] # Clear list
    status_manager.add_log(f"Stopped {count} active worker processes.", "success")

# Background Task for Scraping (Now uses Worker Subprocess)
def run_scrape_task(keyword: str, location: str, limit: int, project_name: str = "Default Project"):
    global STOP_REQUESTED
    STOP_REQUESTED = False # Reset flag on new start
    status_manager.add_log(f"Launching worker process for {keyword}...", "info")
    
    # Launch worker.py as a separate process
    # This guarantees a clean environment and visible browser window
    try:
        p = subprocess.Popen(
            [sys.executable, "worker.py", keyword, location, str(limit), project_name],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0 # Ensures window visibility on Windows
        )
        register_process(p)
        status_manager.add_log("Worker process launched successfully", "success")
        p.wait() # Wait for it to finish so we know when it's done (optional, but good for flow)
    except Exception as e:
        status_manager.add_log(f"Failed to launch worker: {e}", "error")

def run_analyze_task(lead_id: int):
    status_manager.add_log(f"Launching analysis worker for Lead #{lead_id}...", "info")
    try:
        p = subprocess.Popen(
            [sys.executable, "worker.py", "analyze", str(lead_id)],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
        )
        register_process(p)
        status_manager.add_log(f"Analysis worker launched for Lead #{lead_id}", "success")
    except Exception as e:
        status_manager.add_log(f"Failed to launch analysis worker: {e}", "error")

@app.post("/api/stop")
def stop_tasks():
    stop_all_processes()
    return {"status": "stopped", "message": "All active tasks have been stopped."}


@app.get("/api/status")
def get_status():
    return status_manager.logs

@app.post("/api/debug/seed")
def seed_test_data(session: Session = Depends(get_session)):
    """Injects a fake lead to verify UI/DB connection"""
    fake_lead = Lead(
        business_name="Test Plumbing Co. (Fake)",
        domain="example-plumber.com",
        phone="555-0123",
        email="info@example.com",
        email_quality="Generic",
        builder="WordPress",
        builder_type="Standard",
        technical_score=45,
        final_priority=85,
        tier="Tier-1",
        city="Debug City",
        keyword="Debug",
        notes="This is a test record generated by the debug tool."
    )
    session.add(fake_lead)
    session.commit()
    status_manager.add_log("Generated test lead successfully", "success")
    return {"status": "seeded", "message": "Test lead added"}

@app.post("/api/scan")
async def start_scan(
    keyword: str, 
    location: str, 
    limit: int = Query(default=120, le=120),
    project_name: str = Query(default="Default Project"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    # Pass arguments to background task wrapper
    background_tasks.add_task(run_scrape_task, keyword, location, limit, project_name)
    return {"status": "started", "message": f"Scanning for {limit} leads for {keyword} in {location}"}

@app.get("/api/projects")
def get_projects(session: Session = Depends(get_session)):
    """Get list of unique project names"""
    # Prefer Project table
    projects = session.exec(select(Project.name).order_by(desc(Project.created_at))).all()
    
    # Fallback/Sync: Check if there are any projects in Leads that aren't in Project table
    lead_projects = session.exec(select(Lead.project_name).distinct()).all()
    
    # Merge and deduplicate
    all_projects = list(set(projects) | set([p for p in lead_projects if p]))
    return sorted(all_projects)

class ProjectCreate(BaseModel):
    name: str

@app.post("/api/projects")
def create_project(project: ProjectCreate, session: Session = Depends(get_session)):
    existing = session.exec(select(Project).where(Project.name == project.name)).first()
    if existing:
        return {"status": "exists", "name": existing.name}
    
    new_project = Project(name=project.name)
    session.add(new_project)
    session.commit()
    return {"status": "created", "name": new_project.name}

@app.put("/api/projects/{name}")
def rename_project(
    name: str, 
    project_update: ProjectCreate,
    session: Session = Depends(get_session)
):
    # Find the project
    project = session.exec(select(Project).where(Project.name == name)).first()
    
    # Check if new name already exists
    if project_update.name != name:
        existing = session.exec(select(Project).where(Project.name == project_update.name)).first()
        if existing:
            raise HTTPException(status_code=400, detail="Project with this name already exists")

    # Rename Project Entry
    if project:
        project.name = project_update.name
        session.add(project)
    
    # Rename Leads associated with this project
    leads = session.exec(select(Lead).where(Lead.project_name == name)).all()
    for lead in leads:
        lead.project_name = project_update.name
        session.add(lead)
        
    session.commit()
    return {"status": "updated", "old_name": name, "new_name": project_update.name}

@app.delete("/api/projects/{name}")
def delete_project(name: str, session: Session = Depends(get_session)):
    # Delete Project Entry
    project = session.exec(select(Project).where(Project.name == name)).first()
    if project:
        session.delete(project)
    
    # Delete Leads associated with this project
    leads = session.exec(select(Lead).where(Lead.project_name == name)).all()
    for lead in leads:
        session.delete(lead)
        
    session.commit()
    return {"status": "deleted", "name": name, "leads_deleted": len(leads)}



class LeadCreate(BaseModel):
    business_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    domain: Optional[str] = None
    city: Optional[str] = None
    project_name: str = "Default Project"
    tier: str = "New Lead"

@app.post("/api/leads")
def create_lead(lead_data: LeadCreate, session: Session = Depends(get_session)):
    # Check for duplicates (domain or name+phone)
    if lead_data.domain:
        existing = session.exec(select(Lead).where(Lead.domain == lead_data.domain)).first()
        if existing:
             raise HTTPException(status_code=400, detail="Lead with this domain already exists")
    
    if lead_data.phone:
        existing = session.exec(select(Lead).where(
            (Lead.business_name == lead_data.business_name) & 
            (Lead.phone == lead_data.phone)
        )).first()
        if existing:
            raise HTTPException(status_code=400, detail="Lead with this name and phone already exists")

    new_lead = Lead(
        business_name=lead_data.business_name,
        domain=lead_data.domain,
        phone=lead_data.phone,
        email=lead_data.email,
        city=lead_data.city or "Manual Entry",
        project_name=lead_data.project_name,
        tier=lead_data.tier,
        keyword="Manual",
        final_priority=0,
        email_quality="Unknown"
    )
    
    session.add(new_lead)
    session.commit()
    session.refresh(new_lead)
    status_manager.add_log(f"Manually added lead: {new_lead.business_name}", "success")
    return new_lead

class LeadUpdate(BaseModel):
    business_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    domain: Optional[str] = None
    pain_points: Optional[str] = None
    notes: Optional[str] = None
    city: Optional[str] = None
    tier: Optional[str] = None
    email_quality: Optional[str] = None

@app.put("/api/leads/{lead_id}")
def update_lead(
    lead_id: int,
    lead_update: LeadUpdate,
    session: Session = Depends(get_session)
):
    lead = session.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    lead_data = lead_update.dict(exclude_unset=True)
    for key, value in lead_data.items():
        setattr(lead, key, value)
        
    session.add(lead)
    session.commit()
    session.refresh(lead)
    return lead

@app.delete("/api/leads/{lead_id}")
def delete_lead(lead_id: int, session: Session = Depends(get_session)):
    lead = session.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    session.delete(lead)
    session.commit()
    return {"status": "deleted"}

class EmailRequest(BaseModel):
    to_email: str
    subject: str
    message: str
    lead_id: Optional[int] = None
    use_html: bool = True

@app.post("/api/send_email")
def send_email_endpoint(
    request: EmailRequest,
    session: Session = Depends(get_session)
):
    success, message = emailer.send_email(
        to_email=request.to_email,
        subject=request.subject,
        message_body=request.message,
        is_html=request.use_html
    )
    
    if success:
        if request.lead_id:
            lead = session.get(Lead, request.lead_id)
            if lead:
                lead.email_sent = True
                lead.email_sent_at = datetime.utcnow()
                lead.email_status = "Sent"
                session.add(lead)
                session.commit()
                status_manager.add_log(f"Email sent to {lead.business_name}", "success")
        return {"status": "sent", "message": "Email sent successfully"}
    else:
        status_manager.add_log(f"Failed to send email to {request.to_email}: {message}", "error")
        raise HTTPException(status_code=500, detail=message)

@app.post("/api/leads/{lead_id}/analyze")
async def analyze_lead_endpoint(
    lead_id: int, 
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(run_analyze_task, lead_id)
    return {"status": "started", "message": f"Analysis started for lead {lead_id}"}

class ProjectAnalysisRequest(BaseModel):
    project_name: str
    filter_mode: Optional[str] = None

import time

# User-defined limit for concurrent analysis windows
ANALYSIS_BATCH_SIZE = 5

def run_batch_analysis(lead_ids: List[int]):
    global STOP_REQUESTED
    STOP_REQUESTED = False # Reset flag (though multiple concurrent batches might race, usually it's fine)
    
    batch_size = ANALYSIS_BATCH_SIZE
    total = len(lead_ids)
    
    for i in range(0, total, batch_size):
        if STOP_REQUESTED:
            status_manager.add_log("Batch analysis stopped by user.", "warning")
            break

        batch = lead_ids[i : i + batch_size]
        processes = []
        
        status_manager.add_log(f"Starting batch {i//batch_size + 1} ({len(batch)} leads)...", "info")
        
        for lead_id in batch:
            if STOP_REQUESTED: break
            
            # Launch worker
            try:
                p = subprocess.Popen(
                    [sys.executable, "worker.py", "analyze", str(lead_id)],
                    cwd=os.path.dirname(os.path.abspath(__file__)),
                    creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
                )
                register_process(p)
                processes.append(p)
            except Exception as e:
                status_manager.add_log(f"Failed to launch analysis for {lead_id}: {e}", "error")
            
        # Wait for this batch to complete
        for p in processes:
            p.wait()
            
        status_manager.add_log(f"Batch {i//batch_size + 1} completed.", "success")
        
        # Optional small delay between batches
        if i + batch_size < total and not STOP_REQUESTED:
            status_manager.add_log("Waiting 2 seconds before next batch...", "info")
            time.sleep(2)

@app.post("/api/analyze_all")
async def analyze_all_leads(
    request: ProjectAnalysisRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    project_name = request.project_name
    leads = session.exec(select(Lead).where(Lead.project_name == project_name)).all()
    
    lead_ids_to_analyze = [lead.id for lead in leads if lead.domain]
    count = len(lead_ids_to_analyze)
    
    if count > 0:
        background_tasks.add_task(run_batch_analysis, lead_ids_to_analyze)
            
    return {"status": "started", "message": f"Queued analysis for {count} leads (Batch size: 5)", "count": count}

class BatchActionRequest(BaseModel):
    lead_ids: List[int]

@app.post("/api/analyze_batch")
async def analyze_batch(
    request: BatchActionRequest,
    background_tasks: BackgroundTasks
):
    if request.lead_ids:
        background_tasks.add_task(run_batch_analysis, request.lead_ids)
    return {"status": "started", "count": len(request.lead_ids)}

def run_batch_enrichment(lead_ids: List[int]):
    global STOP_REQUESTED
    STOP_REQUESTED = False

    batch_size = ANALYSIS_BATCH_SIZE
    total = len(lead_ids)
    
    for i in range(0, total, batch_size):
        if STOP_REQUESTED:
            status_manager.add_log("Batch enrichment stopped by user.", "warning")
            break

        batch = lead_ids[i : i + batch_size]
        processes = []
        
        status_manager.add_log(f"Starting enrichment batch {i//batch_size + 1} ({len(batch)} leads)...", "info")
        
        for lead_id in batch:
            if STOP_REQUESTED: break

            # Launch worker
            try:
                p = subprocess.Popen(
                    [sys.executable, "worker.py", "enrich", str(lead_id)],
                    cwd=os.path.dirname(os.path.abspath(__file__)),
                    creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
                )
                register_process(p)
                processes.append(p)
            except Exception as e:
                status_manager.add_log(f"Failed to launch enrichment for {lead_id}: {e}", "error")
            
        # Wait for this batch to complete
        for p in processes:
            p.wait()
            
        status_manager.add_log(f"Enrichment Batch {i//batch_size + 1} completed.", "success")
        
        if i + batch_size < total and not STOP_REQUESTED:
            status_manager.add_log("Waiting 2 seconds before next batch...", "info")
            time.sleep(2)

@app.post("/api/enrich_batch")
async def enrich_batch(
    request: BatchActionRequest,
    background_tasks: BackgroundTasks
):
    if request.lead_ids:
        background_tasks.add_task(run_batch_enrichment, request.lead_ids)
    return {"status": "started", "count": len(request.lead_ids)}


# --- Batch Email Logic ---

def process_email_batch(lead_ids: List[int], project_name: str = None, filter_mode: str = None):
    with Session(engine) as session:
        # Reload settings to be sure
        emailer.reload_settings(session)
        
        query = select(Lead)
        if lead_ids:
            query = query.where(Lead.id.in_(lead_ids))
        elif project_name:
            query = query.where(Lead.project_name == project_name)
            
            # Apply Filter Mode if present
            if filter_mode:
                if filter_mode == "analyzed":
                    query = query.where(Lead.tier.notin_(["New Lead", "Processing...", "No Website"]))
                elif filter_mode == "potential":
                    query = query.where(Lead.final_priority >= 50)
                elif filter_mode == "good_potential":
                    query = query.where(Lead.final_priority >= 75)
                elif filter_mode == "good_leads":
                    query = query.where(Lead.tier.in_(["Tier-1", "Tier-1 Gold"]))
                elif filter_mode == "potential_no_website":
                    query = query.where(or_(Lead.domain == None, Lead.domain == "", Lead.tier == "No Website"))
                # Note: "has_email" and "ready_to_email" are redundant here as we check email existence below anyway
                elif filter_mode == "email_sent":
                    query = query.where(Lead.email_sent == True)

            # Always ensure they have an email and haven't been sent one (unless user explicitly filtered for 'email_sent' maybe? but usually email blast implies new emails)
            # Actually, if filter_mode is 'email_sent', we probably shouldn't be emailing them again? 
            # But let's assume 'Email All' implies sending to *eligible* leads within that filter.
            # So we still enforce "not sent yet" logic to prevent double sending.
            
            query = query.where(Lead.email != None).where(Lead.email != "")
            query = query.where(or_(Lead.email_sent == False, Lead.email_sent == None))
        
        leads = session.exec(query).all()
        
        status_manager.add_log(f"Starting batch email for {len(leads)} leads...", "info")
        
        success_count = 0
        fail_count = 0
        
        for lead in leads:
            if not lead.email:
                continue
                
            # Smart Template Selection
            subject_tmpl, body_tmpl = emailer.get_auto_template(lead)
            
            # Format placeholders
            try:
                subject = subject_tmpl.format(business_name=lead.business_name)
                body = body_tmpl.format(
                    business_name=lead.business_name,
                    diagnosis=lead.notes or "Your website could use some improvements."
                )
            except:
                subject = subject_tmpl
                body = body_tmpl
            
            # Send
            status_manager.add_log(f"Sending email to {lead.business_name} ({lead.email})...", "info")
            success, msg = emailer.send_email(lead.email, subject, body, is_html=True)
            
            if success:
                lead.email_sent = True
                lead.email_sent_at = datetime.utcnow()
                lead.email_status = "Sent"
                session.add(lead)
                success_count += 1
            else:
                lead.email_status = f"Failed: {msg}"
                session.add(lead)
                fail_count += 1
                status_manager.add_log(f"Failed to email {lead.business_name}: {msg}", "error")
            
            session.commit()
            
            # Rate limiting (don't spam)
            time.sleep(2) 
            
        status_manager.add_log(f"Batch email complete. Sent: {success_count}, Failed: {fail_count}", "success")

@app.post("/api/email_batch")
async def email_batch(
    request: BatchActionRequest,
    background_tasks: BackgroundTasks
):
    if request.lead_ids:
        background_tasks.add_task(process_email_batch, request.lead_ids, None, None)
    return {"status": "started", "count": len(request.lead_ids)}

@app.post("/api/email_all")
async def email_all(
    request: ProjectAnalysisRequest,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(process_email_batch, None, request.project_name, request.filter_mode)
    return {"status": "started", "message": "Email blast started in background"}

# -------------------------

@app.post("/api/delete_batch")
def delete_batch(
    request: BatchActionRequest,
    session: Session = Depends(get_session)
):
    statement = select(Lead).where(Lead.id.in_(request.lead_ids))
    leads = session.exec(statement).all()
    count = len(leads)
    for lead in leads:
        session.delete(lead)
    session.commit()
    return {"status": "deleted", "count": count}

@app.get("/api/leads", response_model=List[Lead])
def get_leads(
    skip: int = 0, 
    limit: int = 1000, 
    tier: Optional[str] = None,
    filter_mode: Optional[str] = None,
    project_name: Optional[str] = None,
    session: Session = Depends(get_session)
):
    query = select(Lead).order_by(desc(Lead.final_priority))
    
    if project_name:
        query = query.where(Lead.project_name == project_name)
        
    if tier:
        query = query.where(Lead.tier == tier)
        
    if filter_mode:
        if filter_mode == "analyzed":
            # Exclude unprocessed leads
            query = query.where(Lead.tier.notin_(["New Lead", "Processing...", "No Website"]))
        elif filter_mode == "potential":
            # Leads with some potential (e.g. score >= 50)
            query = query.where(Lead.final_priority >= 50)
        elif filter_mode == "good_potential":
            # High quality leads
            query = query.where(Lead.final_priority >= 75)
        elif filter_mode == "good_leads":
             # Tier 1 and Gold
            query = query.where(Lead.tier.in_(["Tier-1", "Tier-1 Gold"]))
        elif filter_mode == "potential_no_website":
            # Potential leads that have no website or where tier is "No Website"
            # We want to catch high value targets that are missing a site
            query = query.where(
                or_(
                    Lead.domain == None,
                    Lead.domain == "",
                    Lead.tier == "No Website"
                )
            )
        elif filter_mode == "has_email":
            # Fix: Ensure empty string is excluded correctly
            query = query.where(Lead.email != None).where(Lead.email != "")
        elif filter_mode == "ready_to_email":
            # Fix: Combine AND conditions properly
            query = query.where(Lead.email != None).where(Lead.email != "")
            query = query.where(or_(Lead.email_sent == False, Lead.email_sent == None))
        elif filter_mode == "email_sent":
            query = query.where(Lead.email_sent == True)
            
    return session.exec(query.offset(skip).limit(limit)).all()

@app.get("/api/leads/export")
def export_leads(session: Session = Depends(get_session)):
    leads = session.exec(select(Lead)).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Business Name', 'Domain', 'Phone', 'Email', 'Tier', 'Priority', 'Builder'])
    
    for lead in leads:
        writer.writerow([
            lead.business_name, 
            lead.domain, 
            lead.phone, 
            lead.email, 
            lead.tier, 
            lead.final_priority,
            lead.builder
        ])
        
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]), 
        media_type="text/csv", 
        headers={"Content-Disposition": "attachment; filename=leads.csv"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
