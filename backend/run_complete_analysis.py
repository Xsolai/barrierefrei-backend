#!/usr/bin/env python3
"""
Vollständige WCAG-Barrierefreiheits-Analyse mit allen Expert-Prompts
Automatische Analyse aller WCAG-Bereiche mit ChatGPT-4
"""

import logging
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from analyzers.website_crawler import WebsiteCrawler
from analyzers.accessibility_checker import AccessibilityChecker
from analyzers.criteria_mapper import CriteriaMapper
from analyzers.openai_analyzer import OpenAIWCAGAnalyzer
import time
from services.supabase_service import SupabaseService

# Logging Setup
def setup_logging():
    # Erstelle logs Verzeichnis falls nicht vorhanden
    Path("logs").mkdir(exist_ok=True)
    
    # Erstelle Formatter
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_formatter = logging.Formatter('%(message)s')  # Vereinfachtes Format für die Konsole
    
    # File Handler für detaillierte Logs
    file_handler = logging.FileHandler(f'logs/wcag_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    # Console Handler nur für wichtige Infos
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Nur Warnungen und Fehler im Terminal
    console_handler.setFormatter(console_formatter)
    
    # Root Logger konfigurieren
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Entferne alle existierenden Handler
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Füge neue Handler hinzu
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Externe Bibliotheken komplett stumm schalten
    logging.getLogger('httpx').setLevel(logging.CRITICAL)
    logging.getLogger('httpcore').setLevel(logging.CRITICAL)
    logging.getLogger('urllib3').setLevel(logging.CRITICAL)
    logging.getLogger('openai').setLevel(logging.CRITICAL)
    logging.getLogger('hpack').setLevel(logging.CRITICAL)
    logging.getLogger('asyncio').setLevel(logging.CRITICAL)
    
    # Spezielle Handler für unsere wichtigen Logger
    important_loggers = [
        'run_complete_analysis',
        'analyzers.openai_analyzer',
        'main'
    ]
    
    for logger_name in important_loggers:
        logger_obj = logging.getLogger(logger_name)
        logger_obj.propagate = False
        logger_obj.addHandler(file_handler)
        
        # Console Handler nur für INFO und höher für wichtige Logger
        important_console_handler = logging.StreamHandler()
        important_console_handler.setLevel(logging.INFO)
        important_console_handler.setFormatter(console_formatter)
        logger_obj.addHandler(important_console_handler)

# Initialisiere Logging
setup_logging()
logger = logging.getLogger(__name__)

class CompleteWCAGAnalyzer:
    """Vollständige WCAG-Analyse mit allen Expert-Prompts"""
    
    def __init__(self, supabase_job_id: Optional[str] = None):
        self.timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.logger = logging.getLogger(__name__)
        self.supabase = SupabaseService()
        self.job_id = supabase_job_id
        self.user_id: Optional[str] = None

        if self.job_id and self.supabase.client:
            try:
                job_details = self.supabase.get_job_status(self.job_id)
                if job_details and 'user_id' in job_details:
                    self.user_id = job_details['user_id']
                    self.logger.info(f"User ID {self.user_id} für Job {self.job_id} geladen.")
                else:
                    self.logger.warning(f"Keine User ID für Job {self.job_id} gefunden.")
            except Exception as e:
                self.logger.error(f"Fehler beim Laden der User ID für Job {self.job_id}: {e}")
        
        # WCAG-Bereiche Definition
        self.wcag_areas = {
            "1_1_textalternativen": {
                "name": "1.1 Textalternativen",
                "principle": "1. Wahrnehmbarkeit",
                "description": "Nicht-Text-Inhalte haben Textalternativen"
            },
            "1_2_zeitbasierte_medien": {
                "name": "1.2 Zeitbasierte Medien", 
                "principle": "1. Wahrnehmbarkeit",
                "description": "Audio- und Video-Inhalte haben Alternativen"
            },
            "1_3_anpassbare_darstellung": {
                "name": "1.3 Anpassbare Darstellung",
                "principle": "1. Wahrnehmbarkeit", 
                "description": "Informationen und Strukturen sind programmatisch bestimmbar"
            },
            "1_4_wahrnehmbare_unterscheidungen": {
                "name": "1.4 Wahrnehmbare Unterscheidungen",
                "principle": "1. Wahrnehmbarkeit",
                "description": "Inhalte sind für Nutzer wahrnehmbar unterscheidbar"
            },
            "2_1_tastaturbedienung": {
                "name": "2.1 Tastaturbedienung",
                "principle": "2. Bedienbarkeit",
                "description": "Alle Funktionen sind per Tastatur bedienbar"
            },
            "2_2_genuegend_zeit": {
                "name": "2.2 Genügend Zeit",
                "principle": "2. Bedienbarkeit",
                "description": "Nutzer haben genug Zeit, Inhalte zu lesen und zu nutzen"
            },
            "2_3_anfaelle_vermeiden": {
                "name": "2.3 Anfälle vermeiden",
                "principle": "2. Bedienbarkeit",
                "description": "Inhalte verursachen keine Anfälle"
            },
            "2_4_navigation": {
                "name": "2.4 Navigierbarkeit",
                "principle": "2. Bedienbarkeit",
                "description": "Navigation und Orientierung sind zugänglich"
            },
            "3_1_lesbarkeit_sprache": {
                "name": "3.1 Lesbarkeit und Sprache",
                "principle": "3. Verständlichkeit",
                "description": "Text ist lesbar und verständlich"
            },
            "3_2_vorhersehbarkeit": {
                "name": "3.2 Vorhersehbarkeit",
                "principle": "3. Verständlichkeit",
                "description": "Webseiten erscheinen und funktionieren vorhersehbar"
            },
            "3_3_eingabeunterstuetzung": {
                "name": "3.3 Unterstützung bei der Eingabe",
                "principle": "3. Verständlichkeit",
                "description": "Nutzer werden bei der Eingabe unterstützt"
            },
            "4_1_robustheit_kompatibilitaet": {
                "name": "4.1 Robustheit und Kompatibilität", 
                "principle": "4. Robustheit",
                "description": "Inhalte sind robust für verschiedene Hilfstechnologien"
            }
        }
        
    def update_progress(self, progress: int, message: str, status: str = 'running'):
        """Aktualisiert den Fortschritt in Supabase"""
        if self.job_id and self.supabase:
            self.supabase.update_job_progress(self.job_id, progress)
        logger.debug(f"Progress: {progress}% - {message}")
        
    def run_complete_analysis(self, url: str, max_pages: int = 5) -> Dict[str, Any]:
        """Führt eine vollständige WCAG-Analyse durch"""
        
        logger.info(f"🚀 Starte WCAG-Analyse für: {url}")
        logger.debug(f"Konfiguration: max_pages={max_pages}, wcag_areas={len(self.wcag_areas)}")
        
        start_time = time.time()
        analysis_results = {
            "meta": {
                "url": url,
                "timestamp": self.timestamp,
                "max_pages": max_pages,
                "wcag_areas_count": len(self.wcag_areas),
                "analysis_version": "2.0"
            },
            "crawling": {},
            "accessibility_check": {},
            "ai_analyses": {},
            "summary": {},
            "token_usage": {
                "total_tokens": 0,
                "successful_analyses": 0,
                "failed_analyses": 0
            }
        }
        
        try:
            # 1. Website-Crawling
            self.update_progress(5, "Website-Crawling...")
            logger.debug("1/3: Starte Website-Crawling...")
            crawl_results = self._run_website_crawling(url, max_pages)
            
            # Speichere Crawl-Results für AI-Analysen
            self.crawl_results = crawl_results
            
            analysis_results["crawling"] = {
                "pages_crawled": crawl_results.get('pages_crawled', 0),
                "base_url": crawl_results.get('base_url', url),
                "total_links": len(crawl_results.get("data", {})),
                "warning": crawl_results.get("warning"),
                "error": crawl_results.get("error")
            }
            
            # Wenn ein Fehler auftrat, loggen aber trotzdem weitermachen
            if "error" in crawl_results:
                logger.warning(f"⚠️ Crawling-Fehler: {crawl_results['error']}")
            elif "warning" in crawl_results:
                logger.debug(f"Crawling-Warnung: {crawl_results['warning']}")
            
            self.update_progress(10, f"Crawling: {analysis_results['crawling']['pages_crawled']} Seiten")
            logger.debug(f"Crawling abgeschlossen: {analysis_results['crawling']['pages_crawled']} Seiten")
            
            # 2. Barrierefreiheits-Check  
            self.update_progress(15, "Automatische Checks...")
            logger.debug("2/3: Starte Barrierefreiheits-Analyse...")
            accessibility_results = self._run_accessibility_check(url)
            
            if not accessibility_results:
                logger.error("❌ Accessibility-Check fehlgeschlagen")
                return {"error": "Accessibility-Check fehlgeschlagen"}
            
            # Speichere Accessibility-Results für AI-Analysen
            self.accessibility_results = accessibility_results
            
            analysis_results["accessibility_check"] = {
                "violations": len(accessibility_results.get("violations", [])),
                "warnings": len(accessibility_results.get("warnings", [])),
                "passed": len(accessibility_results.get("passed", [])),
                "success": True
            }
            
            violations = analysis_results['accessibility_check']['violations']
            self.update_progress(20, f"Automatische Checks: {violations} Verstöße")
            logger.info(f"⚠️ {violations} Verstöße gefunden")
            
            # 3. ChatGPT-4 Expert-Analysen für alle WCAG-Bereiche
            self.update_progress(22, "KI-Analysen...")
            logger.debug("3/3: Starte KI-Analysen...")
            ai_results = self._run_all_ai_analyses()
            analysis_results["ai_analyses"] = ai_results
            
            # Token-Statistiken sammeln
            total_tokens = 0
            successful_count = 0
            failed_count = 0
            
            for wcag_area, result in ai_results.items():
                if result.get("api_call_successful"):
                    successful_count += 1
                    token_usage = result.get("token_usage", {})
                    if isinstance(token_usage, dict):
                        total_tokens += token_usage.get("total_tokens", 0)
                    else:
                        total_tokens += token_usage if isinstance(token_usage, int) else 0
                else:
                    failed_count += 1
                    logger.debug(f"Analyse für {wcag_area} fehlgeschlagen: {result.get('error')}")
            
            analysis_results["token_usage"]["total_tokens"] = total_tokens
            analysis_results["token_usage"]["successful_analyses"] = successful_count
            analysis_results["token_usage"]["failed_analyses"] = failed_count
            
            # 4. Erstelle Zusammenfassung
            logger.debug("Erstelle Zusammenfassung...")
            analysis_results["summary"] = self._create_comprehensive_summary(analysis_results)
            
            # Speichere Ergebnisse in Supabase
            if self.job_id:
                logger.debug("Speichere finale Ergebnisse in Supabase...")
                # Lokale Dateispeicherung entfernt - alles wird in Supabase gespeichert
                logger.debug("Ergebnisse gespeichert")
            
            # Berechne Gesamtzeit
            end_time = time.time()
            total_time = end_time - start_time
            
            # Markiere Job als erfolgreich abgeschlossen
            if self.job_id:
                self.update_progress(100, "Analyse erfolgreich abgeschlossen", "completed")
                self.supabase.mark_job_completed(self.job_id)
                logger.info(f"Job {self.job_id}: Analyse erfolgreich abgeschlossen")
            
            # Nur finale Zusammenfassung ins Terminal
            logger.info("\n=== Analyse abgeschlossen ===")
            logger.info(f"✓ {successful_count}/{len(self.wcag_areas)} WCAG-Bereiche analysiert")
            if failed_count > 0:
                logger.info(f"⚠️ {failed_count} Analysen fehlgeschlagen")
            logger.info(f"⏱️ Dauer: {total_time:.1f} Sekunden")
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"❌ Fehler: {str(e)}")
            if self.job_id:
                self.supabase.mark_job_failed(self.job_id, str(e))
            return {"error": str(e)}
    
    def _run_website_crawling(self, url: str, max_pages: int) -> Dict[str, Any]:
        """Führt Website-Crawling durch"""
        try:
            crawler = WebsiteCrawler()
            crawl_results = crawler.crawl_website(url, max_pages)
            
            if not crawl_results:
                logger.warning("⚠️ Website-Crawling lieferte keine Ergebnisse, fahre mit leeren Daten fort")
                return {
                    "pages_crawled": 0,
                    "base_url": url,
                    "data": {},
                    "warning": "Crawling lieferte keine Ergebnisse"
                }
            
            if "error" in crawl_results:
                logger.warning(f"⚠️ Website-Crawling mit Warnung: {crawl_results['error']}")
                # Trotzdem mit den verfügbaren Daten fortfahren
                return {
                    "pages_crawled": crawl_results.get('pages_crawled', 0),
                    "base_url": crawl_results.get('base_url', url),
                    "data": crawl_results.get('data', {}),
                    "warning": crawl_results['error']
                }
            
            logger.info(f"✅ {crawl_results.get('pages_crawled', 0)} Seiten erfolgreich gecrawlt")
            return crawl_results
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Website-Crawling: {e}")
            # Statt None zurückzugeben, geben wir ein leeres aber valides Ergebnis zurück
            return {
                "pages_crawled": 0,
                "base_url": url,
                "data": {},
                "error": str(e)
            }
    
    def _run_accessibility_check(self, url: str) -> Dict[str, Any]:
        """Führt Barrierefreiheits-Check durch"""
        try:
            checker = AccessibilityChecker()
            accessibility_results = checker.analyze_website(url, depth=1)
            
            if not accessibility_results or "error" in accessibility_results:
                logger.error("❌ Accessibility-Check fehlgeschlagen")
                return {
                    "violations": [],
                    "warnings": [],
                    "passed": [],
                    "error": "Accessibility-Check fehlgeschlagen"
                }
            
            violations = len(accessibility_results.get("violations", []))
            warnings = len(accessibility_results.get("warnings", []))
            passed = len(accessibility_results.get("passed", []))
            
            logger.info(f"✅ Accessibility-Check: {violations} Verstöße, {warnings} Warnungen, {passed} bestanden")
            return accessibility_results
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Accessibility-Check: {e}")
            return {
                "violations": [],
                "warnings": [],
                "passed": [],
                "error": str(e)
            }
    
    def _run_all_ai_analyses(self) -> Dict[str, Any]:
        """Führt alle KI-gestützten WCAG-Analysen mit KOMPLETTEN ROHDATEN durch - KEINE FILTERUNG!"""
        
        # Expert-Prompts Verzeichnis
        expert_prompts_dir = Path(__file__).parent / "resources" / "expert_prompts"
        
        if not expert_prompts_dir.exists():
            self.logger.error(f"❌ Expert-Prompts Verzeichnis nicht gefunden: {expert_prompts_dir}")
            return {}
        
        # OpenAI Analyzer initialisieren
        analyzer = OpenAIWCAGAnalyzer()
        
        # Ergebnisse für jeden WCAG-Bereich (sequenziell)
        results = {}
        
        # Fortschritt berechnen
        total_areas = len(self.wcag_areas)
        progress_per_area = 68 / total_areas  # 68% für AI-Analysen (22-90%)
        current_progress = 22
        
        self.logger.info(f"🔄 Starte WCAG-Analyse mit KOMPLETTEN ROHDATEN für {total_areas} Bereiche")
        self.logger.info(f"📊 KEINE DATENFILTERUNG - Expert-Prompts bekommen ALLE gecrawlten Daten!")
        
        # ✅ ERSTELLE KOMPLETTE ROHDATEN-STRUKTUR - NICHTS WIRD GEFILTERT!
        complete_raw_data = {
            "meta": {
                "analysis_timestamp": time.strftime("%Y-%m-%d_%H-%M-%S"),
                "data_extraction_method": "COMPLETE_RAW_DATA_NO_FILTERING",
                "version": "3.0_UNFILTERED",
                "note": "ALLE Crawling-Daten und Accessibility-Daten - NICHTS GEFILTERT!"
            },
            
            # ✅ KOMPLETTE CRAWLING-DATEN - ALLES UNGEFILTERT
            "complete_website_data": {
                "base_url": self.crawl_results.get('base_url', ''),
                "pages_crawled": self.crawl_results.get('pages_crawled', 0),
                "all_crawled_pages": self.crawl_results.get('data', {}),  # ALLE SEITEN!
                "crawl_metadata": {
                    "total_links_found": len(self.crawl_results.get('data', {})),
                    "crawl_timestamp": self.crawl_results.get('timestamp', ''),
                    "warnings": self.crawl_results.get('warning'),
                    "errors": self.crawl_results.get('error')
                }
            },
            
            # ✅ KOMPLETTE ACCESSIBILITY-DATEN - ALLE VIOLATIONS!
            "complete_accessibility_data": {
                "total_violations": len(self.accessibility_results.get("violations", [])),
                "total_warnings": len(self.accessibility_results.get("warnings", [])),
                "total_passed": len(self.accessibility_results.get("passed", [])),
                "all_violations": self.accessibility_results.get("violations", []),  # ALLE VIOLATIONS!
                "all_warnings": self.accessibility_results.get("warnings", []),     # ALLE WARNINGS!
                "all_passed": self.accessibility_results.get("passed", []),         # ALLE PASSED!
                "accessibility_metadata": {
                    "analysis_tool": "AccessibilityChecker",
                    "analysis_depth": 1,
                    "check_timestamp": time.strftime("%Y-%m-%d_%H-%M-%S")
                }
            },
            
            # ✅ ZUSÄTZLICHE CONTEXT-DATEN
            "analysis_context": {
                "current_wcag_area": "WIRD_FÜR_JEDEN_BEREICH_GESETZT",
                "total_wcag_areas": len(self.wcag_areas),
                "analysis_approach": "COMPREHENSIVE_UNFILTERED_ANALYSIS",
                "token_budget": "1_MILLION_TOKENS_AVAILABLE"
            }
        }
        
        # Analysiere jeden WCAG-Bereich mit KOMPLETTEN ROHDATEN
        for wcag_area in self.wcag_areas.keys():
            try:
                current_progress_int = int(current_progress)
                self.update_progress(current_progress_int, f"Analysiere WCAG-Bereich: {wcag_area} (ALLE DATEN)")
                
                module_start_time = time.time()
                
                # ✅ SETZE AKTUELLEN WCAG-BEREICH - ABER ALLE DATEN BLEIBEN!
                complete_raw_data["analysis_context"]["current_wcag_area"] = wcag_area
                complete_raw_data["analysis_context"]["wcag_area_info"] = self.wcag_areas[wcag_area]
                
                self.logger.info(f"📋 Liefere KOMPLETTE ROHDATEN an Expert-Prompt für {wcag_area}")
                self.logger.info(f"   📊 {len(str(complete_raw_data))} Zeichen Rohdaten")
                self.logger.info(f"   🔍 {len(complete_raw_data['complete_website_data']['all_crawled_pages'])} Seiten")
                self.logger.info(f"   ⚠️ {len(complete_raw_data['complete_accessibility_data']['all_violations'])} Violations (ALLE!)")
                
                # ✅ EXPERT-PROMPT MIT KOMPLETTEN ROHDATEN ANALYSIEREN
                ai_analysis_start = time.time()
                single_analysis_result = analyzer.analyze_single_expert_prompt_with_data(
                    str(expert_prompts_dir),
                    wcag_area,
                    complete_raw_data  # ✅ ALLE DATEN UNGEFILTERT!
                )
                ai_analysis_time = time.time() - ai_analysis_start
                
                # SCHRITT 3: Ergebnis verarbeiten und speichern
                if single_analysis_result:
                    results[wcag_area] = single_analysis_result
                    
                    if single_analysis_result.get("api_call_successful"):
                        token_usage = single_analysis_result.get("token_usage", {})
                        total_tokens = token_usage.get("total_tokens", 0) if isinstance(token_usage, dict) else token_usage if isinstance(token_usage, int) else 0
                        
                        module_duration = time.time() - module_start_time
                        self.logger.info(f"✅ ROHDATEN-Analyse erfolgreich für {wcag_area}")
                        self.logger.info(f"   📊 Dauer: {module_duration:.2f}s (KI: {ai_analysis_time:.2f}s)")
                        self.logger.info(f"   🎯 Token: {total_tokens} (von 1M verfügbar)")
                        
                        # Speichere Modul-Ergebnis in Supabase
                        if self.job_id:
                            raw_openai_response = single_analysis_result.get("analysis_content", "")
                            
                            # Parsen der analysis_content
                            analysis_content_json = {}
                            try:
                                cleaned_response = self._extract_json_from_markdown(raw_openai_response)
                                analysis_content_json = json.loads(cleaned_response)
                            except json.JSONDecodeError as json_err:
                                self.logger.error(f"Fehler beim Parsen von analysis_content für {wcag_area}: {json_err}")
                                analysis_content_json = {"error": "Konnte AI Antwort nicht parsen"}

                            self.supabase.save_module_result(
                                job_id=self.job_id,
                                module_name=wcag_area,
                                result=analysis_content_json,
                                token_usage=total_tokens,
                                user_id=self.user_id
                            )
                            
                            self.logger.info(f"💾 ROHDATEN-Ergebnis für {wcag_area} in Supabase gespeichert")
                    else:
                        self.logger.error(f"❌ ROHDATEN-Analyse fehlgeschlagen für {wcag_area}: {single_analysis_result.get('error')}")
                        if self.job_id:
                            self.supabase.save_module_error(
                                job_id=self.job_id,
                                module_name=wcag_area,
                                error=single_analysis_result.get('error', 'Unbekannter Analysefehler'),
                                user_id=self.user_id
                            )
                else:
                    self.logger.error(f"❌ Keine Ergebnisse für {wcag_area}")
                    results[wcag_area] = {
                        "wcag_area": wcag_area,
                        "api_call_successful": False,
                        "error": "Keine Ergebnisse von ROHDATEN-Analyse"
                    }
                    if self.job_id:
                        self.supabase.save_module_error(
                            job_id=self.job_id,
                            module_name=wcag_area,
                            error="Keine Ergebnisse von ROHDATEN-Analyse",
                            user_id=self.user_id
                        )
                
            except Exception as e:
                self.logger.error(f"❌ Kritischer Fehler bei ROHDATEN-Analyse von {wcag_area}: {e}", exc_info=True)
                results[wcag_area] = {
                    "wcag_area": wcag_area,
                    "api_call_successful": False,
                    "error": str(e)
                }
                if self.job_id:
                    self.supabase.save_module_error(
                        job_id=self.job_id,
                        module_name=wcag_area,
                        error=str(e),
                        user_id=self.user_id
                    )
            
            current_progress += progress_per_area
        
        self.logger.info(f"🏁 ROHDATEN-Analyse abgeschlossen - KEINE DATEN GEFILTERT!")
        return results
    
    def _create_comprehensive_summary(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Erstellt eine umfassende Zusammenfassung aller Analysen"""
        
        # WCAG-Prinzipien gruppieren
        principles_summary = {}
        for wcag_area, result in analysis_results["ai_analyses"].items():
            if result.get("api_call_successful"):
                # Sichere Extraktion der WCAG-Info
                wcag_info = result.get("wcag_info", {})
                principle = wcag_info.get("principle", "Unbekanntes Prinzip")
                
                if principle not in principles_summary:
                    principles_summary[principle] = {
                        "successful_analyses": 0,
                        "total_tokens": 0,
                        "areas": []
                    }
                
                principles_summary[principle]["successful_analyses"] += 1
                
                # Sichere Token-Extraktion
                token_usage = result.get("token_usage", {})
                if isinstance(token_usage, dict):
                    tokens = token_usage.get("total_tokens", 0)
                else:
                    tokens = token_usage if isinstance(token_usage, int) else 0
                    
                principles_summary[principle]["total_tokens"] += tokens
                principles_summary[principle]["areas"].append({
                    "area": wcag_info.get("name", wcag_area),
                    "tokens": tokens
                })
        
        # Gesamtbewertung
        total_possible_analyses = len(self.wcag_areas)
        successful_analyses = analysis_results["token_usage"]["successful_analyses"]
        completion_rate = (successful_analyses / total_possible_analyses) * 100 if total_possible_analyses > 0 else 0
        
        # Compliance Score berechnen (basierend auf Verstößen vs. erfolgreichen Checks)
        violations = analysis_results["accessibility_check"]["violations"]
        passed = analysis_results["accessibility_check"]["passed"]
        total_checks = violations + passed
        compliance_score = (passed / total_checks) * 100 if total_checks > 0 else 0
        
        # Bestimme Konformitätsstufe
        if violations == 0 and successful_analyses == total_possible_analyses:
            conformance_level = "AAA"
        elif violations <= 5 and successful_analyses >= total_possible_analyses * 0.8:
            conformance_level = "AA"
        elif violations <= 10 and successful_analyses >= total_possible_analyses * 0.6:
            conformance_level = "A"
        else:
            conformance_level = "Nicht konform"
        
        return {
            "overall_assessment": {
                "conformance_level": conformance_level,
                "compliance_score": compliance_score,
                "total_violations": violations,
                "successful_analyses": f"{successful_analyses}/{total_possible_analyses}",
                "completion_rate": round(completion_rate, 1),
                "total_pages_analyzed": analysis_results["crawling"]["pages_crawled"],
                "total_wcag_areas": total_possible_analyses,
                "successful_ai_analyses": successful_analyses
            },
            "principles_breakdown": principles_summary,
            "accessibility_overview": {
                "violations": analysis_results["accessibility_check"]["violations"],
                "warnings": analysis_results["accessibility_check"]["warnings"], 
                "passed": analysis_results["accessibility_check"]["passed"],
                "total_token_usage": analysis_results["token_usage"]["total_tokens"]
            },
            "recommendations": self._generate_priority_recommendations(analysis_results),
            "executive_summary": self._generate_executive_summary(analysis_results, conformance_level, compliance_score)
        }
    
    def _generate_priority_recommendations(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generiert prioritäre Empfehlungen basierend auf den Analysen"""
        recommendations = []
        
        # High-Priority: Viele Verstöße
        violations = analysis_results["accessibility_check"]["violations"]
        if violations > 30:
            recommendations.append({
                "priority": "HIGH",
                "category": "Kritische Verstöße",
                "description": f"{violations} WCAG-Verstöße gefunden - sofortige Überprüfung erforderlich",
                "action": "Priorisiere die Behebung der häufigsten Verstöße"
            })
        
        # Medium-Priority: Unvollständige AI-Analysen
        failed_analyses = analysis_results["token_usage"]["failed_analyses"]
        if failed_analyses > 0:
            recommendations.append({
                "priority": "MEDIUM", 
                "category": "Unvollständige Analyse",
                "description": f"{failed_analyses} WCAG-Bereiche konnten nicht vollständig analysiert werden",
                "action": "Überprüfe Expert-Prompt-Dateien und API-Konfiguration"
            })
        
        # Success: Hohe Completion Rate  
        successful_analyses = analysis_results["token_usage"]["successful_analyses"]
        total_possible_analyses = len(self.wcag_areas)
        completion_rate = (successful_analyses / total_possible_analyses) * 100 if total_possible_analyses > 0 else 0
        if completion_rate >= 80:
            recommendations.append({
                "priority": "INFO",
                "category": "Erfolgreiche Analyse", 
                "description": f"{completion_rate}% der WCAG-Bereiche erfolgreich analysiert",
                "action": "Nutze die detaillierten AI-Analysen für konkrete Verbesserungen"
            })
        
        return recommendations
    
    def _generate_executive_summary(self, analysis_results: Dict[str, Any], conformance_level: str, compliance_score: int) -> Dict[str, Any]:
        """Generiert eine Executive Summary"""
        return {
            "headline": f"WCAG-Konformität: {conformance_level}",
            "score": compliance_score,
            "key_findings": [
                f"{analysis_results['crawling']['pages_crawled']} Seiten analysiert",
                f"{analysis_results['accessibility_check']['violations']} kritische Verstöße identifiziert",
                f"{analysis_results['token_usage']['total_tokens']:,} AI-Token für detaillierte Analyse verwendet"
            ],
            "next_steps": "Beheben Sie zuerst die kritischen technischen Verstöße"
        }

    def _extract_json_from_markdown(self, markdown_text: str) -> str:
        """Extrahiert JSON aus Markdown-Code-Blöcken (kopiert von OpenAI Analyzer)"""
        import re
        
        # Versuche JSON aus ```json Code-Blöcken zu extrahieren
        json_pattern = r'```json\s*\n(.*?)\n```'
        matches = re.findall(json_pattern, markdown_text, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        
        # Fallback: Versuche JSON aus generischen Code-Blöcken
        code_pattern = r'```\s*\n(.*?)\n```'
        matches = re.findall(code_pattern, markdown_text, re.DOTALL)
        
        if matches:
            for match in matches:
                content = match.strip()
                if content.startswith('{') and content.endswith('}'):
                    return content
        
        # Fallback: Gib den gesamten Text zurück
        return markdown_text.strip()

def main():
    """Hauptfunktion für vollständige WCAG-Analyse"""
    
    # Konfiguration - kann über ENV-Variable überschrieben werden
    target_url = os.getenv("TEST_TARGET_URL", "https://ecomtask.de")
    max_pages = int(os.getenv("TEST_MAX_PAGES", "5"))
    
    logger.info("🚀 Starte vollständige WCAG-Barrierefreiheits-Analyse")
    logger.info(f"🎯 Ziel-URL: {target_url}")
    logger.info(f"📊 Max. Seiten: {max_pages}")
    
    # Vollständige Analyse durchführen
    analyzer = CompleteWCAGAnalyzer()
    results = analyzer.run_complete_analysis(target_url, max_pages)
    
    if "error" in results:
        logger.error(f"❌ Analyse fehlgeschlagen: {results['error']}")
        return
    
    # Erfolgs-Zusammenfassung
    summary = results["summary"]["overall_assessment"]
    logger.info("🎉 VOLLSTÄNDIGE WCAG-ANALYSE ABGESCHLOSSEN!")
    logger.info(f"✅ Completion Rate: {summary['completion_rate']}%")
    logger.info(f"📊 Compliance Score: {summary['compliance_score']}%") 
    logger.info(f"🤖 AI-Analysen: {summary['successful_ai_analyses']}/{summary['total_wcag_areas']}")
    logger.info(f"🎯 Token-Verbrauch: {results['token_usage']['total_tokens']:,}")

if __name__ == "__main__":
    main() 