import sys
import os
from google.cloud.firestore_v1.query import Query

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.firebase_config import init_firebase

def get_top_leads(priority=None, location=None, industry=None, limit=20):
    """
    Extrapolator script querying Firebase DB arrays to identify high potential prospects.
    Includes memory filtration to bypass strict Cloud Firestore composite index limits.
    """
    try:
        db = init_firebase()
    except Exception as e:
        print(f"❌ Failed to obtain Firebase instances Context Handler: {e}")
        return []
        
    ref = db.collection('scored_leads')
    
    if priority:
        ref = ref.where("priority", "==", priority)
        
    # Standard base fetch explicitly ordering score parameter values descending
    query = ref.order_by("score", direction=Query.DESCENDING)
    
    try:
        docs = query.stream()
        results = []
        for doc in docs:
            data = doc.to_dict()
            
            # Post retrieval manual string match filtration overrides
            if location and location.lower() not in data.get("location", "").lower():
                continue
            if industry and industry.lower() not in data.get("industry", "").lower():
                continue
                
            results.append(data)
            if len(results) >= limit:
                break
                
        print(f"\n🔍 Discovered {len(results)} evaluated indices successfully:")
        for idx, lead in enumerate(results, 1):
            name = lead.get('company_name', 'Unknown Name')
            score = lead.get('score', 0)
            prio = lead.get('priority', 'Low')
            ind = lead.get('industry', 'N/A')
            loc = lead.get('location', 'Global')
            print(f"{idx}. {name} | Score: {score} | Priority: {prio} | Ind: {ind} | Loc: {loc}")
            
        return results
        
    except Exception as e:
        print(f"❌ Firestore Remote Schema Exception Rule: {e}")
        print("Note: To mitigate sequential index limits, you might need an integrated Firebase console constraint schema link explicitly clicked inside the errors.")
        return []

if __name__ == "__main__":
    try:
        print("--- Global Top 5 Leads ---")
        get_top_leads(limit=5)
        
        print("\n--- Analytics High Priority Filter (Top 5) ---")
        get_top_leads(priority="High", limit=5)
        
        print("\n--- Geographic Specific Target Search Filtering: UK (Top 5) ---")
        get_top_leads(location="UK", limit=5)
    except Exception as ex:
        print(f"Main Thread Faulted Exception -> {ex}")
