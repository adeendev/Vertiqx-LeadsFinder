from apify_client import ApifyClient
from sqlmodel import Session, select
from models import Lead, Settings, Project
from database import engine
import datetime

class ApifyService:
    def __init__(self, session: Session):
        self.session = session
        self.token = self._get_token()
        self.client = ApifyClient(token=self.token) if self.token else None

    def _get_token(self):
        setting = self.session.exec(select(Settings).where(Settings.key == "APIFY_API_TOKEN")).first()
        return setting.value if setting else None

    def run_google_places_scraper(self, search_terms: list[str], location: str, max_places: int = 50, project_name: str = "Default Project"):
        if not self.client:
            raise Exception("Apify API Token not found. Please configure it in settings.")

        # Prepare Actor input
        run_input = {
            "searchStringsArray": search_terms,
            "locationQuery": location,
            "maxCrawledPlacesPerSearch": max_places,
            "language": "en",
            "searchMatching": "all",
            "placeMinimumStars": "",
            "website": "allPlaces",
            "skipClosedPlaces": False,
            "scrapePlaceDetailPage": False,
            "scrapeTableReservationProvider": False,
            "includeWebResults": False,
            "scrapeDirectories": False,
            "maxQuestions": 0,
            "scrapeContacts": False,
            "scrapeSocialMediaProfiles": {
                "facebooks": False,
                "instagrams": False,
                "youtubes": False,
                "tiktoks": False,
                "twitters": False
            },
            "maximumLeadsEnrichmentRecords": 0,
            "maxReviews": 0,
            "reviewsSort": "newest",
            "reviewsFilterString": "",
            "reviewsOrigin": "all",
            "scrapeReviewsPersonalData": True,
            "maxImages": 0,
            "scrapeImageAuthors": False,
            "allPlacesNoSearchAction": ""
        }

        # Run the Actor and wait for it to finish
        # Actor ID for Google Maps Scraper (compass/crawler-google-places)
        # The user provided ID: "nwua9Gu5YrADL7ZDj" in the snippet, but also linked to compass/crawler-google-places
        # compass/crawler-google-places is the public actor. "nwua9Gu5YrADL7ZDj" might be a specific ID.
        # I'll use "compass/crawler-google-places" as it's more reliable generally, or the ID if they prefer.
        # User snippet: client.actor("nwua9Gu5YrADL7ZDj").call(input)
        # I will use the ID provided by the user.
        
        run = self.client.actor("nwua9Gu5YrADL7ZDj").call(run_input=run_input)

        # Fetch results
        dataset_items = self.client.dataset(run["defaultDatasetId"]).list_items().items
        
        saved_leads = []
        for item in dataset_items:
            lead = self._process_item(item, project_name, location)
            if lead:
                saved_leads.append(lead)
        
        return saved_leads

    def _process_item(self, item: dict, project_name: str, fallback_location: str = "") -> Lead:
        # Map Apify result to Lead model
        business_name = item.get("title")
        if not business_name:
            return None

        # Extract data
        website = item.get("website")
        phone = item.get("phone")
        address = item.get("address")
        city = item.get("city")
        
        # Try to extract city from address if missing
        if not city and address:
             parts = address.split(",")
             if len(parts) >= 2:
                 city = parts[-2].strip() 
             else:
                 city = address

        lead = Lead(
            business_name=business_name,
            domain=website,
            phone=phone,
            city=city or fallback_location, 
            keyword=item.get("searchString", "Apify Search"),
            project_name=project_name,
            notes=f"Imported from Apify. Address: {address}",
            tier="New"
        )
        
        # Save to DB
        # Check if exists
        existing = self.session.exec(select(Lead).where(Lead.business_name == business_name).where(Lead.project_name == project_name)).first()
        if not existing:
            self.session.add(lead)
            self.session.commit()
            self.session.refresh(lead)
            return lead
        return existing

    def run_google_search(self, query: str, num_results: int = 10):
        """
        Uses Apify's Google Search Scraper (apify/google-search-scraper)
        to bypass CAPTCHAs and get clean results.
        """
        if not self.client:
            return None

        run_input = {
            "queries": [query],
            "resultsPerPage": num_results,
            "maxPagesPerQuery": 1,
            "languageCode": "",
            "mobileResults": False,
            "includeUnfilteredResults": False,
            "saveHtml": False,
            "saveHtmlToKeyValueStore": False,
            "includeIcons": False,
        }

        try:
            # Run the Actor (apify/google-search-scraper)
            run = self.client.actor("apify/google-search-scraper").call(run_input=run_input)
            
            # Fetch results
            dataset_items = self.client.dataset(run["defaultDatasetId"]).list_items().items
            
            # Format results to match what analyzer expects
            # Analyzer expects list of objects with 'link', 'title', 'snippet' (or similar structure to parse)
            clean_results = []
            for item in dataset_items:
                # The actor returns a list of 'organicResults'
                organic = item.get("organicResults", [])
                for res in organic:
                    clean_results.append({
                        "title": res.get("title"),
                        "link": res.get("url"),
                        "snippet": res.get("description")
                    })
            
            return clean_results
            
        except Exception as e:
            print(f"Apify Google Search failed: {e}")
            return None
