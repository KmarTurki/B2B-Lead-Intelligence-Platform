import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ingestion.scrapers.directory_scraper import DirectoryScraper
from ingestion.api_collectors.free_api_collector import FreeAPICollector
from ingestion.firebase_writer import FirebaseWriter

def load_icp():
    """Load matching metrics configurations from standard settings path."""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'icp_config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    print("🚀 Booting Data Ingestion Pipelines...")
    
    icp_config = load_icp()
    print(f"📋 Loaded ICP for industries parameters: {', '.join(icp_config['icp']['target_industries'])}")
    
    # 1. Scrape generic directory sources natively 
    scraper = DirectoryScraper()
    print("\n--- Phase 1: Identifying Directories via Web Scraping ---")
    base_url = "https://www.europages.co.uk/en/companies"
    scraped_companies = scraper.scrape_directory(base_url, max_pages=3)
    print(f"🔎 Acquired {len(scraped_companies)} leads.")
    
    # 2. Enrich outputs natively passing payloads
    print("\n--- Phase 2: Metadata enrichment parameters mapping ---")
    api_collector = FreeAPICollector()
    enriched_companies = api_collector.enrich(scraped_companies)
    
    # 3. Synchronize payload states directly inside Google Cloud backend
    print("\n--- Phase 3: Committing to active cloud index ---")
    writer = FirebaseWriter()
    saved_count = writer.write_companies(enriched_companies)
    
    # End routine summaries
    print(f"\n✅ Ingestion complete — {saved_count} companies saved to Firebase")

if __name__ == "__main__":
    main()
