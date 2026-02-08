from bs4 import BeautifulSoup
import re

class BuilderDetector:
    def __init__(self):
        self.signatures = {
            'WordPress': [r'/wp-content/', r'/wp-includes/', r'wordpress'],
            'Shopify': [r'cdn\.shopify\.com', r'Shopify'],
            'Wix': [r'wix\.com', r'wix-dns', r'_wix'],
            'Squarespace': [r'squarespace\.com', r'static1\.squarespace'],
            'Webflow': [r'webflow\.com', r'w-nav'],
            'GoDaddy': [r'godaddy', r'img1\.wsimg\.com'],
            'Hostinger': [r'hostinger', r'zyro'],
            'React': [r'react', r'data-reactid'],
            'Next.js': [r'/_next/'],
        }
        
        self.ai_indicators = [
            r'zyro',
            r'godaddy sites',
            r'wix adi',
            r'artificial intelligence', # Sometimes in footer "Powered by AI..."
        ]

    def detect(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        html_str = str(soup).lower()
        
        detected_builder = "Unknown"
        is_ai = False
        
        # Check Builders
        for builder, patterns in self.signatures.items():
            for pattern in patterns:
                if re.search(pattern, html_str):
                    detected_builder = builder
                    break
            if detected_builder != "Unknown":
                break
                
        # Check AI indicators
        for pattern in self.ai_indicators:
            if re.search(pattern, html_str):
                is_ai = True
                break
                
        # Specific AI checks for known builders
        if detected_builder == 'GoDaddy':
            # GoDaddy often implies simple/AI builder
            is_ai = True
        
        return {
            'builder': detected_builder,
            'is_ai': is_ai
        }
