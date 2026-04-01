import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from enrichment.firebase_enricher import FirebaseEnricher

def main():
    print("🚀 Firing Lead Enrichment Engine Modules...")
    enricher = FirebaseEnricher()
    enriched_leads = enricher.enrich_all_scored_leads()
    
    if not enriched_leads:
        print("Empty extraction return layer.")
        return
        
    total = len(enriched_leads)
    has_tech = sum(1 for lead in enriched_leads if lead.get("has_tech_stack"))
    has_kw = sum(1 for lead in enriched_leads if len(lead.get("keywords_found", [])) > 0)
    avg_score = sum(lead.get("score", 0) for lead in enriched_leads) / total if total > 0 else 0
    
    sorted_leads = sorted(enriched_leads, key=lambda x: x.get("score", 0), reverse=True)
    
    print("\n✅ Enrichment complete")
    print(f"Total companies enriched: {total}")
    print(f"Companies with tech stack detected: {has_tech}")
    print(f"Companies with keywords matched: {has_kw}")
    print(f"Average score after enrichment: {avg_score:.1f}")
    
    print("\n🏆 Top 5 enriched leads:")
    for i, lead in enumerate(sorted_leads[:5], 1):
        name = lead.get('company_name', 'Unknown')
        score = lead.get('score', 0)
        prio = lead.get('priority', 'Unknown')
        techs = ", ".join(lead.get('tech_stack', []))
        print(f"{i}. {name} — Score: {score} — Tech: {techs} — Priority: {prio}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Application Thread Crash: {e}")
