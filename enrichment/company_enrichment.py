import time
import random
import requests
import os
import json
import re
from bs4 import BeautifulSoup

TECH_STACK_KEYWORDS = ["react", "vue", "angular", "python", "django", "node", "shopify", "wordpress", "webflow", "hubspot", "salesforce", "aws", "google cloud", "azure", "stripe"]

def get_icp_keywords():
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config', 'icp_config.json'))
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return [k.lower() for k in config.get("icp", {}).get("keywords", [])]
    except Exception:
        return ["automation", "digital transformation", "growth", "scaling"]

def enrich_company_data(company):
    """Enriches company data by actively probing remote domains for signals."""
    website = company.get("website", "")
    if not website:
        return {}
        
    enriched_data = {
        "tech_stack": [],
        "keywords_found": [],
        "description": "",
        "social_links": {
            "linkedin": "",
            "twitter": "",
            "facebook": ""
        },
        "has_tech_stack": False
    }

    try:
        if not website.startswith(('http://', 'https://')):
            website = 'https://' + website
            
        time.sleep(random.uniform(2, 5))
        
        headers = {
            "User-Agent": "LeadAura Enrichment Engine/1.0 (+http://leadaura-platform.com)"
        }
        response = requests.get(website, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text(separator=' ', strip=True).lower()
        
        # 1. Tech stack detection
        for tech in TECH_STACK_KEYWORDS:
            if re.search(r'\b' + re.escape(tech) + r'\b', text_content):
                label = 'AWS' if tech == 'aws' else tech.title()
                enriched_data["tech_stack"].append(label)
                
        if enriched_data["tech_stack"]:
            enriched_data["has_tech_stack"] = True
            
        # 2. Page Keywords overlap checking
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        desc = meta_desc['content'].strip() if meta_desc and meta_desc.has_attr('content') else ""
        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        
        full_meta = f"{title} {desc}".lower()
        icp_keywords = get_icp_keywords()
        
        for kw in icp_keywords:
            if kw in full_meta:
                enriched_data["keywords_found"].append(kw)
                
        # 3. Text Body Description inference
        for p in soup.find_all('p'):
            pt = p.get_text(strip=True)
            if len(pt) > 50:
                enriched_data["description"] = pt
                break
                
        if not enriched_data["description"]:
            enriched_data["description"] = desc 
            
        # 4. Social logic evaluation 
        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'linkedin.com/company' in href:
                enriched_data["social_links"]["linkedin"] = href
            elif ('twitter.com/' in href or 'x.com/' in href) and 'share' not in href and 'intent' not in href:
                enriched_data["social_links"]["twitter"] = href
            elif 'facebook.com/' in href and 'sharer' not in href:
                enriched_data["social_links"]["facebook"] = href
                
    except Exception as e:
        print(f"⚠️ Error mapping metrics from {website}: {e}")
        
    return enriched_data
