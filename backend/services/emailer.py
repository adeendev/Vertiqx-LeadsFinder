import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os
import logging
from dotenv import load_dotenv
from services.email_template import get_email_template

load_dotenv()

from sqlmodel import select
from models import Settings

class EmailService:
    def __init__(self):
        # Initial dummy values, will be loaded from DB on startup/reload
        self.host = ""
        self.port = 465
        self.user = ""
        self.password = ""
        self.from_email = ""
        self.company_name = ""
        self.company_logo = ""
        self.company_website = ""

    def reload_settings(self, session):
        settings = session.exec(select(Settings)).all()
        config = {s.key: s.value for s in settings}
        
        self.host = config.get("SMTP_HOST", "smtp.hostinger.com")
        self.port = int(config.get("SMTP_PORT", "465"))
        self.user = config.get("SMTP_USER", "")
        self.password = config.get("SMTP_PASS", "")
        self.from_email = config.get("SMTP_FROM") or self.user
        self.company_name = config.get("COMPANY_NAME", "Vertiqx")
        self.company_logo = config.get("COMPANY_LOGO", "")
        self.company_website = config.get("COMPANY_WEBSITE", "")
        self.template_type = config.get("TEMPLATE_TYPE", "html")
        self.template_ai_subject = config.get("TEMPLATE_AI_WEBSITE_SUBJECT", "Upgrade your website")
        self.template_ai_body = config.get("TEMPLATE_AI_WEBSITE_BODY", "")
        self.config = config # Store full config for dynamic access
        
        logging.info("Email settings reloaded")

    def get_auto_template(self, lead):
        """
        Determines the best template to use based on lead status
        Returns: (subject, body)
        """
        if not lead:
            return "Hello", "Hi there,"

        if lead.tier == "No Website" or not lead.domain:
            return (
                self.config.get("TEMPLATE_NO_WEBSITE_SUBJECT", "Question about {business_name}"),
                self.config.get("TEMPLATE_NO_WEBSITE_BODY", "")
            )
        
        # Check if AI Builder
        if lead.builder_type == "AI":
             return (
                self.template_ai_subject,
                self.template_ai_body
            )

        # Default fallback (or add more logic for 'Issues' etc)
        return (
             self.config.get("TEMPLATE_WITH_ISSUES_SUBJECT", "Website feedback"),
             self.config.get("TEMPLATE_WITH_ISSUES_BODY", "")
        )

    def send_email(self, to_email: str, subject: str, message_body: str, is_html: bool = True):
        if not self.user or not self.password:
            logging.error("SMTP credentials not set.")
            return False, "SMTP credentials missing"

        try:
            # Determine if we should use HTML template based on setting or override
            use_template = is_html and self.template_type == "html"

            if use_template:
                msg = MIMEMultipart("related")
            else:
                msg = MIMEMultipart("alternative")
            
            msg["Subject"] = subject
            msg["From"] = f"{self.company_name} <{self.from_email}>"
            msg["To"] = to_email

            if use_template:
                # Create the alternative part for text/html
                msgAlternative = MIMEMultipart("alternative")
                msg.attach(msgAlternative)
                
                # Use the new template
                html_content = get_email_template(
                    name="Valued Partner", # We can make this dynamic later
                    email=to_email,
                    subject=subject,
                    message=message_body,
                    company_name=self.company_name,
                    company_logo=self.company_logo,
                    company_website=self.company_website
                )
                part = MIMEText(html_content, "html")
                msgAlternative.attach(part)

                # Attach Image with Content-ID
                logo_path = r"f:\Adeen\Projects\New folder\public\Vertiqx.png"
                if os.path.exists(logo_path):
                    try:
                        with open(logo_path, 'rb') as fp:
                            msgImage = MIMEImage(fp.read())
                        
                        # Define the image ID
                        msgImage.add_header('Content-ID', '<company_logo>')
                        msgImage.add_header('Content-Disposition', 'inline', filename="Vertiqx.png")
                        msg.attach(msgImage)
                        logging.info("Attached logo via CID")
                    except Exception as img_err:
                         logging.error(f"Failed to attach logo: {img_err}")
                else:
                    logging.warning(f"Logo file not found at {logo_path}")

            else:
                # Simple text or simple HTML
                part = MIMEText(message_body, "html" if is_html else "plain")
                msg.attach(part)

            # SSL Connection
            logging.info(f"Connecting to SMTP server: {self.host}:{self.port}")
            if self.port == 465:
                server = smtplib.SMTP_SSL(self.host, self.port)
            else:
                server = smtplib.SMTP(self.host, self.port)
                server.starttls()

            logging.info(f"Logging in as {self.user}...")
            server.login(self.user, self.password)
            server.sendmail(self.from_email, to_email, msg.as_string())
            server.quit()
            
            logging.info(f"Email sent successfully to {to_email}")
            return True, "Email sent successfully"

        except smtplib.SMTPAuthenticationError:
            logging.error("SMTP Authentication Failed. Check username/password.")
            return False, "Authentication Failed. Check credentials."
        except smtplib.SMTPConnectError:
            logging.error("SMTP Connection Failed. Check host/port.")
            return False, "Connection Failed. Check server settings."
        except Exception as e:
            logging.error(f"Failed to send email: {e}")
            return False, f"Email Error: {str(e)}"
