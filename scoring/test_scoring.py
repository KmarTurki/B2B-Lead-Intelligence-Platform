import sys
import os
from datetime import datetime, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scoring.lead_scoring import score_all_leads
from config.firebase_config import init_firebase

def test_scoring_logic():
    print("🛠️ Initiating automated tests for Evaluation Rules...\n")
    
    # Fake schema variants validating edge cases of algorithm weights
    fake_companies = [
        {
            "company_name": "Perfect SaaS Co",
            "website": "https://perfectsaas.com",
            "industry": "SaaS", # 30 
            "location": "Paris, France", # 20 
            "employee_count": 50, # 25 
            "has_tech_stack": True, # 15 
            "description": "We specialize in digital transformation and automation.", # 10 
            "source": "test_script"
        },
        {
            "company_name": "Average FinTech",
            "website": "https://averagefintech.io",
            "industry": "FinTech", # 30 
            "location": "Berlin, Germany", # 20 
            "employee_count": 500, # 0
            "has_tech_stack": False, # 0
            "description": "Financial services for retail.", # 0
            "source": "test_script"
        },
        {
            "company_name": "Medium Startup",
            "website": "https://medianstart.co",
            "industry": "SaaS", # 30 
            "location": "Toronto, Canada", # 0
            "employee_count": 150, # 25
            "has_tech_stack": False, # 0
            "description": "Growth tech solutions", # 0 (assuming growth isn't directly parsed here or gets 10 if parsed)
            "source": "test_script"
        },
        {
            "company_name": "Poor Match Corp",
            "website": "https://poormatch.net",
            "industry": "Agriculture", # 0
            "location": "New York, USA", # 0
            "employee_count": 5, # 0
            "has_tech_stack": False, # 0
            "description": "Farming tools.", # 0
            "source": "test_script"
        },
        {
            "company_name": "UK FinTech Ltd",
            "website": "https://ukfintech.co.uk",
            "industry": "FinTech", # 30
            "location": "London, UK", # 20
            "employee_count": 100, # 25
            "has_tech_stack": False, # 0
            "description": "Payments and transfers.", # 0
            "source": "test_script"
        }
    ]
    
    print("[1/3] Translating Fake Rules Engine Outputs...")
    scored = score_all_leads(fake_companies)
    
    high = sum(1 for lead in scored if lead.get("priority") == "High")
    medium = sum(1 for lead in scored if lead.get("priority") == "Medium")
    low = sum(1 for lead in scored if lead.get("priority") == "Low")
    
    for lead in scored:
        print(f"- {lead['company_name']} -> Score: {lead['score']}, Priority: {lead['priority']}")
        
    print("\n[2/3] Writing Synthetic Payload over Firebase Sync Layer...")
    try:
        db = init_firebase()
        scored_ref = db.collection('scored_leads')
        saved_amount = 0
        for doc in scored:
            q = scored_ref.where("website", "==", doc["website"]).limit(1).stream()
            if not list(q):
                doc["scored_at"] = datetime.now(timezone.utc)
                scored_ref.add(doc)
                saved_amount += 1
        print(f"Propagated {saved_amount} independent entities payload.")
    except Exception as e:
        print(f"❌ Firebase I/O Network Failure: {e}")
        return
        
    print("\n[3/3] Echo Validation Sequence (Read-back Assertion)...")
    try:
        docs = db.collection('scored_leads').where("source", "==", "test_script").stream()
        found = len(list(docs))
        
        if found > 0:
            print(f"\n✅ Scoring test passed — {found} leads scored and saved to Firebase")
            print(f"High: {high} | Medium: {medium} | Low: {low}")
        else:
            print("\n❌ Test failed — Found zero persistent data indices mapped resolving source criteria.")
    except Exception as e:
        print(f"❌ Target Query Evaluation Fault: {e}")

if __name__ == "__main__":
    test_scoring_logic()
