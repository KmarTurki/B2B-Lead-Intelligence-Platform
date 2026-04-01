from pydantic import BaseModel
from typing import List, Optional, Dict

class CompanyBase(BaseModel):
    company_name: str
    website: str
    industry: Optional[str] = "Unknown"
    location: Optional[str] = "Unknown"
    employee_count: Optional[int] = 0
    source: Optional[str] = ""

class ScoredLead(CompanyBase):
    score: int = 0
    priority: str = "Low"

class EnrichedLead(ScoredLead):
    tech_stack: List[str] = []
    has_tech_stack: bool = False
    keywords_found: List[str] = []
    description: Optional[str] = ""
    social_links: Dict[str, str] = {}
    contact_email: Optional[str] = ""
    predicted_emails: List[str] = []

class StatsResponse(BaseModel):
    total_leads: int
    high_priority: int
    medium_priority: int
    low_priority: int
    average_score: float
    top_industries: List[str]
    top_locations: List[str]
    leads_with_tech_stack: int

class PipelineResponse(BaseModel):
    status: str
    companies_scraped: int
    companies_scored: int
    companies_enriched: int
