from datetime import datetime, timezone
import sys
import os

# Adds root leadaura folder to sys path context
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.firebase_config import init_firebase

class FirebaseWriter:
    def __init__(self):
        try:
            self.db = init_firebase()
        except Exception as e:
            print(f"❌ Failed to interface with Firebase. Check your credentials path in .env: {e}")
            self.db = None
            
    def write_companies(self, companies):
        """Batch save company outputs applying deduplication filters."""
        if not self.db:
            print("DB client is not available. Skipping save operations.")
            return 0
            
        saved_count = 0
        collection_ref = self.db.collection('raw_companies')
        
        for company in companies:
            website = company.get("website", "").strip()
            if not website:
                # Companies without website validation logic skip storage
                print("Skipping company entry lacking a valid website.")
                continue 
                
            # Validating duplicates by exact matching `website` field
            query = collection_ref.where("website", "==", website).limit(1).stream()
            is_duplicate = len(list(query)) > 0
            
            if not is_duplicate:
                company["scraped_at"] = datetime.now(timezone.utc)
                
                try:
                    collection_ref.add(company)
                    saved_count += 1
                except Exception as e:
                    print(f"⚠️ Failed to record payload for {company.get('company_name', 'Unknown')}: {e}")
            else:
                print(f"⏭️ Skipping duplicate platform entry: {company.get('company_name')} ({website})")
                
        print(f"✅ Firebase Writer finished: {saved_count} new companies saved to Firestore.")
        return saved_count
