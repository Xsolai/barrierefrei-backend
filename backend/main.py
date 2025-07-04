from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import traceback
import logging
from analyzers.accessibility_checker import AccessibilityChecker
from analyzers.website_crawler import WebsiteCrawler
from analyzers.accessibility_criteria import AccessibilityCriteria
from analyzers.criteria_mapper import CriteriaMapper
from services.supabase_service import SupabaseService
from pdf_generator import PDFReportGenerator
import sys
import json
import asyncio
import uuid
from datetime import datetime, timedelta
import os
from pathlib import Path
from services.stripe_service import StripeService
from contextlib import asynccontextmanager
import config

# Logging-Konfiguration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('backend.log')
    ]
)
logger = logging.getLogger(__name__)

# Speicher für laufende Analysen
running_analyses = {}

# Global Services
stripe_service = None

def init_stripe_service():
    """Initialisiert den Stripe Service bei Serverstart"""
    global stripe_service
    try:
        stripe_service = StripeService()
        logger.info("Stripe Service erfolgreich initialisiert")
    except Exception as e:
        logger.warning(f"Stripe Service konnte nicht initialisiert werden: {e}")
        stripe_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan-Event-Handler für FastAPI - ersetzt die veralteten @app.on_event"""
    # Startup
    logger.info("WCAG Analyzer API startet...")
    init_stripe_service()
    yield
    # Shutdown (falls benötigt)
    logger.info("WCAG Analyzer API wird beendet...")

app = FastAPI(title="BarrierefreiCheck API", lifespan=lifespan)

# CORS-Konfiguration
app.add_middleware(
    CORSMiddleware,
        allow_origins=[
        config.FRONTEND_URL,      # Primäre Frontend URL aus ENV
        config.BACKEND_URL,       # Backend URL aus ENV  
        "http://localhost:3000",  # Für lokale Entwicklung
        "http://localhost:3001",  # Für lokale Entwicklung (alternativer Port)
        "http://localhost:3002",  # Für lokale Entwicklung (alternativer Port)
        "http://localhost:8080",  # Für lokale Entwicklung
        # Production URLs werden jetzt über ENV-Variablen gesteuert (FRONTEND_URL)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    url: str
    checkpoints: Optional[List[str]] = None
    depth: Optional[int] = 1
    max_pages: Optional[int] = 100
    plan: Optional[str] = "basic"  # basic, pro, enterprise
    user_id: Optional[str] = None

class PaymentRequest(BaseModel):
    plan_id: str
    website_url: str
    customer_email: str
    user_id: str
    price_amount: int  # in Cent
    page_count: Optional[int] = 1
    upgrades: Optional[list] = []
    upgrade_details: Optional[Dict[str, Any]] = {}  # Detaillierte Upgrade-Informationen für Line Items
    metadata: Optional[Dict[str, Any]] = {}
    coupon_code: Optional[str] = None  # Rabattcode
    origin_url: Optional[str] = None # Hinzugefügt für dynamische Redirects

class AnalysisStatus(BaseModel):
    job_id: str
    status: str  # "running", "completed", "failed"
    progress: int  # 0-100
    message: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class PaymentWebhookRequest(BaseModel):
    session_id: str

class CouponValidationRequest(BaseModel):
    coupon_code: str

class PageCountRequest(BaseModel):
    url: str

@app.get("/")
async def root():
    return {"message": "Willkommen bei der BarrierefreiCheck API"}

@app.get("/health")
async def health_check():
    """Health-Check-Endpunkt für Monitoring und Startup-Verification"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "stripe_service": stripe_service is not None,
            "api": True
        }
    }

@app.get("/payment-test/success")
async def payment_test_success(session_id: str = None):
    """Test-Endpunkt für erfolgreiche Zahlungen (Entwicklung)"""
    return {
        "message": "✅ Payment erfolgreich!",
        "session_id": session_id,
        "note": "Dies ist ein Test-Endpunkt für die Entwicklung",
        "next_steps": [
            "In Production wird hier zum Frontend weitergeleitet",
            "Prüfen Sie /analyze-status/{job_id} für den Analyse-Status"
        ]
    }

@app.get("/payment-test/canceled")
async def payment_test_canceled():
    """Test-Endpunkt für abgebrochene Zahlungen (Entwicklung)"""
    return {
        "message": "❌ Payment abgebrochen",
        "note": "Dies ist ein Test-Endpunkt für die Entwicklung",
        "next_steps": [
            "In Production wird hier zum Frontend weitergeleitet",
            "Benutzer kann eine neue Zahlung starten"
        ]
    }

@app.get("/test")
async def test_analysis(url: Optional[str] = "https://www.example.com"):
    """
    Test-Endpunkt für die Barrierefreiheitsanalyse.
    Analysiert eine komplexe Website mit verschiedenen Barrierefreiheitselementen.
    
    Args:
        url: Die zu testende URL. Standardmäßig example.com.
    """
    try:
        logger.info(f"Starte Test-Analyse für {url}")
        
        # Website crawlen
        crawler = WebsiteCrawler()
        logger.info("Starte Website-Crawling für Test-Endpunkt")
        crawl_results = crawler.crawl_website(url, max_pages=1) # Nur 1 Seite für schnellen Test
        logger.info(f"Crawl-Ergebnisse für Test: {json.dumps(crawl_results, indent=2, ensure_ascii=False)}")

        if not crawl_results or "error" in crawl_results or not crawl_results.get("data"):
            logger.error(f"Fehler oder keine Daten beim Crawlen für Test: {crawl_results}")
            raise HTTPException(
                status_code=500,
                detail={"message": "Fehler beim Crawlen der Test-URL", "crawl_results": crawl_results}
            )
        
        # Barrierefreiheit prüfen
        checker = AccessibilityChecker()
        logger.info("Starte Barrierefreiheitsanalyse für Test-Endpunkt")
        accessibility_results = checker.analyze_website(url, depth=1)
        logger.info(f"Accessibility-Ergebnisse für Test: {json.dumps(accessibility_results, indent=2, ensure_ascii=False)}")

        if not isinstance(accessibility_results, dict) or "error" in accessibility_results:
            logger.error(f"Fehler oder ungültige Ergebnisse von AccessibilityChecker: {accessibility_results}")
            # Um den Fehler zu demonstrieren, geben wir hier die fehlerhaften Results direkt zurück
            # Im produktiven Endpunkt würden wir hier einen HTTPException werfen
            categorized_results = {"error": "Fehler bei Barrierefreiheitsanalyse", "details": accessibility_results}
            mapped_results = {"error": "Fehler bei Barrierefreiheitsanalyse", "details": accessibility_results}
        else:
            # Ergebnisse kategorisieren
            criteria = AccessibilityCriteria()
            logger.info("Starte Kategorisierung der Ergebnisse für Test-Endpunkt")
            categorized_results = criteria.categorize_results(crawl_results, accessibility_results)
            logger.info(f"Kategorisierte Ergebnisse für Test: {json.dumps(categorized_results, indent=2, ensure_ascii=False)}")
            
            # Daten den Prüfkriterien zuordnen
            mapper = CriteriaMapper()
            logger.info("Starte Zuordnung zu Prüfkriterien für Test-Endpunkt")
            mapped_results = mapper.map_data_to_criteria(crawl_results, accessibility_results)
            logger.info(f"Gemappte Ergebnisse für Test: {json.dumps(mapped_results, indent=2, ensure_ascii=False)}")

        # Detaillierte Testergebnisse
        test_results = {
            "status": "success",
            "url": url,
            "crawl_info": {
                "pages_crawled": crawl_results.get("pages_crawled", 0),
                "base_url": crawl_results.get("base_url", url)
            },
            "extracted_data_completeness": {
                "html_structure": bool(crawl_results.get("data")),
                "accessibility_features": isinstance(accessibility_results, dict) and "error" not in accessibility_results,
                "wcag_categories": isinstance(categorized_results, dict) and "error" not in categorized_results,
                "criteria_mapping": isinstance(mapped_results, dict) and "error" not in mapped_results
            },
            "data_samples": {
                "structure_sample": list(crawl_results.get("data", {}).keys())[:2],  # Erste zwei URLs
                "accessibility_sample": {
                    "violations": accessibility_results.get("violations", [])[:2] if isinstance(accessibility_results, dict) else [],
                    "warnings": accessibility_results.get("warnings", [])[:2] if isinstance(accessibility_results, dict) else [],
                    "passed": accessibility_results.get("passed", [])[:2] if isinstance(accessibility_results, dict) else []
                },
                "categorization_sample": categorized_results if isinstance(categorized_results, dict) else {},
                "mapping_sample": mapped_results if isinstance(mapped_results, dict) else {}
            }
        }
        
        logger.info("Test-Analyse erfolgreich abgeschlossen")
        return test_results
        
    except Exception as e:
        logger.error(f"Fehler im Test-Endpunkt /test: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Fehler bei der Test-Analyse",
                "error": str(e),
                "type": "test_endpoint_error"
            }
        )

@app.post("/analyze")
async def analyze_website(request: AnalysisRequest):
    try:
        logger.info(f"Starte Analyse für URL: {request.url}")
        
        # Website crawlen
        crawler = WebsiteCrawler()
        logger.info("Starte Website-Crawling")
        
        try:
            crawl_results = crawler.crawl_website(request.url, request.max_pages)
        except Exception as e:
            logger.error(f"Fehler beim Crawlen: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "Fehler beim Crawlen der Website",
                    "error": str(e),
                    "type": "crawl_error"
                }
            )
        
        if "error" in crawl_results:
            logger.error(f"Crawling-Fehler: {crawl_results['error']}")
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "Fehler beim Crawlen der Website",
                    "error": crawl_results['error'],
                    "type": "crawl_error"
                }
            )
        
        logger.info("Website-Crawling erfolgreich abgeschlossen")
        
        # Barrierefreiheit prüfen
        checker = AccessibilityChecker()
        logger.info("Starte Barrierefreiheitsanalyse")
        
        try:
            accessibility_results = checker.analyze_website(request.url, request.depth)
        except Exception as e:
            logger.error(f"Fehler bei der Barrierefreiheitsanalyse: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "Fehler bei der Barrierefreiheitsanalyse",
                    "error": str(e),
                    "type": "accessibility_error"
                }
            )
        
        if isinstance(accessibility_results, dict) and "error" in accessibility_results:
            logger.error(f"Accessibility-Fehler: {accessibility_results['error']}")
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "Fehler bei der Barrierefreiheitsanalyse",
                    "error": accessibility_results['error'],
                    "type": "accessibility_error"
                }
            )
        
        logger.info("Barrierefreiheitsanalyse erfolgreich abgeschlossen")
        
        # Ergebnisse kategorisieren
        criteria = AccessibilityCriteria()
        logger.info("Starte Kategorisierung der Ergebnisse")
        
        try:
            categorized_results = criteria.categorize_results(crawl_results, accessibility_results)
        except Exception as e:
            logger.error(f"Fehler bei der Kategorisierung: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "Fehler bei der Kategorisierung der Ergebnisse",
                    "error": str(e),
                    "type": "categorization_error"
                }
            )
        
        if isinstance(categorized_results, dict) and "error" in categorized_results:
            logger.error(f"Kategorisierungs-Fehler: {categorized_results['error']}")
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "Fehler bei der Kategorisierung der Ergebnisse",
                    "error": categorized_results['error'],
                    "type": "categorization_error"
                }
            )
        
        logger.info("Kategorisierung erfolgreich abgeschlossen")
        
        # Daten den Prüfkriterien zuordnen
        mapper = CriteriaMapper()
        logger.info("Starte Zuordnung zu Prüfkriterien")
        
        try:
            mapped_results = mapper.map_data_to_criteria(crawl_results, accessibility_results)
        except Exception as e:
            logger.error(f"Fehler bei der Zuordnung zu Prüfkriterien: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "Fehler bei der Zuordnung zu Prüfkriterien",
                    "error": str(e),
                    "type": "mapping_error"
                }
            )
        
        if isinstance(mapped_results, dict) and "error" in mapped_results:
            logger.error(f"Mapping-Fehler: {mapped_results['error']}")
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "Fehler bei der Zuordnung zu Prüfkriterien",
                    "error": mapped_results['error'],
                    "type": "mapping_error"
                }
            )
        
        logger.info("Zuordnung zu Prüfkriterien erfolgreich abgeschlossen")
        
        # Ergebnisse zusammenführen
        try:
            results = {
                "status": "success",
                "url": request.url,
                "crawl_info": {
                    "pages_crawled": crawl_results["pages_crawled"],
                    "base_url": crawl_results["base_url"]
                },
                "site_structure": crawl_results["data"],
                "accessibility_analysis": accessibility_results,
                "wcag_categorization": categorized_results,
                "criteria_mapping": mapped_results,
                "summary": {
                    "total_pages": len(crawl_results["data"]),
                    "violations": len(accessibility_results.get("violations", [])),
                    "warnings": len(accessibility_results.get("warnings", [])),
                    "passed": len(accessibility_results.get("passed", []))
                }
            }
            
            # Berechne Gesamtscore
            total_issues = (
                len(accessibility_results.get("violations", [])) + 
                len(accessibility_results.get("warnings", [])) * 0.5
            )
            results["accessibility_score"] = max(0, 100 - total_issues * 5)
            
            logger.info("Analyse erfolgreich abgeschlossen")
            return results
            
        except Exception as e:
            logger.error(f"Fehler beim Zusammenführen der Ergebnisse: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "Fehler beim Zusammenführen der Ergebnisse",
                    "error": str(e),
                    "type": "results_error"
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unerwarteter Fehler: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Ein unerwarteter Fehler ist aufgetreten",
                "error": str(e),
                "type": "unexpected_error"
            }
        )

@app.post("/analyze-complete")
async def analyze_complete(request: AnalysisRequest):
    """
    Führt die vollständige WCAG-Analyse mit allen Expert-Prompts durch.
    Dies ist die umfangreiche Analyse, die mehrere Minuten dauern kann.
    """
    try:
        logger.info(f"Starte VOLLSTÄNDIGE WCAG-Analyse für URL: {request.url}")
        
        # Importiere die vollständige Analyse
        from run_complete_analysis import CompleteWCAGAnalyzer
        
        # Erstelle Analyzer-Instanz
        analyzer = CompleteWCAGAnalyzer()
        
        # Führe vollständige Analyse durch
        logger.info("Starte umfangreiche WCAG-Analyse mit Expert-Prompts...")
        analysis_results = analyzer.run_complete_analysis(
            request.url, 
            max_pages=request.max_pages or 5
        )
        
        if "error" in analysis_results:
            logger.error(f"Vollständige Analyse fehlgeschlagen: {analysis_results['error']}")
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "Fehler bei der vollständigen WCAG-Analyse",
                    "error": analysis_results['error'],
                    "type": "complete_analysis_error"
                }
            )
        
        logger.info("Vollständige WCAG-Analyse erfolgreich abgeschlossen")
        
        # Bereite die Antwort vor
        response = {
            "status": "success",
            "url": request.url,
            "timestamp": analysis_results["meta"]["timestamp"],
            "crawl_info": analysis_results["crawling"],
            "accessibility_check": analysis_results["accessibility_check"],
            "ai_analyses": analysis_results["ai_analyses"],
            "summary": analysis_results["summary"],
            "token_usage": analysis_results["token_usage"],
            "message": "Vollständige WCAG-Analyse mit Expert-Prompts abgeschlossen"
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unerwarteter Fehler bei vollständiger Analyse: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Ein unerwarteter Fehler ist aufgetreten",
                "error": str(e),
                "type": "unexpected_error"
            }
        )

@app.post("/analyze-complete-async")
async def analyze_complete_async(request: AnalysisRequest, x_user_id: Optional[str] = Header(None)):
    """
    Startet die vollständige WCAG-Analyse asynchron und gibt eine Job-ID zurück.
    Speichert den Job-Status in Supabase.
    """
    try:
        # Erstelle Supabase-Service
        supabase = SupabaseService()
        
        # Erstelle Job in Supabase mit User-ID
        job_id = supabase.create_analysis_job(request.url, request.plan, x_user_id) if supabase.client else str(uuid.uuid4())
        
        logger.info(f"Starte asynchrone WCAG-Analyse mit Job-ID: {job_id} für URL: {request.url}, User: {x_user_id}")
        
        # Initialisiere Job-Status (für In-Memory-Tracking)
        running_analyses[job_id] = {
            "status": "running",
            "progress": 0,
            "message": "Analyse gestartet...",
            "started_at": datetime.now().isoformat(),
            "url": request.url,
            "plan": request.plan,
            "user_id": x_user_id
        }
        
        # Starte Analyse in Background-Task
        asyncio.create_task(run_analysis_async(job_id, request))
        
        return {
            "job_id": job_id,
            "message": "Analyse wurde gestartet",
            "status_url": f"/analyze-status/{job_id}",
            "plan": request.plan
        }
        
    except Exception as e:
        logger.error(f"Fehler beim Starten der asynchronen Analyse: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Fehler beim Starten der Analyse",
                "error": str(e),
                "type": "startup_error"
            }
        )

async def run_analysis_async(job_id: str, request: AnalysisRequest):
    """
    Führt die Analyse asynchron aus und aktualisiert den Status in Supabase.
    """
    try:
        # Importiere die vollständige Analyse
        from run_complete_analysis import CompleteWCAGAnalyzer
        
        # Prüfe ob Job in running_analyses existiert, falls nicht, initialisiere ihn
        if job_id not in running_analyses:
            logger.warning(f"Job {job_id} nicht in running_analyses gefunden - initialisiere ihn")
            running_analyses[job_id] = {
                "status": "running",
                "progress": 0,
                "message": "Analyse initialisiert...",
                "started_at": datetime.now().isoformat(),
                "url": request.url,
                "plan": request.plan,
                "user_id": getattr(request, 'user_id', None)
            }
        
        # Update Status
        running_analyses[job_id]["progress"] = 10
        running_analyses[job_id]["message"] = "Initialisiere Analyzer..."
        
        # Erstelle Analyzer-Instanz mit Supabase Job-ID
        analyzer = CompleteWCAGAnalyzer(supabase_job_id=job_id)
        
        # Führe vollständige Analyse durch
        logger.info(f"Job {job_id}: Starte umfangreiche WCAG-Analyse...")
        running_analyses[job_id]["progress"] = 20
        running_analyses[job_id]["message"] = "Crawle Website..."
        
        analysis_results = analyzer.run_complete_analysis(
            request.url, 
            max_pages=request.max_pages or 5
        )
        
        if "error" in analysis_results:
            logger.error(f"Job {job_id}: Analyse fehlgeschlagen: {analysis_results['error']}")
            running_analyses[job_id]["status"] = "failed"
            running_analyses[job_id]["error"] = analysis_results['error']
            return
        
        logger.info(f"Job {job_id}: Analyse erfolgreich abgeschlossen")
        
        # Bereite die Antwort vor
        response = {
            "status": "success",
            "url": request.url,
            "timestamp": analysis_results["meta"]["timestamp"],
            "crawl_info": analysis_results["crawling"],
            "accessibility_check": analysis_results["accessibility_check"],
            "ai_analyses": analysis_results["ai_analyses"],
            "summary": analysis_results["summary"],
            "token_usage": analysis_results["token_usage"],
            "message": "Vollständige WCAG-Analyse mit Expert-Prompts abgeschlossen"
        }
        
        # Update Status auf completed
        running_analyses[job_id]["status"] = "completed"
        running_analyses[job_id]["progress"] = 100
        running_analyses[job_id]["message"] = "Analyse abgeschlossen"
        running_analyses[job_id]["result"] = response
        running_analyses[job_id]["completed_at"] = datetime.now().isoformat()
        
    except Exception as e:
        logger.error(f"Job {job_id}: Unerwarteter Fehler: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Prüfe erneut ob Job existiert, bevor Update
        if job_id in running_analyses:
            running_analyses[job_id]["status"] = "failed"
            running_analyses[job_id]["error"] = str(e)
            running_analyses[job_id]["message"] = "Fehler bei der Analyse"
        else:
            logger.error(f"Job {job_id} kann nicht aktualisiert werden - nicht in running_analyses gefunden")

@app.get("/analyze-status/{job_id}")
async def get_analysis_status(job_id: str):
    """
    Gibt den aktuellen Status einer laufenden Analyse zurück.
    Prüft zuerst In-Memory, dann Supabase.
    """
    logger.info(f"📊 Status-Anfrage für Job: {job_id}")
    
    # Debug: Zeige alle verfügbaren Jobs
    logger.info(f"🔍 Verfügbare In-Memory Jobs: {list(running_analyses.keys())}")
    
    # Prüfe zuerst In-Memory
    if job_id in running_analyses:
        job_data = running_analyses[job_id]
        logger.info(f"✅ Job {job_id} in In-Memory gefunden: {job_data['status']} ({job_data.get('progress', 0)}%)")
        return AnalysisStatus(
            job_id=job_id,
            status=job_data["status"],
            progress=job_data.get("progress", 0),
            message=job_data.get("message", ""),
            result=job_data.get("result"),
            error=job_data.get("error")
        )
    
    # Prüfe Supabase
    logger.info(f"🔍 Job {job_id} nicht in In-Memory, prüfe Supabase...")
    try:
        supabase = SupabaseService()
        if supabase.client:
            job_status = supabase.get_job_status(job_id)
            if job_status:
                logger.info(f"✅ Job {job_id} in Supabase gefunden: {job_status}")
                
                # Hole auch die Ergebnisse, falls die Analyse abgeschlossen ist
                if job_status["status"] == "completed":
                    try:
                        results = supabase.get_job_results(job_id)
                        logger.info(f"📋 Job {job_id} Ergebnisse geladen")
                        return AnalysisStatus(
                            job_id=job_id,
                            status=job_status["status"],
                            progress=job_status.get("progress", 100),
                            message="Analyse abgeschlossen",
                            result=results.get("report"),
                            error=None
                        )
                    except Exception as e:
                        logger.warning(f"⚠️ Fehler beim Laden der Ergebnisse für Job {job_id}: {e}")
                        # Gib trotzdem den Status zurück, auch wenn Ergebnisse nicht geladen werden können
                        return AnalysisStatus(
                            job_id=job_id,
                            status=job_status["status"],
                            progress=job_status.get("progress", 100),
                            message="Analyse abgeschlossen",
                            result=None,
                            error=None
                        )
                else:
                    return AnalysisStatus(
                        job_id=job_id,
                        status=job_status["status"],
                        progress=job_status.get("progress", 0),
                        message=job_status.get("message", "Analyse läuft..."),
                        result=None,
                        error=job_status.get("error_message")
                    )
            else:
                logger.warning(f"❌ Job {job_id} nicht in Supabase gefunden")
    except Exception as e:
        logger.error(f"❌ Fehler beim Abrufen des Job-Status aus Supabase: {e}")
    
    # Job nicht gefunden - gib einen hilfreichen Fehler mit verfügbaren Jobs zurück
    available_jobs = list(running_analyses.keys())
    logger.error(f"❌ Job {job_id} nicht gefunden (weder In-Memory noch Supabase)")
    logger.error(f"🔍 Verfügbare Jobs: {available_jobs}")
    
    raise HTTPException(
        status_code=404,
        detail={
            "message": "Job nicht gefunden", 
            "job_id": job_id,
            "available_jobs": available_jobs,
            "suggestion": "Prüfe die Job-ID in der URL oder starte eine neue Analyse"
        }
    )

@app.get("/analyze-results/{job_id}")
async def get_analysis_results(job_id: str):
    """
    Holt die vollständigen Analyseergebnisse aus Supabase.
    """
    supabase = SupabaseService()
    if not supabase.client:
        raise HTTPException(
            status_code=503,
            detail={"message": "Supabase-Service nicht verfügbar"}
        )
    
    results = supabase.get_job_results(job_id)
    if not results or not results.get("job"):
        raise HTTPException(
            status_code=404,
            detail={"message": "Job nicht gefunden", "job_id": job_id}
        )
    
    return {
        "job_id": job_id,
        "job": results["job"],
        "modules": results["modules"],
        "report": results["report"]
    }

@app.get("/jobs")
async def get_jobs(limit: int = 10, offset: int = 0, x_user_id: Optional[str] = Header(None)):
    """
    Listet alle Analyse-Jobs aus Supabase auf.
    Wenn User-ID angegeben, nur Jobs dieses Users.
    """
    supabase = SupabaseService()
    if not supabase.client:
        raise HTTPException(
            status_code=503,
            detail={"message": "Supabase-Service nicht verfügbar"}
        )
    
    try:
        if x_user_id:
            # Hole nur Jobs des spezifischen Users
            return supabase.get_user_jobs(x_user_id, limit, offset)
        else:
            # Hole alle Jobs (Admin-Ansicht)
            response = supabase.client.table('analysis_jobs').select('*').order('created_at', desc=True).range(offset, offset + limit - 1).execute()
            
            return {
                "jobs": response.data,
                "total": len(response.data),
                "limit": limit,
                "offset": offset
            }
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Jobs: {e}")
        raise HTTPException(
            status_code=500,
            detail={"message": "Fehler beim Abrufen der Jobs", "error": str(e)}
        )

@app.get("/jobs/{job_id}")
async def get_job_details(job_id: str, x_user_id: Optional[str] = Header(None)):
    """
    Holt Details eines spezifischen Jobs inklusive upgrade_tasks.
    """
    supabase = SupabaseService()
    if not supabase.client:
        raise HTTPException(
            status_code=503,
            detail={"message": "Supabase-Service nicht verfügbar"}
        )
    
    try:
        # Hole Job-Details
        job_response = supabase.client.table('analysis_jobs').select('*').eq('id', job_id).execute()
        
        if not job_response.data:
            raise HTTPException(
                status_code=404,
                detail={"message": "Job nicht gefunden", "job_id": job_id}
            )
        
        job = job_response.data[0]
        
        # Prüfe User-Berechtigung falls User-ID angegeben
        if x_user_id and job.get('user_id') != x_user_id:
            raise HTTPException(
                status_code=403,
                detail={"message": "Keine Berechtigung für diesen Job"}
            )
        
        # Hole upgrade_tasks für diesen Job
        tasks_response = supabase.client.table('upgrade_tasks')\
            .select('*')\
            .eq('job_id', job_id)\
            .order('created_at', desc=True)\
            .execute()
        
        # Füge upgrade_tasks zum Job hinzu
        job['upgrade_tasks'] = tasks_response.data or []
        
        return job
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Job-Details: {e}")
        raise HTTPException(
            status_code=500,
            detail={"message": "Fehler beim Abrufen der Job-Details", "error": str(e)}
        )

# Dashboard Endpoints für Teams
@app.get("/dashboard/certifier/tasks")
async def get_certifier_tasks(x_user_id: Optional[str] = Header(None)):
    """
    Holt alle verfügbaren Certificate Tasks für das Certifier Dashboard.
    """
    supabase = SupabaseService()
    if not supabase.client:
        raise HTTPException(
            status_code=503,
            detail={"message": "Supabase-Service nicht verfügbar"}
        )
    
    try:
        # Hole alle Certificate upgrade_tasks mit Job- und User-Details
        tasks_response = supabase.client.table('upgrade_tasks')\
            .select('''
                *,
                analysis_jobs!inner(
                    id,
                    url,
                    plan,
                    status,
                    created_at,
                    user_id
                )
            ''')\
            .eq('upgrade_type', 'certificate')\
            .eq('assigned_to', 'certifier')\
            .order('created_at', desc=False)\
            .execute()
        
        # Erweitere Tasks mit User-Profil-Informationen
        tasks = tasks_response.data or []
        
        for task in tasks:
            job = task.get('analysis_jobs')
            if job and job.get('user_id'):
                # Hole User-Profil (optional - falls verfügbar)
                try:
                    profile_response = supabase.client.table('user_profiles')\
                        .select('full_name')\
                        .eq('user_id', job['user_id'])\
                        .execute()
                    
                    if profile_response.data:
                        task['customer_profile'] = profile_response.data[0]
                except Exception as e:
                    logger.warning(f"Konnte User-Profil für {job['user_id']} nicht laden: {e}")
                    task['customer_profile'] = None
        
        logger.info(f"🏆 Certifier Dashboard: {len(tasks)} Certificate Tasks geladen")
        
        return {
            "tasks": tasks,
            "total_count": len(tasks),
            "pending_count": len([t for t in tasks if t.get('status') == 'requested']),
            "in_progress_count": len([t for t in tasks if t.get('status') == 'in_progress']),
            "completed_count": len([t for t in tasks if t.get('status') == 'completed'])
        }
        
    except Exception as e:
        logger.error(f"Fehler beim Laden der Certifier Tasks: {e}")
        raise HTTPException(
            status_code=500,
            detail={"message": "Fehler beim Laden der Certifier Tasks", "error": str(e)}
        )

@app.get("/dashboard/webdev/tasks")  
async def get_webdev_tasks(x_user_id: Optional[str] = Header(None)):
    """
    Holt alle verfügbaren Professional Fix Tasks für das Webdev Dashboard.
    """
    supabase = SupabaseService()
    if not supabase.client:
        raise HTTPException(
            status_code=503,
            detail={"message": "Supabase-Service nicht verfügbar"}
        )
    
    try:
        # Hole alle Professional Fix upgrade_tasks mit Job- und User-Details
        tasks_response = supabase.client.table('upgrade_tasks')\
            .select('''
                *,
                analysis_jobs!inner(
                    id,
                    url,
                    plan,
                    status,
                    created_at,
                    user_id
                )
            ''')\
            .eq('upgrade_type', 'professional_fix')\
            .eq('assigned_to', 'webdev')\
            .order('created_at', desc=False)\
            .execute()
        
        # Erweitere Tasks mit User-Profil-Informationen
        tasks = tasks_response.data or []
        
        for task in tasks:
            job = task.get('analysis_jobs')
            if job and job.get('user_id'):
                # Hole User-Profil (optional - falls verfügbar)
                try:
                    profile_response = supabase.client.table('user_profiles')\
                        .select('full_name')\
                        .eq('user_id', job['user_id'])\
                        .execute()
                    
                    if profile_response.data:
                        task['customer_profile'] = profile_response.data[0]
                except Exception as e:
                    logger.warning(f"Konnte User-Profil für {job['user_id']} nicht laden: {e}")
                    task['customer_profile'] = None
        
        logger.info(f"🔧 Webdev Dashboard: {len(tasks)} Professional Fix Tasks geladen")
        
        return {
            "tasks": tasks,
            "total_count": len(tasks),
            "pending_count": len([t for t in tasks if t.get('status') == 'requested']),
            "in_progress_count": len([t for t in tasks if t.get('status') == 'in_progress']),
            "completed_count": len([t for t in tasks if t.get('status') == 'completed'])
        }
        
    except Exception as e:
        logger.error(f"Fehler beim Laden der Webdev Tasks: {e}")
        raise HTTPException(
            status_code=500,
            detail={"message": "Fehler beim Laden der Webdev Tasks", "error": str(e)}
        )

# Task Management Endpoints
@app.put("/dashboard/tasks/{task_id}/status")
async def update_task_status(
    task_id: str, 
    new_status: str, 
    notes: Optional[str] = None,
    x_user_id: Optional[str] = Header(None)
):
    """
    Aktualisiert den Status einer upgrade_task.
    Erlaubte Status: requested, in_progress, completed, cancelled
    """
    supabase = SupabaseService()
    if not supabase.client:
        raise HTTPException(
            status_code=503,
            detail={"message": "Supabase-Service nicht verfügbar"}
        )
    
    # Validiere Status
    allowed_statuses = ['requested', 'in_progress', 'completed', 'cancelled']
    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail={"message": f"Ungültiger Status. Erlaubt: {', '.join(allowed_statuses)}"}
        )
    
    try:
        # Hole aktuelle Task-Details
        task_response = supabase.client.table('upgrade_tasks')\
            .select('*, analysis_jobs!inner(id, url, user_id)')\
            .eq('id', task_id)\
            .execute()
        
        if not task_response.data:
            raise HTTPException(
                status_code=404,
                detail={"message": "Task nicht gefunden"}
            )
        
        task = task_response.data[0]
        
        # Bereite Update-Daten vor
        update_data = {
            'status': new_status,
            'updated_at': datetime.now().isoformat()
        }
        
        # Füge Notizen hinzu falls vorhanden
        if notes:
            update_data['notes'] = notes
        
        # Setze Timestamps basierend auf Status
        if new_status == 'in_progress':
            update_data['started_at'] = datetime.now().isoformat()
            update_data['assigned_to_user_id'] = x_user_id
        elif new_status == 'completed':
            update_data['completed_at'] = datetime.now().isoformat()
            if not task.get('started_at'):
                update_data['started_at'] = datetime.now().isoformat()
        
        # Aktualisiere Task
        result = supabase.client.table('upgrade_tasks')\
            .update(update_data)\
            .eq('id', task_id)\
            .execute()
        
        if result.data:
            logger.info(f"✅ Task {task_id} Status aktualisiert auf '{new_status}' von User {x_user_id}")
            
            # Bei Completion: Kunden benachrichtigen
            if new_status == 'completed':
                logger.info(f"🎯 Task {task_id} ({task.get('upgrade_type')}) abgeschlossen - sollte Kunde benachrichtigen")
                # Hier könnte später E-Mail-Benachrichtigung implementiert werden
            
            return {
                "success": True,
                "task_id": task_id,
                "new_status": new_status,
                "message": f"Task Status erfolgreich auf '{new_status}' aktualisiert"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail={"message": "Task konnte nicht aktualisiert werden"}
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren des Task Status: {e}")
        raise HTTPException(
            status_code=500,
            detail={"message": "Fehler beim Aktualisieren des Task Status", "error": str(e)}
        )

@app.get("/download-pdf/{job_id}")
async def download_pdf(job_id: str):
    """
    Generiert ein PDF aus den Analyseergebnissen und stellt es zum Download bereit.
    """
    try:
        supabase = SupabaseService()
        if not supabase.client:
            raise HTTPException(
                status_code=503,
                detail={"message": "Supabase-Service nicht verfügbar"}
            )
        
        # Hole Job-Daten und Module aus Supabase
        results = supabase.get_job_results(job_id)
        if not results or not results.get("job"):
            raise HTTPException(
                status_code=404,
                detail={"message": "Job nicht gefunden", "job_id": job_id}
            )
        
        job_data = results["job"]
        modules_data = results.get("modules", [])
        
        logger.info(f"Generiere PDF für Job {job_id}: {job_data.get('url', 'unknown')}")
        
        # PDF-Generator initialisieren
        pdf_generator = PDFReportGenerator()
        
        # PDF erstellen
        try:
            pdf_path = pdf_generator.generate_pdf_from_job_data(
                job_id=job_id,
                job_data=job_data,
                modules_data=modules_data
            )
        except Exception as e:
            logger.error(f"Fehler bei PDF-Generation für Job {job_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail={"message": f"Fehler beim Generieren des PDF: {str(e)}"}
            )
        
        if not pdf_path or not os.path.exists(pdf_path):
            raise HTTPException(
                status_code=500,
                detail={"message": "PDF-Datei konnte nicht erstellt werden"}
            )
        
        # Sauberen Dateinamen erstellen
        clean_url = job_data.get('url', 'website').replace('https://', '').replace('http://', '').replace('/', '_').replace(':', '')
        filename = f"WCAG_Bericht_{clean_url}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        logger.info(f"PDF erfolgreich erstellt: {pdf_path}")
        
        return FileResponse(
            path=pdf_path, 
            filename=filename,
            media_type='application/pdf'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unerwarteter Fehler beim PDF-Download für Job {job_id}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Ein unerwarteter Fehler ist aufgetreten",
                "error": str(e),
                "job_id": job_id
            }
        )

@app.post("/cleanup-hanging-jobs")
async def cleanup_hanging_jobs():
    """
    Bereinigt hängende Jobs, die länger als 30 Minuten nicht aktualisiert wurden.
    """
    try:
        supabase = SupabaseService()
        if not supabase.client:
            raise HTTPException(
                status_code=503,
                detail={"message": "Supabase-Service nicht verfügbar"}
            )
        
        # Finde Jobs, die länger als 30 Minuten nicht aktualisiert wurden
        cutoff_time = (datetime.utcnow() - timedelta(minutes=30)).isoformat()
        
        # Hole alle laufenden Jobs, die länger als 30 Minuten nicht aktualisiert wurden
        response = supabase.client.table('analysis_jobs').select('*').eq('status', 'running').lt('updated_at', cutoff_time).execute()
        
        hanging_jobs = response.data
        cleaned_count = 0
        
        for job in hanging_jobs:
            job_id = job['id']
            
            # Markiere als fehlgeschlagen
            supabase.client.table('analysis_jobs').update({
                'status': 'failed',
                'error': 'Job nach 30 Minuten Inaktivität automatisch abgebrochen (Timeout)',
                'completed_at': datetime.utcnow().isoformat()
            }).eq('id', job_id).execute()
            
            # Entferne aus In-Memory-Dictionary falls vorhanden
            if job_id in running_analyses:
                del running_analyses[job_id]
            
            cleaned_count += 1
            logger.info(f"Hängender Job {job_id} bereinigt (inaktiv seit {job['updated_at']})")
        
        # Leere das gesamte In-Memory-Dictionary für einen sauberen Neustart
        running_analyses.clear()
        
        return {
            "message": f"{cleaned_count} hängende Jobs bereinigt",
            "cleaned_jobs": [job['id'] for job in hanging_jobs],
            "in_memory_cleared": True
        }
        
    except Exception as e:
        logger.error(f"Fehler beim Bereinigen hängender Jobs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Fehler beim Bereinigen hängender Jobs",
                "error": str(e)
            }
        )

# Payment Endpoints
@app.post("/create-payment-session")
async def create_payment_session(request: PaymentRequest):
    """
    Erstellt eine Stripe Checkout Session für die Zahlung
    """
    if not stripe_service:
        raise HTTPException(
            status_code=503,
            detail="Payment Service nicht verfügbar"
        )
    
    try:
        logger.info(f"Erstelle Payment Session für User {request.user_id}, Plan: {request.plan_id}")
        
        # Bestimme die URLs für Redirects
        if request.origin_url:
            # Wenn eine spezifische origin_url angegeben wurde, verwende diese
            base_url = request.origin_url.strip('/')
            cancel_url = f"{base_url}/payment/canceled"
            logger.info(f"Verwende spezifische origin_url: {base_url}")
        else:
            # Für Entwicklung: Verwende Frontend-URLs für echte Weiterleitung
            frontend_base = os.getenv('FRONTEND_BASE_URL', 'http://localhost:3000')
            
            # Korrigiere HTTPS zu HTTP für localhost
            if frontend_base.startswith('https://localhost'):
                frontend_base = frontend_base.replace('https://', 'http://')
                logger.warning(f"⚠️ HTTPS zu HTTP korrigiert für localhost: {frontend_base}")
            
            base_url = frontend_base
            cancel_url = f"{frontend_base}/payment/canceled"
            logger.info(f"🎯 Verwende Frontend-URLs: Base -> {base_url}")
        
        # Bestimme spezifische Success-URL basierend auf Plan-Typ
        if request.plan_id == 'professional_fix':
            success_url = f"{base_url}/payment/success/professional-fix?session_id={{CHECKOUT_SESSION_ID}}"
            logger.info(f"🔧 Professional Fix Success-URL: {success_url}")
        elif request.plan_id == 'certificate_only':
            success_url = f"{base_url}/payment/success/certificate?session_id={{CHECKOUT_SESSION_ID}}"
            logger.info(f"🏆 Certificate Success-URL: {success_url}")
        else:
            # Standard Analyse (basic, enterprise)
            success_url = f"{base_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
            logger.info(f"📊 Standard Analysis Success-URL: {success_url}")
        
        logger.info(f"🎯 Final URLs: Success -> {success_url}, Cancel -> {cancel_url}")
        
        # Erweiterte Metadaten für die Analyse
        metadata = {
            **request.metadata,
            "page_count": request.page_count,
            "upgrades": json.dumps(request.upgrades) if request.upgrades else "[]",
            "created_at": datetime.now().isoformat()
        }
        
        session_data = stripe_service.create_checkout_session(
            plan_id=request.plan_id,
            price_amount=request.price_amount,
            url=request.website_url,
            customer_email=request.customer_email,
            user_id=request.user_id,
            metadata=metadata,
            coupon_code=request.coupon_code,
            success_url=success_url,
            cancel_url=cancel_url,
            upgrade_details=request.upgrade_details
        )
        
        logger.info(f"Payment Session erstellt: {session_data['session_id']}")
        
        return {
            "success": True,
            "checkout_url": session_data["checkout_url"],
            "session_id": session_data["session_id"],
            "expires_at": session_data["expires_at"]
        }
        
    except Exception as e:
        logger.error(f"Fehler beim Erstellen der Payment Session: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Payment Session konnte nicht erstellt werden: {str(e)}"
        )

@app.post("/validate-coupon")
async def validate_coupon(request: CouponValidationRequest):
    """
    Validiert einen Rabattcode
    """
    if not stripe_service:
        raise HTTPException(
            status_code=503,
            detail="Payment Service nicht verfügbar"
        )
    
    try:
        result = stripe_service.validate_coupon(request.coupon_code)
        return result
        
    except Exception as e:
        logger.error(f"Fehler beim Validieren des Coupons: {str(e)}")
        return {
            "valid": False,
            "error": f"Fehler beim Validieren: {str(e)}"
        }

@app.get("/payment-status/{session_id}")
async def get_payment_status(session_id: str):
    """
    Ruft den Status einer Stripe Checkout Session ab.
    """
    if not stripe_service:
        raise HTTPException(status_code=503, detail="Stripe Service nicht verfügbar")
    
    try:
        logger.info(f"Rufe Payment-Status für Session-ID ab: {session_id}")
        session = stripe_service.get_checkout_session(session_id)
        
        # Prüfe Payment Status - bei manchen Payments (z.B. 100% Rabatt) gibt es keinen payment_intent
        if session.payment_intent:
            # Standard Payment mit PaymentIntent
            payment_intent = stripe_service.get_payment_intent(session.payment_intent)
            is_paid = payment_intent.status == 'succeeded'
            payment_status = payment_intent.status
            amount = payment_intent.amount
        else:
            # Kein PaymentIntent (z.B. bei 100% Rabatt) - prüfe Session Status direkt
            is_paid = session.payment_status == 'paid' and session.status == 'complete'
            payment_status = session.payment_status
            amount = session.amount_total
            logger.info(f"Kein PaymentIntent für Session {session_id} - verwende Session Status: payment_status={session.payment_status}, status={session.status}, is_paid={is_paid}")
        
        logger.info(f"Payment-Status für {session_id}: {'bezahlt' if is_paid else 'nicht bezahlt'}")

        return {
            "session_id": session_id,
            "payment_status": payment_status,
            "is_paid": is_paid,
            "amount": amount,
            "currency": session.currency,
            "metadata": session.metadata
        }
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Payment-Status für Session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen des Payment-Status: {str(e)}")

@app.post("/stripe-webhook")
async def stripe_webhook(request: Request):
    """
    Empfängt Webhooks von Stripe, um Zahlungen zu bestätigen und Analysen zu starten.
    """
    if not stripe_service:
        raise HTTPException(status_code=503, detail="Payment Service nicht verfügbar")
    
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    if not sig_header:
        logger.error("Webhook-Fehler: Fehlender stripe-signature Header")
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")
        
    try:
        event = stripe_service.construct_webhook_event(payload, sig_header)
        logger.info(f"✅ Stripe Webhook Event empfangen: {event['type']}")
        logger.info(f"🔍 Event Data: {json.dumps(event, indent=2, default=str)}")
    except Exception as e:
        logger.error(f"Webhook-Fehler bei der Signaturprüfung: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    # Nur auf erfolgreiche Checkout-Sessions reagieren
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        metadata = session.get('metadata', {})
        
        logger.info(f"🎯 Verarbeite 'checkout.session.completed' für Session: {session.id}")
        logger.info(f"📋 Session Metadata: {metadata}")
        
        try:
            # Extrahiere die notwendigen Daten aus den Metadaten
            url = metadata.get('website_url')
            plan = metadata.get('plan_id', 'basic')
            user_id = metadata.get('user_id')
            max_pages = int(metadata.get('page_count', '5'))
            
            logger.info(f"🔍 DEBUGGING: url={url}, plan='{plan}', user_id={user_id}")
            
            # Extrahiere Upgrades aus den Metadaten
            selected_upgrades = []
            upgrades_json = metadata.get('upgrades', '[]')
            try:
                if upgrades_json:
                    selected_upgrades = json.loads(upgrades_json)
                    logger.info(f"🎯 Upgrades aus Stripe-Metadaten extrahiert: {selected_upgrades}")
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️ Fehler beim Parsen der Upgrades aus Metadaten: {e}")
                selected_upgrades = []

            if not url or not user_id:
                logger.error(f"Webhook-Fehler: Fehlende 'website_url' oder 'user_id' in Metadaten für Session {session.id}")
                raise HTTPException(status_code=400, detail="Metadaten unvollständig")

            supabase = SupabaseService()
            
            logger.info(f"🔍 PLAN CHECK: plan='{plan}', type={type(plan)}, equals_professional_fix={plan == 'professional_fix'}")
            
            # WICHTIG: Unterscheidung zwischen Analyse-Käufen, Professional Fix und Certificate
            if plan == 'professional_fix':
                logger.info(f"🔧 ENTERING Professional Fix workflow für {url} von User {user_id}")
                
                # Verwende die exakte Job-ID aus den Stripe-Metadaten (beide möglichen Schlüssel prüfen)
                original_job_id = metadata.get('original_job_id') or metadata.get('existing_job_id')
                
                if not original_job_id:
                    logger.error(f"❌ Keine 'original_job_id' oder 'existing_job_id' in Stripe-Metadaten für Professional Fix gefunden")
                    raise HTTPException(status_code=400, detail="Job-ID fehlt in Metadaten")
                
                logger.info(f"🔍 Professional Fix für spezifische Job-ID: {original_job_id}")
                
                # Hole den spezifischen Job über Job-ID
                job_result = supabase.client.table('analysis_jobs')\
                    .select('*')\
                    .eq('id', original_job_id)\
                    .eq('user_id', user_id)\
                    .execute()
                
                if not job_result.data or len(job_result.data) == 0:
                    logger.error(f"❌ Analysis Job {original_job_id} nicht gefunden oder gehört nicht User {user_id}")
                    raise HTTPException(status_code=400, detail=f"Analysis Job {original_job_id} nicht gefunden")
                
                target_job = job_result.data[0]
                logger.info(f"✅ Job gefunden: {target_job['id']} - {target_job['url']} - Status: {target_job['status']}")
                    
                # Erstelle upgrade_task für Professional Fix
                try:
                    upgrade_task_data = {
                        'job_id': target_job['id'],
                        'upgrade_type': 'professional_fix',
                        'status': 'requested',
                        'assigned_to': 'webdev',
                        'customer_notified': False,
                        'trigger_source': 'manual',
                        'triggered_by_user_id': user_id,
                        'created_at': datetime.now().isoformat()
                    }
                    
                    # Prüfe ob bereits ein upgrade_task für diesen Job existiert
                    existing_task_result = supabase.client.table('upgrade_tasks')\
                        .select('id')\
                        .eq('job_id', target_job['id'])\
                        .eq('upgrade_type', 'professional_fix')\
                        .execute()
                    
                    if existing_task_result.data and len(existing_task_result.data) > 0:
                        logger.warning(f"⚠️ Upgrade Task für Job {target_job['id']} existiert bereits")
                        task_id = existing_task_result.data[0]['id']
                    else:
                        # Erstelle neuen upgrade_task
                        task_result = supabase.client.table('upgrade_tasks')\
                            .insert(upgrade_task_data)\
                            .execute()
                        
                        if task_result.data and len(task_result.data) > 0:
                            task_id = task_result.data[0]['id']
                            logger.info(f"✅ Upgrade Task {task_id} für Professional Fix erstellt")
                        else:
                            logger.error(f"❌ Fehler beim Erstellen des Upgrade Tasks: {task_result}")
                            raise HTTPException(status_code=500, detail="Upgrade Task konnte nicht erstellt werden")
                    
                    # Optional: Versuche den ursprünglichen Job zu aktualisieren (nicht kritisch)
                    try:
                        # Nur die Session ID speichern, ohne neue Spalten
                        result = supabase.client.table('analysis_jobs').update({
                            'updated_at': datetime.now().isoformat()
                        }).eq('id', target_job['id']).execute()
                        logger.info(f"✅ Analysis Job {target_job['id']} aktualisiert")
                    except Exception as e:
                        logger.info(f"ℹ️ Analysis Job Update übersprungen: {e}")
                    
                    logger.info(f"🎯 Professional Fix Workflow erfolgreich:")
                    logger.info(f"   📋 Task-ID: {task_id}")
                    logger.info(f"   🔗 Job-ID: {target_job['id']}")
                    logger.info(f"   👤 Customer: {user_id}")
                    logger.info(f"   💳 Payment Session: {session.id}")
                    logger.info(f"   🌐 Website: {url}")
                    
                    return {"status": "success", "task_id": task_id, "job_id": target_job['id'], "type": "professional_fix"}
                    
                except Exception as e:
                    logger.error(f"❌ Fehler beim Erstellen des Professional Fix Upgrade Tasks: {str(e)}")
                    raise HTTPException(status_code=500, detail=f"Professional Fix Task konnte nicht erstellt werden: {str(e)}")
                    
            elif plan == 'certificate_only':
                logger.info(f"🏆 ENTERING Certificate workflow für {url} von User {user_id}")
                
                # DEBUG: Zeige alle Metadaten
                logger.info(f"📋 ALLE METADATA: {json.dumps(metadata, indent=2)}")
                
                # Verwende die exakte Job-ID aus den Stripe-Metadaten (beide möglichen Schlüssel prüfen)
                original_job_id = metadata.get('original_job_id') or metadata.get('existing_job_id')
                
                logger.info(f"🔍 Job-ID Suche: original_job_id={metadata.get('original_job_id')}, existing_job_id={metadata.get('existing_job_id')}")
                logger.info(f"🎯 Finale Job-ID: {original_job_id}")
                
                if not original_job_id:
                    logger.error(f"❌ Keine 'original_job_id' oder 'existing_job_id' in Stripe-Metadaten für Certificate gefunden")
                    logger.error(f"❌ Vorhandene Keys in Metadata: {list(metadata.keys())}")
                    raise HTTPException(status_code=400, detail="Job-ID fehlt in Metadaten")
                
                logger.info(f"🔍 Certificate für spezifische Job-ID: {original_job_id}")
                
                # Hole den spezifischen Job über Job-ID
                job_result = supabase.client.table('analysis_jobs')\
                    .select('*')\
                    .eq('id', original_job_id)\
                    .eq('user_id', user_id)\
                    .execute()
                
                if not job_result.data or len(job_result.data) == 0:
                    logger.error(f"❌ Analysis Job {original_job_id} nicht gefunden oder gehört nicht User {user_id}")
                    raise HTTPException(status_code=400, detail=f"Analysis Job {original_job_id} nicht gefunden")
                
                target_job = job_result.data[0]
                logger.info(f"✅ Job gefunden: {target_job['id']} - {target_job['url']} - Status: {target_job['status']}")
                    
                # Erstelle upgrade_task für Certificate
                try:
                    upgrade_task_data = {
                        'job_id': target_job['id'],
                        'upgrade_type': 'certificate',
                        'status': 'requested',
                        'assigned_to': 'certifier',
                        'customer_notified': False,
                        'trigger_source': 'manual',
                        'triggered_by_user_id': user_id,
                        'created_at': datetime.now().isoformat()
                    }
                    
                    # Prüfe ob bereits ein upgrade_task für diesen Job existiert
                    existing_task_result = supabase.client.table('upgrade_tasks')\
                        .select('id')\
                        .eq('job_id', target_job['id'])\
                        .eq('upgrade_type', 'certificate')\
                        .execute()
                    
                    if existing_task_result.data and len(existing_task_result.data) > 0:
                        logger.warning(f"⚠️ Certificate Task für Job {target_job['id']} existiert bereits")
                        task_id = existing_task_result.data[0]['id']
                    else:
                        # Erstelle neuen upgrade_task
                        task_result = supabase.client.table('upgrade_tasks')\
                            .insert(upgrade_task_data)\
                            .execute()
                        
                        if task_result.data and len(task_result.data) > 0:
                            task_id = task_result.data[0]['id']
                            logger.info(f"✅ Upgrade Task {task_id} für Certificate erstellt")
                        else:
                            logger.error(f"❌ Fehler beim Erstellen des Certificate Tasks: {task_result}")
                            raise HTTPException(status_code=500, detail="Certificate Task konnte nicht erstellt werden")
                    
                    # Optional: Versuche den ursprünglichen Job zu aktualisieren (nicht kritisch)
                    try:
                        # Nur die Session ID speichern, ohne neue Spalten
                        result = supabase.client.table('analysis_jobs').update({
                            'updated_at': datetime.now().isoformat()
                        }).eq('id', target_job['id']).execute()
                        logger.info(f"✅ Analysis Job {target_job['id']} aktualisiert")
                    except Exception as e:
                        logger.info(f"ℹ️ Analysis Job Update übersprungen: {e}")
                    
                    logger.info(f"🎯 Certificate Workflow erfolgreich:")
                    logger.info(f"   📋 Task-ID: {task_id}")
                    logger.info(f"   🔗 Job-ID: {target_job['id']}")
                    logger.info(f"   👤 Customer: {user_id}")
                    logger.info(f"   💳 Payment Session: {session.id}")
                    logger.info(f"   🌐 Website: {url}")
                    
                    return {"status": "success", "task_id": task_id, "job_id": target_job['id'], "type": "certificate"}
                    
                except Exception as e:
                    logger.error(f"❌ Fehler beim Erstellen des Certificate Upgrade Tasks: {str(e)}")
                    raise HTTPException(status_code=500, detail=f"Certificate Task konnte nicht erstellt werden: {str(e)}")
                    
            else:
                logger.info(f"📊 Standard Analyse gekauft: Plan {plan} für {url} von User {user_id}")
                
                # Erstelle den AnalysisRequest für den asynchronen Task
                analysis_request = AnalysisRequest(
                    url=url,
                    plan=plan,
                    max_pages=max_pages,
                    user_id=user_id
                )
                
                # Starte die Analyse direkt, genau wie es /analyze-complete-async tun würde
                job_id = supabase.create_analysis_job(
                    url=url, 
                    plan=plan, 
                    user_id=user_id,
                    payment_session_id=session.id, # Speichere die Stripe Session ID
                    selected_upgrades=selected_upgrades # Speichere die ausgewählten Upgrades
                )
                
                # WICHTIG: Initialisiere Job-Status in running_analyses (genau wie in analyze-complete-async)
                running_analyses[job_id] = {
                    "status": "running",
                    "progress": 0,
                    "message": "Analyse via Webhook gestartet...",
                    "started_at": datetime.now().isoformat(),
                    "url": url,
                    "plan": plan,
                    "user_id": user_id,
                    "payment_session_id": session.id
                }
                
                logger.info(f"Analysejob {job_id} via Webhook erstellt. Starte asynchronen Task...")

                asyncio.create_task(run_analysis_async(job_id, analysis_request))
                
                logger.info(f"✅ Analyse für Job {job_id} erfolgreich via Webhook gestartet.")
                return {"status": "success", "job_id": job_id, "type": "analysis"}

        except Exception as e:
            logger.error(f"Fehler bei der Verarbeitung des Webhooks und Start der Analyse: {e}")
            # Einen Fehler an Stripe zurückgeben, damit der Webhook erneut versucht wird
            raise HTTPException(status_code=500, detail=f"Webhook-Verarbeitung fehlgeschlagen: {e}")
    else:
        logger.info(f"⏭️ Überspringe Event Type: {event['type']} (erwarten checkout.session.completed)")
        return {"status": "event received but not processed"}
            
    return {"status": "event received"}

@app.post("/api/count-pages")
async def count_pages_api(request: PageCountRequest):
    """
    API-Endpoint für Frontend Page Counter
    Zählt die Seiten einer Website mit verschiedenen Strategien
    """
    try:
        logger.info(f"Starte Seitenanzahl-Ermittlung für: {request.url}")
        
        # Verwende den WebsiteCrawler für die Seitenanzahl-Ermittlung
        from analyzers.website_crawler import WebsiteCrawler
        crawler = WebsiteCrawler()
        
        # Führe die Seitenanzahl-Ermittlung durch
        result = crawler.count_all_pages(request.url, max_depth=2)
        
        # Formatiere das Ergebnis für das Frontend
        return {
            "success": True,
            "page_count": result.get("total_pages", 25),
            "confidence": result.get("confidence", "medium"),
            "methods_used": result.get("methods_used", ["estimation"]),
            "details": result.get("details", {}),
            "recommendations": result.get("recommendations", []),
            "message": f"Seitenanzahl erfolgreich ermittelt: {result.get('total_pages', 25)} Seiten"
        }
        
    except Exception as e:
        logger.error(f"Fehler bei Seitenanzahl-Ermittlung: {str(e)}")
        # Fallback-Antwort
        return {
            "success": False,
            "page_count": 25,
            "confidence": "low",
            "methods_used": ["fallback"],
            "details": {"error": str(e)},
            "recommendations": ["Manuelle Überprüfung empfohlen"],
            "message": "Fallback-Schätzung verwendet",
            "error": str(e)
        }

if __name__ == "__main__":
    logger.info("Starte Server")
    try:
        uvicorn.run("main:app", host=config.BACKEND_HOST, port=config.BACKEND_PORT, reload=True)
    except Exception as e:
        logger.error(f"Fehler beim Serverstart: {str(e)}")
        sys.exit(1) 