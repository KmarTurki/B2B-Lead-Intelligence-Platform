import time
import random
import requests
from bs4 import BeautifulSoup
from urllib import robotparser
from urllib.parse import urlparse

class BaseScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "LeadAuraBot/1.0 (+http://leadaura-platform.com/scrapers)"
        })
        self.rp = robotparser.RobotFileParser()
        self.robots_loaded = {}

    def _check_robots(self, url):
        """Internal helper to respect robots.txt rules."""
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        if base_url not in self.robots_loaded:
            self.rp.set_url(f"{base_url}/robots.txt")
            try:
                self.rp.read()
                self.robots_loaded[base_url] = True
            except Exception:
                # Default to polite scraping if robots.txt is inaccessible
                self.robots_loaded[base_url] = False 
                
        if self.robots_loaded[base_url]:
            return self.rp.can_fetch(self.session.headers["User-Agent"], url)
        return True

    def scrape(self, url):
        """
        Public method to scrape an arbitrary URL sequentially.
        Adds random polling intervals and performs try/except handling.
        """
        if not self._check_robots(url):
            print(f"⚠️ Warning: robots.txt disallows scraping {url}")
            return []
            
        try:
            # Respectful delay between 2 and 5 seconds
            sleep_time = random.uniform(2.0, 5.0)
            time.sleep(sleep_time)
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            return self.parse(soup, url)
            
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            return []

    def parse(self, soup, url):
        """Abstract parsing method extended by subclasses."""
        return []
