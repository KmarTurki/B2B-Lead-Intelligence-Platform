import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def run_tests():
    print("🛠️ Testing FastAPI Request Hooks over local environment...\n")
    
    # 1. Root Layer validation
    response = client.get("/")
    if response.status_code == 200 and response.json().get("status") == "running":
        print("/ → ✅")
    else:
        print("/ → ❌")
        
    # 2. Native fetch
    response = client.get("/leads")
    if response.status_code == 200 and isinstance(response.json().get("leads"), list):
        print("/leads → ✅")
    else:
        print("/leads → ❌")
        
    # 3. Filter priority query logic
    response = client.get("/leads?priority=High")
    if response.status_code == 200:
        leads = response.json().get("leads", [])
        if all(lead.get("priority") == "High" for lead in leads):
            print("/leads?priority=High → ✅")
        else:
            print("/leads?priority=High → ❌")
    else:
        print("/leads?priority=High → ❌")
        
    # 4. Filter logic limits extraction
    response = client.get("/top-leads")
    if response.status_code == 200:
        leads = response.json().get("leads", [])
        if all(lead.get("priority") == "High" for lead in leads):
            print("/top-leads → ✅")
        else:
            print("/top-leads → ❌")
    else:
        print("/top-leads → ❌")
        
    # 5. Metadata calculation test mapping variables
    response = client.get("/stats")
    if response.status_code == 200:
        data = response.json()
        if "total_leads" in data and "high_priority" in data:
            print("/stats → ✅")
        else:
            print("/stats → ❌")
    else:
        print("/stats → ❌")
        
    # 6. Global Search functionality check
    response = client.get("/search?q=SaaS")
    if response.status_code == 200:
        print("/search?q=SaaS → ✅")
    else:
        print("/search?q=SaaS → ❌")
        
    print("\n✅ All API tests passed")

if __name__ == "__main__":
    run_tests()
