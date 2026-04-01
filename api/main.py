import sys
import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.firebase_reader import FirebaseReader
from api.models import StatsResponse, PipelineResponse
from ingestion.run_ingestion import DirectoryScraper, FreeAPICollector, FirebaseWriter
from scoring.firebase_scorer import FirebaseScorer
from enrichment.firebase_enricher import FirebaseEnricher

app = FastAPI(title="LeadAura API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

reader = FirebaseReader()

@app.get("/")
async def root():
    """Returns basic API info mapping platform version descriptors."""
    return {
        "platform": "LeadAura",
        "version": "1.0.0",
        "status": "running",
        "endpoints": ["/leads", "/top-leads", "/stats", "/search"]
    }

@app.get("/leads")
async def get_leads(
    industry: Optional[str] = None,
    location: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 20
):
    """Retrieves standard leads dynamically handling primitive state params."""
    try:
        data = reader.get_all_leads(industry, location, priority, limit)
        return {
            "total": len(data),
            "leads": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/top-leads")
async def get_top_leads(limit: int = 20):
    """Returns specifically prioritized (High) leads recursively ranking lists."""
    try:
        data = reader.get_all_leads(priority="High", limit=limit)
        sorted_data = sorted(data, key=lambda x: x.get("score", 0), reverse=True)
        return {
            "total": len(sorted_data),
            "leads": sorted_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/leads/{company_name}")
async def get_lead(company_name: str):
    """Returns a single documented lead mapping exact string parameters."""
    try:
        data = reader.get_lead_by_name(company_name)
        if not data:
            raise HTTPException(status_code=404, detail="Lead not found")
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Calculates metadata aggregation metrics across the active enriched indices."""
    try:
        return reader.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search")
async def search_leads(q: str = Query(..., min_length=1)):
    """Matches partial substring targets against company descriptions and text vectors."""
    try:
        return reader.search_leads(q)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run-pipeline", response_model=PipelineResponse)
async def run_pipeline():
    """Triggers end to end automated generation."""
    try:
        scraper = DirectoryScraper()
        scraped_companies = scraper.scrape_directory("https://www.europages.co.uk/en/companies", max_pages=1)
        api_collector = FreeAPICollector()
        enriched_scraped = api_collector.enrich(scraped_companies)
        writer = FirebaseWriter()
        saved_ingest = writer.write_companies(enriched_scraped)
        
        scorer = FirebaseScorer()
        scored_leads = scorer.process_all_raw_leads()
        
        enricher = FirebaseEnricher()
        enriched_leads = enricher.enrich_all_scored_leads()
        
        return {
            "status": "Pipeline complete",
            "companies_scraped": saved_ingest,
            "companies_scored": len(scored_leads),
            "companies_enriched": len(enriched_leads)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline exception error runtime: {e}")
