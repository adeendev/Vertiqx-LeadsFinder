import re
from bs4 import BeautifulSoup
import urllib.parse

class EmailExtractor:
    def __init__(self):
        # Improved regex to avoid capturing unicode escapes or url encoding prefixes if possible
        # But cleaning is safer.
        self.email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        self.ignore_list = ['sentry', 'noreply', 'domain', 'example', 'wix', 'squarespace', 'godaddy', 'u003e', 'adeen24667@gmail.com']

    def add_ignore(self, email):
        if email and email.lower() not in self.ignore_list:
            self.ignore_list.append(email.lower())


    def clean_email(self, email):
        # Remove common garbage prefixes
        email = email.lower()
        
        # Handle URL encoding
        email = urllib.parse.unquote(email)
        
        # Remove unicode escape sequences patterns if they appear as literal text
        if "u003e" in email:
            email = email.replace("u003e", "")
        
        # Remove whitespace
        email = email.strip()
        
        # Remove garbage characters often found at start/end
        email = email.lstrip("/>:.<")
        email = email.rstrip("/>:.<")
        
        # Filter out image filenames that look like emails (common scraping error)
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.bmp', '.ico', '.tiff']
        if any(email.endswith(ext) for ext in image_extensions):
            return None
        
        # Basic validation
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return None
            
        return email

    def extract(self, html_content):
        emails = set()
        
        # Regex search
        matches = re.findall(self.email_regex, html_content)
        for email in matches:
            cleaned = self.clean_email(email)
            if cleaned and not any(ignored in cleaned for ignored in self.ignore_list):
                emails.add(cleaned)
                
        # Mailto links
        soup = BeautifulSoup(html_content, 'html.parser')
        for a in soup.find_all('a', href=True):
            if a['href'].startswith('mailto:'):
                email = a['href'].replace('mailto:', '').split('?')[0]
                cleaned = self.clean_email(email)
                if cleaned and not any(ignored in cleaned for ignored in self.ignore_list):
                    emails.add(cleaned)
                    
        return list(emails)

    def rate_quality(self, email):
        if not email:
            return "None"
        
        if any(x in email for x in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']):
            return "Personal"
        
        if any(x in email for x in ['info', 'contact', 'support', 'sales', 'hello', 'office']):
            return "Generic"
            
        return "Named" # Assumed specific person
