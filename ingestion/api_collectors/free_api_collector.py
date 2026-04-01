import requests
import time

class FreeAPICollector:
    def __init__(self):
        self.session = requests.Session()
        
    def enrich_location(self, companies):
        """Enrich location data targeting RestCountries APIs."""
        print("🌍 Enriching location data using RestCountries API...")
        for company in companies:
            location = company.get("location", "")
            if not location or location == "Unknown":
                continue
                
            # Filter location context down to the assumed country: 'Berlin, Germany' -> 'Germany'
            country_name = location.split(",")[-1].strip()
            if not country_name:
                continue
                
            try:
                url = f"https://restcountries.com/v3.1/name/{country_name}"
                response = self.session.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        company["region"] = data[0].get("region", "Global")
            except Exception as e:
                print(f"⚠️ Error enriching location {country_name}: {e}")
                
            # Slow down calls to comply with generic free API usage constraints
            time.sleep(0.5)
            
        return companies

    def enrich_industry(self, companies):
        """Enrich Industry information using public Wikipedia extraction."""
        print("📚 Enriching industry data using Wikipedia API...")
        for company in companies:
            industry = company.get("industry", "")
            if not industry or "Demo" in industry:
                continue
                
            try:
                # Page Summary Rest API
                url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{industry.replace(' ', '_')}"
                response = self.session.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    extract = data.get("extract", "")
                    company["industry_description"] = extract[:150] + "..." if extract else ""
            except Exception as e:
                pass
                
            # Rate limit
            time.sleep(0.1)
            
        return companies
        
    def enrich(self, companies):
        """Main routing orchestrator for data enrichment."""
        companies = self.enrich_location(companies)
        companies = self.enrich_industry(companies)
        return companies
