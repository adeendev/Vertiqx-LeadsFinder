from sqlmodel import Session, select
from backend.database import engine, get_session
from backend.models import Settings
from backend.services.emailer import EmailService
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

load_dotenv("backend/.env")

def setup_gmail_settings(session: Session):
    print("🔄 Switching DB settings to Gmail...")
    updates = {
        "SMTP_HOST": os.getenv("GMAIL_HOST", "smtp.gmail.com"),
        "SMTP_PORT": os.getenv("GMAIL_PORT", "587"),
        "SMTP_USER": os.getenv("GMAIL_USER", ""),
        "SMTP_PASS": os.getenv("GMAIL_PASS", ""),
        "SMTP_FROM": os.getenv("GMAIL_FROM", "")
    }
    
    for key, val in updates.items():
        setting = session.exec(select(Settings).where(Settings.key == key)).first()
        if setting:
            setting.value = str(val)
            session.add(setting)
        else:
            session.add(Settings(key=key, value=str(val)))
    session.commit()
    print("✅ Settings updated to Gmail.")

def test_service():
    with Session(engine) as session:
        # 1. Setup Gmail in DB
        setup_gmail_settings(session)
        
        # 2. Initialize Service
        service = EmailService()
        service.reload_settings(session)
        
        print(f"Service Configured: {service.host}:{service.port} User: {service.user}")
        
        # 3. Send Email
        to_email = "test_recipient@example.com" # Just checking if it sends to server, actual delivery doesn't matter as much as handshake
        # But better to use a real email or the user's email if possible. 
        # I'll use the FROM email as the TO email to send to self.
        to_email = service.from_email
        
        print(f"Attempting to send email to {to_email}...")
        success, message = service.send_email(
            to_email=to_email,
            subject="Test Gmail via Service",
            message_body="<h1>It works!</h1><p>This is a test from the EmailService.</p>",
            is_html=True
        )
        
        if success:
            print(f"✅ SUCCESS: {message}")
        else:
            print(f"❌ FAILED: {message}")

if __name__ == "__main__":
    test_service()
