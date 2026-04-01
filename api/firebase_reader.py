import sys
import os
from collections import Counter

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.firebase_config import init_firebase

class FirebaseReader:
    def __init__(self):
        try:
            self.db = init_firebase()
        except Exception as e:
            print(f"❌ Failed to init Backend Firestore: {e}")
            self.db = None
            
    def get_all_leads(self, industry=None, location=None, priority=None, limit=20):
        if not self.db:
            return []
            
        ref = self.db.collection('enriched_leads')
        if priority:
            # We assume a single primitive index can handle exact matches
            ref = ref.where("priority", "==", priority)
            
        docs = ref.stream()
        results = []
        for doc in docs:
            data = doc.to_dict()
            if industry and industry.lower() not in data.get("industry", "").lower():
                continue
            if location and location.lower() not in data.get("location", "").lower():
                continue
            results.append(data)
            
        return results[:limit]
        
    def get_lead_by_name(self, company_name):
        if not self.db:
            return None
        # String match constraints check via Cloud query API
        docs = self.db.collection('enriched_leads').where("company_name", "==", company_name).limit(1).stream()
        for doc in docs:
            return doc.to_dict()
        return None
        
    def search_leads(self, query):
        if not self.db:
            return []
            
        query = query.lower()
        docs = self.db.collection('enriched_leads').stream()
        matching = []
        for doc in docs:
            data = doc.to_dict()
            haystack = f"{data.get('company_name','')} {data.get('industry','')} {data.get('location','')} {data.get('description','')} {data.get('website','')}".lower()
            if query in haystack:
                matching.append(data)
                
        return matching
        
    def get_stats(self):
        if not self.db:
            return {}
            
        docs = self.db.collection('enriched_leads').stream()
        leads = list(doc.to_dict() for doc in docs)
        
        total = len(leads)
        if total == 0:
            return {
                "total_leads": 0, "high_priority": 0, "medium_priority": 0, "low_priority": 0,
                "average_score": 0.0, "top_industries": [], "top_locations": [], "leads_with_tech_stack": 0
            }
            
        priorities = Counter(l.get("priority", "Low") for l in leads)
        score_sum = sum(l.get("score", 0) for l in leads)
        has_tech = sum(1 for l in leads if l.get("has_tech_stack"))
        
        inds = Counter(l.get("industry", "Unknown") for l in leads if l.get("industry"))
        locs = Counter(l.get("location", "Unknown") for l in leads if l.get("location"))
        
        top_inds = [item[0] for item in inds.most_common(2)]
        top_locs = [item[0] for item in locs.most_common(3)]
        
        return {
            "total_leads": total,
            "high_priority": priorities.get("High", 0),
            "medium_priority": priorities.get("Medium", 0),
            "low_priority": priorities.get("Low", 0),
            "average_score": round(score_sum / total, 1),
            "top_industries": top_inds,
            "top_locations": top_locs,
            "leads_with_tech_stack": has_tech
        }
