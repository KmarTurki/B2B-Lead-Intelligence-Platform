import os
import json

def load_icp():
    """Loads the ICP configuration from config/icp_config.json"""
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config', 'icp_config.json'))
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading ICP config: {e}")
        return {}

def score_lead(company):
    """Scores a single company based on dynamic ICP criteria weights."""
    config = load_icp()
    icp = config.get("icp", {})
    weights = config.get("scoring_weights", {})
    
    score = 0
    
    # 1. Industry match (30 points)
    target_industries = [ind.lower() for ind in icp.get("target_industries", [])]
    company_industry = company.get("industry", "").lower()
    if any(target in company_industry for target in target_industries):
        score += weights.get("industry_match", 30)
        
    # 2. Size match (25 points)
    min_emp = icp.get("min_employees", 10)
    max_emp = icp.get("max_employees", 200)
    emp_count = company.get("employee_count", 0)
    # Default 0 employees often means unknown, depending on requirements we might skip it
    if min_emp <= emp_count <= max_emp:
        score += weights.get("size_match", 25)
        
    # 3. Location match (20 points)
    target_locations = [loc.lower() for loc in icp.get("target_locations", [])]
    company_location = company.get("location", "").lower()
    if any(target in company_location for target in target_locations):
        score += weights.get("location_match", 20)
        
    # 4. Tech stack detected (15 points)
    if company.get("has_tech_stack"):
        score += weights.get("tech_stack_detected", 15)
        
    # 5. Keyword match (10 points)
    keywords = [kw.lower() for kw in icp.get("keywords", [])]
    description = company.get("description", "").lower()
    if any(kw in description for kw in keywords):
        score += weights.get("keyword_match", 10)
        
    return score

def get_priority(score):
    """Categorizes qualitative priority based on numerical score."""
    if score >= 70:
        return "High"
    elif score >= 40:
        return "Medium"
    else:
        return "Low"

def score_all_leads(companies):
    """Scores a sequence of company dictionaries and bubbles highest matches via sort."""
    for company in companies:
        company["score"] = score_lead(company)
        company["priority"] = get_priority(company["score"])
        
    return sorted(companies, key=lambda x: x["score"], reverse=True)
