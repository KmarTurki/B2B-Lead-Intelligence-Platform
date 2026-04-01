import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scoring.firebase_scorer import FirebaseScorer

def main():
    print("🚀 Booting Lead Scoring Engine Pipelines...")
    scorer = FirebaseScorer()
    scored_leads = scorer.process_all_raw_leads()
    
    if not scored_leads:
        print("Terminated early: Output array was empty.")
        return
        
    high = sum(1 for lead in scored_leads if lead.get("priority") == "High")
    medium = sum(1 for lead in scored_leads if lead.get("priority") == "Medium")
    low = sum(1 for lead in scored_leads if lead.get("priority") == "Low")
    
    print("\n✅ Scoring complete")
    print(f"Total leads scored: {len(scored_leads)}")
    print(f"High priority: {high}")
    print(f"Medium priority: {medium}")
    print(f"Low priority: {low}")
    
    print("\n🏆 Top 5 leads:")
    for i, lead in enumerate(scored_leads[:5], 1):
        name = lead.get('company_name', 'Unknown')
        score = lead.get('score', 0)
        prio = lead.get('priority', 'Unknown')
        print(f"{i}. {name} — Score: {score} — Priority: {prio}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Uncaught process exception: {e}")
