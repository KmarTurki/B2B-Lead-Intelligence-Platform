from urllib.parse import urlparse

def extract_domain(website):
    """Cleanly extracts the root domain from any structured generic URL."""
    if not website:
        return ""
    if not website.startswith(('http://', 'https://')):
        website = 'http://' + website
        
    parsed = urlparse(website)
    domain = parsed.netloc
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain

def generate_email_patterns(domain, first_name="", last_name=""):
    """Generates the most common email patterns mapping corporate contexts."""
    domain = extract_domain(domain)
    if not domain:
        return []
        
    first_name = first_name.lower().strip()
    last_name = last_name.lower().strip()
    
    patterns = [
        f"contact@{domain}",
        f"info@{domain}",
        f"hello@{domain}"
    ]
    
    if first_name and last_name:
        patterns.extend([
            f"{first_name}@{domain}",
            f"{first_name}.{last_name}@{domain}",
            f"{first_name[0]}{last_name}@{domain}"
        ])
    return patterns

def guess_best_email(domain):
    """Returns the most likely baseline generic contact email."""
    extracted = extract_domain(domain)
    if not extracted:
        return ""
    return f"info@{extracted}"
