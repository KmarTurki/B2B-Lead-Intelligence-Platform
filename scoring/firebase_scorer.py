import sys
import os
from datetime import datetime, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.firebase_config import init_firebase
from scoring.lead_scoring import score_all_leads

class FirebaseScorer:
    def __init__(self):
        try:
            self.db = init_firebase()
        except Exception as e:
            print(f"❌ Failed to initialize Firebase for Scorer: {e}")
            self.db = None
            
    def process_all_raw_leads(self):
        """Scans raw_companies, runs scoring algorithms, pipes data into scored_leads collection."""
        if not self.db:
            print("DB client not loaded.")
            return []
            
        print("🔄 Fetching raw companies from Firebase...")
        try:
            raw_ref = self.db.collection('raw_companies')
            docs = raw_ref.stream()
        except Exception as e:
            print(f"❌ Error fetching raw companies: {e}")
            return []
        
        companies = []
        for doc in docs:
            data = doc.to_dict()
            data['_doc_id'] = doc.id
            companies.append(data)
            
        if not companies:
            print("No raw companies found for scoring.")
            return []
            
        print(f"📊 Evaluated attributes recursively for {len(companies)} leads...")
        scored_companies = score_all_leads(companies)
        
        scored_ref = self.db.collection('scored_leads')
        saved_count = 0
        
        for company in scored_companies:
            website = company.get("website", "").strip()
            if not website:
                continue
                
            # Duplicate gating by website
            try:
                query = scored_ref.where("website", "==", website).limit(1).stream()
                is_duplicate = len(list(query)) > 0
            except Exception as e:
                print(f"⚠️ Index check failure for {website}: {e}")
                is_duplicate = False
            
            # Remove internal state ID mapping referencing old raw list
            company.pop('_doc_id', None)
            
            if not is_duplicate:
                company["scored_at"] = datetime.now(timezone.utc)
                try:
                    scored_ref.add(company)
                    saved_count += 1
                    print(f"✅ Saved scored lead: {company.get('company_name')} (Score: {company.get('score')} | {company.get('priority')})")
                except Exception as e:
                    print(f"⚠️ Failed to persist payload for {company.get('company_name', 'Unknown')}: {e}")
            else:
                print(f"⏭️ Skipping previously scored lead entry: {company.get('company_name')} ({website})")
                
        print(f"\n✅ Firestore flush complete. Transmitted {saved_count} metrics.")
        return scored_companies
