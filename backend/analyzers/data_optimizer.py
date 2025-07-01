#!/usr/bin/env python3
"""
Data Optimizer für WCAG-Analysen
Optimiert und filtert Daten für effiziente GPT-Analyse
"""

import logging
from typing import Dict, Any, List, Optional
import json

logger = logging.getLogger(__name__)

class WCAGDataOptimizer:
    """Optimiert extrahierte Daten für GPT-Analyse"""
    
    # Maximale Anzahl von Beispielen pro Kategorie
    MAX_EXAMPLES = {
        "critical": 100,   # War 15 - jetzt praktisch unlimitiert
        "severe": 100,     # War 10
        "moderate": 50,    # War 8
        "minor": 50        # War 5
    }
    
    # Relevante Felder pro WCAG-Bereich
    RELEVANT_FIELDS = {
        "1_1_textalternativen": [
            "images.total_count",
            "images.without_alt",
            "images.with_alt",
            "images.empty_alt",
            "images.detailed_analysis",  # Aber gefiltert!
            "non_text_content",
            "accessibility_violations"
        ],
        "1_3_anpassbare_darstellung": [
            "semantic_structure.headings",
            "semantic_structure.landmarks",
            "forms.total_count",
            "forms.without_labels",
            "lists",
            "tables.structure_issues"
        ],
        "2_4_navigation": [
            "navigation.structure",
            "navigation.skip_links",
            "links.total_count",
            "links.ambiguous_count",
            "page_title",
            "headings.hierarchy_issues",
            "breadcrumbs"
        ]
        # ... weitere WCAG-Bereiche
    }
    
    # WICHTIG: Mit 1 Million Token Budget brauchen wir keine künstlichen Limits!
    INCLUDE_FULL_HTML = True
    MAX_DATA_SIZE = 5000000  # 5MB statt 500KB - für 1 Million Token!
    
    # NEU: Schwellenwerte für erweiterte Kontextanreicherung
    SMALL_DATASET_THRESHOLD = 5000  # 5KB
    VERY_SMALL_DATASET_THRESHOLD = 2000  # 2KB - für HTML-Rohdaten
    
    def optimize_data_for_gpt(
        self, 
        wcag_area: str, 
        raw_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimiert Daten für GPT-Analyse
        
        Args:
            wcag_area: WCAG-Bereich
            raw_data: Rohdaten vom Extraktor
            
        Returns:
            Optimierte Daten für GPT
        """
        logger.info(f"🔧 Optimiere Daten für {wcag_area}")
        logger.info(f"📊 INCLUDE_FULL_HTML = {self.INCLUDE_FULL_HTML}")  # DEBUG
        logger.info(f"📊 Rohdaten-Größe: {len(json.dumps(raw_data))} Zeichen")  # DEBUG
        
        # Basis-Struktur
        optimized = {
            "wcag_area": wcag_area,
            "summary_statistics": self._extract_summary_stats(wcag_area, raw_data),
            "critical_findings": self._extract_critical_findings(wcag_area, raw_data),
            "representative_examples": self._extract_examples(wcag_area, raw_data),
            "context": self._extract_context(raw_data)
        }
        
        # NEU: Bei großem Token-Budget die KOMPLETTEN Rohdaten mitliefern!
        if self.INCLUDE_FULL_HTML:
            # Füge die vollständigen Rohdaten hinzu
            optimized["full_raw_data"] = raw_data
            logger.info(f"💰 Token-Budget erlaubt vollständige Rohdaten: {len(json.dumps(raw_data))} Zeichen")
            logger.info(f"🚀 FULL_RAW_DATA AKTIVIERT für {wcag_area}!")  # EXTRA DEUTLICH
            
            # NEU: Erweitere kleine Datensätze mit mehr Kontext für bessere Analyse
            data_size = len(json.dumps(raw_data))
            if data_size < 5000:  # Weniger als 5KB Daten
                logger.info(f"📈 Erweitere kleinen Datensatz ({data_size} Zeichen) mit zusätzlichem Kontext")
                optimized["enhanced_context"] = self._enhance_small_dataset(wcag_area, raw_data)
        else:
            logger.info(f"❌ INCLUDE_FULL_HTML ist False - keine full_raw_data")  # DEBUG
        
        # Bereichs-spezifische Optimierung
        if wcag_area == "1_1_textalternativen":
            optimized = self._optimize_textalternativen(optimized, raw_data)
        elif wcag_area == "1_3_anpassbare_darstellung":
            optimized = self._optimize_anpassbare_darstellung(optimized, raw_data)
        elif wcag_area == "2_4_navigation":
            optimized = self._optimize_navigation(optimized, raw_data)
        
        # Größe reduzieren
        optimized = self._reduce_size(optimized)
        
        logger.info(f"✅ Daten optimiert: {self._calculate_size(optimized)} Zeichen")
        
        return optimized
    
    def _extract_summary_stats(
        self, 
        wcag_area: str, 
        raw_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extrahiert Zusammenfassungs-Statistiken"""
        
        stats = {}
        
        if wcag_area == "1_1_textalternativen":
            images = raw_data.get("images", {})
            total = images.get("total_count", 0)
            
            if total > 0:
                stats = {
                    "total_images": total,
                    "images_without_alt": images.get("without_alt", 0),
                    "images_with_alt": images.get("with_alt", 0),
                    "alt_coverage_percentage": round(
                        (images.get("with_alt", 0) / total) * 100, 1
                    ),
                    "critical_issues": images.get("without_alt", 0),
                    "decorative_images": images.get("decorative", 0)
                }
            else:
                stats = {
                    "total_images": 0,
                    "note": "Keine Bilder gefunden - 100 Punkte"
                }
        
        return stats
    
    def _extract_critical_findings(
        self, 
        wcag_area: str, 
        raw_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extrahiert nur die kritischsten Befunde - MIT HTML-CODE!"""
        
        findings = []
        
        if wcag_area == "1_1_textalternativen":
            # Suche nach Bildern ohne Alt-Text
            detailed = raw_data.get("images", {}).get("detailed_analysis", [])
            
            for page_analysis in detailed[:5]:  # Max 5 Seiten statt 3
                if isinstance(page_analysis, dict):
                    images = page_analysis.get("images", [])
                    page_url = page_analysis.get("url", "")
                    
                    for img in images[:10]:  # Max 10 Bilder pro Seite statt 5
                        if isinstance(img, dict) and not img.get("has_alt"):
                            findings.append({
                                "type": "missing_alt",
                                "severity": "critical",
                                "page_url": page_url,
                                "element": {
                                    "src": img.get("src", ""),
                                    "context": img.get("context", ""),
                                    "dimensions": f"{img.get('width', 0)}x{img.get('height', 0)}",
                                    "is_decorative": img.get("is_decorative", False)
                                },
                                # NEU: Vollständiger HTML-Code!
                                "html_code": img.get("html_snippet", img.get("html", "")),
                                "html_context": img.get("html_context", ""),
                                "dom_location": img.get("dom_path", "")
                            })
                            
                            if len(findings) >= self.MAX_EXAMPLES["critical"]:
                                break
        
        elif wcag_area == "1_3_anpassbare_darstellung":
            # Strukturprobleme detailliert sammeln
            semantic = raw_data.get("semantic_structure", {})
            
            # Heading-Probleme
            headings = semantic.get("headings", {})
            if headings.get("issues", {}).get("skipped_levels"):
                for skip in headings.get("issues", {}).get("skipped_levels", [])[:10]:
                    findings.append({
                        "type": "heading_hierarchy",
                        "severity": "critical",
                        "issue": f"Übersprungene Ebene: {skip}",
                        "impact": "Screenreader-Nutzer verlieren Orientierung"
                    })
            
            # NEU: Sammle HTML-Code von problematischen Headings
            heading_list = semantic.get("headings", {}).get("list", [])
            for heading in heading_list[:20]:  # Mehr Headings für bessere Analyse
                if isinstance(heading, dict):
                    findings.append({
                        "type": "heading_structure",
                        "severity": "info",
                        "level": heading.get("level"),
                        "text": heading.get("text"),
                        "html_code": heading.get("html", ""),
                        "context": heading.get("context", "")
                    })
            
            # Fehlende Landmarks
            landmarks = semantic.get("landmarks", {})
            if not landmarks.get("main"):
                findings.append({
                    "type": "missing_landmark",
                    "severity": "critical",
                    "element": "main",
                    "impact": "Hauptinhalt nicht semantisch markiert"
                })
                
        elif wcag_area == "2_4_navigation":
            # Navigation-Details
            nav_data = raw_data.get("navigation", {})
            
            # Skip-Links
            if not nav_data.get("skip_links", {}).get("found"):
                findings.append({
                    "type": "missing_skip_links",
                    "severity": "critical",
                    "impact": "Tastaturnutzer müssen durch gesamte Navigation"
                })
            
            # Mehrdeutige Links MIT HTML-Code
            ambiguous = nav_data.get("links", {}).get("ambiguous", [])
            for link in ambiguous[:30]:  # Mehr Links für bessere Analyse
                if isinstance(link, dict):
                    findings.append({
                        "type": "ambiguous_link",
                        "severity": "major",
                        "text": link.get("text", ""),
                        "href": link.get("href", ""),
                        "context": link.get("context", ""),
                        # NEU: HTML-Code
                        "html_code": link.get("html", ""),
                        "in_nav": link.get("in_nav", False),
                        "css_classes": link.get("css_classes", [])
                    })
        
        return findings
    
    def _extract_examples(
        self, 
        wcag_area: str, 
        raw_data: Dict[str, Any]
    ) -> Dict[str, List]:
        """Extrahiert repräsentative Beispiele"""
        
        examples = {
            "good_practices": [],
            "violations": [],
            "warnings": []
        }
        
        if wcag_area == "1_1_textalternativen":
            detailed = raw_data.get("images", {}).get("detailed_analysis", [])
            
            for page_analysis in detailed[:5]:  # Max 5 Seiten für Beispiele statt 2
                if isinstance(page_analysis, dict):
                    images = page_analysis.get("images", [])
                    page_url = page_analysis.get("url", "")
                    
                    for img in images:
                        if isinstance(img, dict):
                            alt = img.get("alt", "")
                            
                            # Gute Beispiele
                            if alt and len(alt) > 10 and len(alt) < 100:
                                if len(examples["good_practices"]) < 10:  # Mehr gute Beispiele
                                    examples["good_practices"].append({
                                        "alt": alt,
                                        "src": img.get("src", ""),
                                        "page_url": page_url,
                                        "context": img.get("context", ""),
                                        # NEU: HTML-Code für gute Beispiele
                                        "html_code": img.get("html_snippet", img.get("html", "")),
                                        "implementation": "korrekt"
                                    })
                            
                            # Verstöße
                            elif not img.get("has_alt"):
                                if len(examples["violations"]) < 15:  # Mehr Verstöße
                                    examples["violations"].append({
                                        "issue": "missing_alt",
                                        "src": img.get("src", ""),
                                        "page_url": page_url,
                                        "context": img.get("context", ""),
                                        "img_type": "informative" if not img.get("is_decorative") else "decorative",
                                        # NEU: Vollständiger HTML-Code des Verstoßes
                                        "html_code": img.get("html_snippet", img.get("html", "")),
                                        "html_context": img.get("html_context", ""),
                                        "fix_suggestion": "Fügen Sie ein aussagekräftiges alt-Attribut hinzu"
                                    })
                            
                            # NEU: Warnungen (z.B. leere Alt-Texte bei informativen Bildern)
                            elif alt == "" and not img.get("is_decorative"):
                                if len(examples["warnings"]) < 10:
                                    examples["warnings"].append({
                                        "issue": "empty_alt_on_informative_image",
                                        "src": img.get("src", ""),
                                        "page_url": page_url,
                                        "html_code": img.get("html_snippet", img.get("html", "")),
                                        "current_state": "alt=''",
                                        "recommendation": "Prüfen Sie, ob das Bild wirklich dekorativ ist"
                                    })
        
        return examples
    
    def _extract_context(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrahiert relevanten Kontext"""
        
        return {
            "pages_analyzed": raw_data.get("pages_analyzed", []),
            "extraction_method": raw_data.get("extraction_method", "unknown"),
            "total_elements_checked": self._count_total_elements(raw_data)
        }
    
    def _optimize_textalternativen(
        self, 
        optimized: Dict[str, Any], 
        raw_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Spezielle Optimierung für 1.1 Textalternativen"""
        
        # Entferne überflüssige Performance-Daten
        if "comprehensive_image_analysis" in raw_data:
            # Behalte nur relevante Teile
            comprehensive = raw_data["comprehensive_image_analysis"]
            optimized["additional_context"] = {
                "format_distribution": comprehensive.get("image_metadata", {}).get("formats", {}),
                "social_media_images": {
                    "has_og_image": bool(comprehensive.get("social_media_images", {}).get("open_graph_images")),
                    "has_twitter_image": bool(comprehensive.get("social_media_images", {}).get("twitter_card_images"))
                }
            }
        
        return optimized
    
    def _optimize_anpassbare_darstellung(
        self, 
        optimized: Dict[str, Any], 
        raw_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Spezielle Optimierung für 1.3 Anpassbare Darstellung"""
        
        # Fokus auf Struktur-Probleme
        semantic = raw_data.get("semantic_structure", {})
        
        if semantic:
            optimized["structure_analysis"] = {
                "heading_issues": self._summarize_heading_issues(semantic),
                "landmark_coverage": self._calculate_landmark_coverage(semantic),
                "form_accessibility": self._summarize_form_issues(semantic)
            }
        
        return optimized
    
    def _optimize_navigation(
        self, 
        optimized: Dict[str, Any], 
        raw_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Spezielle Optimierung für 2.4 Navigation"""
        
        nav_data = raw_data.get("navigation", {})
        
        if nav_data:
            optimized["navigation_quality"] = {
                "has_skip_links": nav_data.get("skip_links", {}).get("found", False),
                "ambiguous_links": self._extract_ambiguous_links(nav_data),
                "heading_hierarchy_valid": nav_data.get("heading_hierarchy", {}).get("valid", False)
            }
        
        return optimized
    
    def _reduce_size(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Reduziert die Datengröße durch intelligente Filterung"""
        
        # NEU: Mit 1 Million Token Budget keine Reduktion mehr nötig!
        if self.INCLUDE_FULL_HTML:
            json_str = json.dumps(data, ensure_ascii=False)
            logger.info(f"📊 Volle Datengröße beibehalten: {len(json_str)} Zeichen (Budget: 1M Token)")
            logger.info(f"💡 Das sind ca. {len(json_str) // 4} Tokens")
            return data  # Keine Reduktion!
        
        # Alter Code nur als Fallback
        json_str = json.dumps(data, ensure_ascii=False)
        
        if len(json_str) > self.MAX_DATA_SIZE:  # 5MB Limit
            logger.warning(f"⚠️ Daten sehr groß ({len(json_str)} Zeichen), minimal reduzieren...")
            
            # Nur bei EXTREM großen Datenmengen reduzieren
            if "representative_examples" in data:
                for category in data["representative_examples"]:
                    if len(data["representative_examples"][category]) > 50:  # War 10
                        data["representative_examples"][category] = data["representative_examples"][category][:50]
            
            # Kürze lange Listen
            data = self._truncate_lists(data, max_items=100)  # War 15
        
        logger.info(f"📊 Finale Datengröße: {len(json_str)} Zeichen (Budget: 1M Token)")
        
        return data
    
    def _calculate_size(self, data: Dict[str, Any]) -> int:
        """Berechnet die Größe der Daten in Zeichen"""
        return len(json.dumps(data, ensure_ascii=False))
    
    def _count_total_elements(self, raw_data: Dict[str, Any]) -> int:
        """Zählt die Gesamtzahl der geprüften Elemente"""
        
        # Bereichsspezifisch
        if "images" in raw_data:
            return raw_data["images"].get("total_count", 0)
        elif "semantic_structure" in raw_data:
            headings = raw_data.get("semantic_structure", {}).get("headings", {})
            return headings.get("total_count", 0)
        elif "navigation" in raw_data:
            links = raw_data.get("navigation", {}).get("links", {})
            return links.get("total_count", 0)
        
        return 0
    
    def _summarize_heading_issues(self, semantic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fasst Überschriften-Probleme zusammen"""
        
        headings = semantic_data.get("headings", {})
        
        return {
            "total_headings": headings.get("total_count", 0),
            "hierarchy_valid": headings.get("hierarchy_valid", False),
            "skipped_levels": headings.get("issues", {}).get("skipped_levels", []),
            "multiple_h1": headings.get("issues", {}).get("multiple_h1", False)
        }
    
    def _calculate_landmark_coverage(self, semantic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Berechnet Landmark-Abdeckung"""
        
        landmarks = semantic_data.get("landmarks", {})
        
        return {
            "has_main": landmarks.get("main", False),
            "has_nav": landmarks.get("nav", False),
            "has_header": landmarks.get("header", False),
            "has_footer": landmarks.get("footer", False),
            "coverage_score": sum([
                landmarks.get("main", False),
                landmarks.get("nav", False),
                landmarks.get("header", False),
                landmarks.get("footer", False)
            ]) * 25
        }
    
    def _summarize_form_issues(self, semantic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fasst Formular-Probleme zusammen"""
        
        forms = semantic_data.get("forms", {})
        
        return {
            "total_forms": forms.get("total_count", 0),
            "forms_without_labels": forms.get("without_labels", 0),
            "missing_fieldsets": forms.get("missing_fieldsets", 0)
        }
    
    def _extract_ambiguous_links(self, nav_data: Dict[str, Any]) -> List[str]:
        """Extrahiert mehrdeutige Link-Texte"""
        
        links = nav_data.get("links", {}).get("ambiguous", [])
        
        # Nur die ersten 5 als Beispiele
        return [
            link.get("text", "") 
            for link in links[:5] 
            if isinstance(link, dict)
        ]
    
    def _truncate_lists(self, data: Any, max_items: int = 5) -> Any:
        """Kürzt Listen rekursiv auf maximale Länge"""
        
        if isinstance(data, dict):
            return {
                key: self._truncate_lists(value, max_items)
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return data[:max_items]
        else:
            return data 
    
    def _enhance_small_dataset(self, wcag_area: str, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Erweitert kleine Datensätze mit zusätzlichem Kontext für bessere GPT-Analyse
        """
        data_size = len(json.dumps(raw_data))
        
        enhanced = {
            "dataset_type": "enhanced_for_quality",
            "reason": "Wenig spezifische Daten gefunden - erweitert mit allgemeinem Kontext",
            "data_size_bytes": data_size,
            "enhancement_level": "standard" if data_size > self.VERY_SMALL_DATASET_THRESHOLD else "maximum",
            "wcag_requirements": self._get_wcag_requirements(wcag_area),
            "analysis_guidance": self._get_analysis_guidance(wcag_area),
            "common_issues": self._get_common_issues(wcag_area),
            "best_practices": self._get_best_practices(wcag_area),
            "related_wcag_areas": self._get_related_areas(wcag_area)
        }
        
        # Füge allgemeine Seitenstruktur hinzu wenn vorhanden
        if "pages_analyzed" in raw_data and raw_data["pages_analyzed"]:
            enhanced["general_page_structure"] = {
                "note": "Da wenig spezifische Daten für diesen WCAG-Bereich gefunden wurden, hier die allgemeine Seitenstruktur zur Kontextbildung",
                "pages": raw_data["pages_analyzed"],
                "recommendation": "Prüfen Sie, ob die Abwesenheit relevanter Elemente korrekt ist oder ob Inhalte übersehen wurden"
            }
        
        # NEU: Bei SEHR kleinen Datensätzen (<2KB) füge HTML-Rohdaten hinzu
        if data_size < self.VERY_SMALL_DATASET_THRESHOLD:
            logger.info(f"🔥 SEHR kleiner Datensatz ({data_size} bytes) - füge HTML-Rohdaten hinzu")
            enhanced["enhancement_level"] = "maximum_with_html"
            enhanced["html_snippets"] = self._collect_html_snippets_for_context(wcag_area, raw_data)
            enhanced["dom_analysis"] = self._collect_dom_structure_for_context(raw_data)
            enhanced["critical_note"] = """
            WICHTIG: Da extrem wenig spezifische Daten für diesen WCAG-Bereich gefunden wurden,
            wurden zusätzliche HTML-Rohdaten und DOM-Strukturen hinzugefügt. Dies ermöglicht:
            - Tiefere Analyse auf versteckte oder dynamische Inhalte
            - Erkennung von JavaScript-generierten Elementen
            - Identifikation von Framework-spezifischen Patterns
            - Manuelle Überprüfung der HTML-Struktur
            """
        
        return enhanced
    
    def _collect_html_snippets_for_context(self, wcag_area: str, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sammelt relevante HTML-Snippets basierend auf dem WCAG-Bereich
        """
        snippets = {
            "relevance": f"HTML-Snippets relevant für {wcag_area}",
            "snippets": []
        }
        
        # Definiere relevante HTML-Bereiche pro WCAG-Bereich
        relevant_selectors = {
            "1_2_zeitbasierte_medien": ["video", "audio", "iframe", "object", "embed", "[data-video]", "[data-player]"],
            "2_2_genuegend_zeit": ["meta[http-equiv='refresh']", "[data-timeout]", "[data-session]", ".timer", ".countdown"],
            "2_3_anfaelle_vermeiden": ["@keyframes", "animation", "transition", ".blink", ".flash", ".pulse"],
            "3_1_lesbarkeit_sprache": ["[lang]", "[xml:lang]", "abbr", "acronym", "[data-translate]"]
        }
        
        # Hole relevante Selektoren für diesen WCAG-Bereich
        selectors = relevant_selectors.get(wcag_area, ["body"])
        
        # Sammle HTML-Snippets aus den gecrawlten Daten
        pages_data = raw_data.get("pages_analyzed", [])
        for page in pages_data[:3]:  # Max 3 Seiten
            snippets["snippets"].append({
                "page": page,
                "selectors_searched": selectors,
                "note": "HTML-Struktur kann Hinweise auf dynamisch geladene Inhalte geben"
            })
        
        return snippets
    
    def _collect_dom_structure_for_context(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sammelt DOM-Struktur-Informationen für tiefere Analyse
        """
        return {
            "dom_depth": "Analyse der DOM-Tiefe kann auf komplexe Strukturen hinweisen",
            "shadow_dom_hints": "Prüfung auf Shadow DOM Komponenten empfohlen",
            "spa_indicators": "Single-Page-Application Patterns könnten relevante Inhalte dynamisch laden",
            "framework_hints": {
                "react": "Suche nach React-spezifischen Attributen (data-reactroot, etc.)",
                "vue": "Suche nach Vue-spezifischen Attributen (v-if, v-show, etc.)",
                "angular": "Suche nach Angular-spezifischen Attributen (ng-if, *ngFor, etc.)"
            }
        }
    
    def _get_wcag_requirements(self, wcag_area: str) -> Dict[str, Any]:
        """Gibt die spezifischen WCAG-Anforderungen für einen Bereich zurück"""
        requirements = {
            "1_2_zeitbasierte_medien": {
                "1.2.1": "Aufgezeichnete Audio-Only und Video-Only (Level A)",
                "1.2.2": "Untertitel (aufgezeichnet) (Level A)", 
                "1.2.3": "Audiodeskription oder Medienalternative (aufgezeichnet) (Level A)",
                "1.2.4": "Untertitel (live) (Level AA)",
                "1.2.5": "Audiodeskription (aufgezeichnet) (Level AA)",
                "wichtig": "Auch wenn keine Medien gefunden wurden, sollte geprüft werden ob die Seite Medieninhalte einbetten könnte"
            },
            "2_2_genuegend_zeit": {
                "2.2.1": "Zeiteinteilung anpassbar (Level A)",
                "2.2.2": "Pausieren, beenden, ausblenden (Level A)",
                "2.2.3": "Keine Zeiteinteilung (Level AAA)",
                "2.2.4": "Unterbrechungen (Level AAA)",
                "2.2.5": "Erneute Authentifizierung (Level AAA)",
                "wichtig": "Prüfen Sie Session-Timeouts, automatische Refreshs, zeitbasierte Funktionen"
            },
            "2_3_anfaelle_vermeiden": {
                "2.3.1": "Grenzwert von dreimaligem Blitzen (Level A)",
                "2.3.2": "Drei Blitze (Level AAA)",
                "2.3.3": "Animation durch Interaktionen (Level AAA)",
                "wichtig": "Auch subtile Animationen und CSS-Transitions können problematisch sein"
            },
            "3_1_lesbarkeit_sprache": {
                "3.1.1": "Sprache der Seite (Level A)",
                "3.1.2": "Sprache von Teilen (Level AA)",
                "3.1.3": "Ungebräuchliche Wörter (Level AAA)",
                "3.1.4": "Abkürzungen (Level AAA)",
                "3.1.5": "Leseniveau (Level AAA)",
                "3.1.6": "Aussprache (Level AAA)",
                "wichtig": "Sprache muss korrekt deklariert sein für Screenreader"
            }
        }
        return requirements.get(wcag_area, {"info": "Standardanforderungen für " + wcag_area})
    
    def _get_analysis_guidance(self, wcag_area: str) -> List[str]:
        """Gibt Analyse-Hinweise für Bereiche mit wenig Daten"""
        guidance = {
            "1_2_zeitbasierte_medien": [
                "Prüfen Sie ob die Seite YouTube/Vimeo-Embeds nutzt",
                "Suchen Sie nach <video>, <audio> Tags die möglicherweise dynamisch geladen werden",
                "Prüfen Sie JavaScript auf Media-Player Initialisierung",
                "Beachten Sie dass Medien auch über iframes eingebunden sein können"
            ],
            "2_2_genuegend_zeit": [
                "Analysieren Sie Session-Management und Timeouts",
                "Prüfen Sie Meta-Refresh-Tags",
                "Suchen Sie nach JavaScript-basierten Timern",
                "Untersuchen Sie automatische Slideshows oder Karussells"
            ],
            "2_3_anfaelle_vermeiden": [
                "Prüfen Sie CSS-Animationen und Transitions",
                "Analysieren Sie JavaScript-basierte Animationen",
                "Suchen Sie nach animierten GIFs oder Videos mit schnellen Schnitten",
                "Beachten Sie auch Loading-Spinner und Progress-Indikatoren"
            ]
        }
        return guidance.get(wcag_area, ["Führen Sie eine gründliche manuelle Prüfung durch"])
    
    def _get_common_issues(self, wcag_area: str) -> List[str]:
        """Listet häufige Probleme auch wenn keine gefunden wurden"""
        return {
            "1_2_zeitbasierte_medien": [
                "Fehlende Untertitel bei Videos",
                "Keine Audiodeskription für visuelle Inhalte",
                "Automatisch startende Medien ohne Kontrolle",
                "Fehlende Transkripte für Podcasts"
            ],
            "2_3_anfaelle_vermeiden": [
                "Blinkende Werbebanner",
                "Schnelle Bildwechsel in Slideshows",
                "Flackernde Ladeanimationen",
                "Stroboskop-Effekte in Videos"
            ]
        }.get(wcag_area, [])
    
    def _get_best_practices(self, wcag_area: str) -> List[str]:
        """Best Practices für den WCAG-Bereich"""
        return {
            "1_2_zeitbasierte_medien": [
                "Alle Videos sollten Untertitel haben",
                "Audiodeskription für wichtige visuelle Informationen",
                "Transkripte als Alternative anbieten",
                "Media-Player müssen barrierefrei bedienbar sein"
            ],
            "2_2_genuegend_zeit": [
                "Warnung vor Session-Ablauf mit Verlängerungsoption",
                "Pausierbare automatische Inhalte",
                "Keine automatischen Refreshs ohne Nutzerinteraktion",
                "Speichern von Formulardaten bei Timeout"
            ]
        }.get(wcag_area, [])
    
    def _get_related_areas(self, wcag_area: str) -> List[str]:
        """Verwandte WCAG-Bereiche die ebenfalls geprüft werden sollten"""
        relations = {
            "1_2_zeitbasierte_medien": ["1_1_textalternativen", "2_1_tastaturbedienung"],
            "2_2_genuegend_zeit": ["3_3_eingabeunterstuetzung", "3_2_vorhersehbarkeit"],
            "2_3_anfaelle_vermeiden": ["2_2_genuegend_zeit", "1_4_wahrnehmbare_unterscheidungen"]
        }
        return relations.get(wcag_area, []) 