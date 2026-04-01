import sys
import os
from datetime import datetime, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.firebase_config import init_firebase
from enrichment.company_enrichment import enrich_company_data
from enrichment.email_generator import guess_best_email
from scoring.lead_scoring import score_lead, get_priority

class FirebaseEnricher:
    def __init__(self):
        try:
            self.db = init_firebase()
        except Exception as e:
            print(f"❌ Initialization aborted setting Cloud access: {e}")
            self.db = None
            
    def enrich_all_scored_leads(self):
        """Pipelines scored dataset elements appending external data logic to them."""
        if not self.db:
            print("DB client is inaccessible.")
            return []
            
        print("🔄 Fetching scored companies schemas from Firebase...")
        scored_ref = self.db.collection('scored_leads')
        docs = scored_ref.stream()
        
        companies = [doc.to_dict() for doc in docs]
        if not companies:
            print("Zero records found matching pre-filter logic.")
            return []
            
        enriched_count = 0
        enriched_ref = self.db.collection('enriched_leads')
        results = []
        
        for company in companies:
            website = company.get("website", "")
            name = company.get("company_name", "Unknown Name")
            if not website:
                continue
                
            query = enriched_ref.where("website", "==", website).limit(1).stream()
            if len(list(query)) > 0:
                print(f"⏭️ Skipping already resolved index entity: {name}")
                continue
                
            print(f"🔍 Enriching: {name} ({website})")
            
            enrich_data = enrich_company_data(company)
            best_email = guess_best_email(website)
            
            # Combine fields and update temporal marker
            company.update(enrich_data)
            company["contact_email"] = best_email
            company["enriched_at"] = datetime.now(timezone.utc)
            
            # Recalculate Scoring state variables explicitly
            new_score = score_lead(company)
            company["score"] = new_score
            company["priority"] = get_priority(new_score)
            
            try:
                enriched_ref.add(company)
                enriched_count += 1
                tech_list = ", ".join(company.get("tech_stack", []))
                print(f"✅ Enriched: {name} — Tech: {tech_list} — Score updated: {new_score}")
                results.append(company)
            except Exception as e:
                print(f"⚠️ Insertion bounds failure {name}: {e}")
                
        print(f"\n✅ Layer 4 Pipeline End: {enriched_count} leads dynamically processed.")
        return results
