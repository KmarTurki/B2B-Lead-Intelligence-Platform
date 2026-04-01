import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from enrichment.company_enrichment import enrich_company_data
from enrichment.email_generator import generate_email_patterns, guess_best_email
from config.firebase_config import init_firebase

def test_enrichment():
    print("🛠️ Injecting testing states for Layer 4 Enrichment Validation...\n")
    
    test_companies = [
        {
            "company_name": "Stripe",
            "website": "https://stripe.com",
            "industry": "FinTech",
            "location": "San Francisco, USA",
            "employee_count": 5000,
            "source": "enrichment_test",
            "score": 0,
            "priority": "Low"
        },
        {
            "company_name": "Shopify",
            "website": "https://shopify.com",
            "industry": "SaaS",
            "location": "Ottawa, Canada",
            "employee_count": 10000,
            "source": "enrichment_test",
            "score": 0,
            "priority": "Low"
        },
        {
            "company_name": "HubSpot",
            "website": "https://hubspot.com",
            "industry": "SaaS",
            "location": "Cambridge, USA",
            "employee_count": 7000,
            "source": "enrichment_test",
            "score": 0,
            "priority": "Low"
        }
    ]
    
    print("[1/3] Parsing Production Domains over network boundary...")
    enriched_results = []
    
    tech_count = 0
    kw_count = 0
    
    for comp in test_companies:
        print(f"\n🔍 Testing {comp['company_name']} ({comp['website']})")
        
        enrichment_data = enrich_company_data(comp)
        
        predicted_emails = generate_email_patterns(comp['website'], "John", "Doe")
        best_email = guess_best_email(comp['website'])
        
        comp.update(enrichment_data)
        comp["predicted_emails"] = predicted_emails
        comp["best_email"] = best_email
        
        if comp.get("has_tech_stack"):
            tech_count += 1
        if comp.get("keywords_found"):
            kw_count += 1
            
        enriched_results.append(comp)
        
        print(f"   -> Found Tech: {comp.get('tech_stack')}")
        print(f"   -> Found Keywords: {comp.get('keywords_found')}")
        print(f"   -> Emails: {best_email} | {len(predicted_emails)} patterns generated")
        
    print("\n[2/3] Passing records layer context to Firestore...")
    try:
        db = init_firebase()
        ref = db.collection('enriched_leads')
        saved = 0
        
        for doc in enriched_results:
            q = ref.where("website", "==", doc["website"]).limit(1).stream()
            if not list(q):
                ref.add(doc)
                saved += 1
        print(f"Flushed {saved} mock leads mapping outputs.")
    except Exception as e:
        print(f"❌ IO Firestore Constraint Error: {e}")
        return
        
    print("\n[3/3] Simulating independent Read context back to state...")
    try:
        docs = db.collection('enriched_leads').where("source", "==", "enrichment_test").stream()
        found = len(list(docs))
        
        if found > 0:
            print(f"\n✅ Enrichment test passed — {found} companies enriched and saved to Firebase")
            print(f"Tech stacks found: {tech_count}")
            print(f"Keywords matched: {kw_count}")
        else:
            print("\n❌ Verification Failure.")
    except Exception as e:
        print(f"❌ Re-index Fetch Query Exception: {e}")

if __name__ == "__main__":
    test_enrichment()
