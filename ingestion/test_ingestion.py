import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ingestion.scrapers.directory_scraper import DirectoryScraper
from ingestion.firebase_writer import FirebaseWriter
from config.firebase_config import init_firebase

def test_ingestion():
    print("🛠️ Running Unit Test for Data Ingestion Layer...")
    
    # 1. Run a small test scrape
    print("\n[1/3] Testing Directory Scraper (1 page)...")
    scraper = DirectoryScraper()
    base_url = "https://www.europages.co.uk/en/companies"
    # Scrape only 1 page
    companies = scraper.scrape_directory(base_url, max_pages=1)
    print(f"Scraped {len(companies)} items.")
    
    # 2. Save fake test companies
    print("\n[2/3] Writing 3 Fake Test Companies to Firebase...")
    fake_companies = [
        {
            "company_name": "Test SaaS Co",
            "website": "https://testsaas.com",
            "industry": "SaaS",
            "location": "Paris, France",
            "employee_count": 25,
            "source": "test_script"
        },
        {
            "company_name": "FinTheWorld",
            "website": "https://fintheworld.io",
            "industry": "FinTech",
            "location": "London, UK",
            "employee_count": 150,
            "source": "test_script"
        },
        {
            "company_name": "Dummy Corp",
            "website": "https://dummycorp.net",
            "industry": "Unknown",
            "location": "Berlin, Germany",
            "employee_count": 10,
            "source": "test_script"
        }
    ]
    
    writer = FirebaseWriter()
    saved = writer.write_companies(fake_companies)
    print(f"Saved {saved} fake companies for testing.")
    
    # 3. Read back to verify
    print("\n[3/3] Verifying records in Firebase Firestore...")
    db = init_firebase()
    docs = db.collection('raw_companies').where("source", "==", "test_script").limit(3).stream()
    
    found_count = len(list(docs))
    print(f"Found {found_count} fake companies back from Firebase.")
    
    if found_count > 0:
        print(f"\n✅ Test passed — {found_count} companies found in Firebase")
    else:
        print("\n❌ Test failed — No fake companies were retrieved.")

if __name__ == "__main__":
    test_ingestion()
