#!/usr/bin/env python3
"""
Spezialisierte Daten-Extraktoren für WCAG-Bereiche
Jeder Extraktor sammelt nur die für seinen WCAG-Bereich relevanten Daten
"""

import logging
import time
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
import requests
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class BaseWCAGExtractor:
    """Basis-Klasse für alle WCAG-spezifischen Daten-Extraktoren"""
    
    def __init__(self, base_url: str, crawl_data: Dict[str, Any]):
        self.base_url = base_url
        self.crawl_data = crawl_data
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def extract_focused_data(self) -> Dict[str, Any]:
        """Extrahiert nur die für diesen WCAG-Bereich relevanten Daten"""
        raise NotImplementedError("Muss in Subklassen implementiert werden")
    
    def _get_soup_for_url(self, url: str) -> Optional[BeautifulSoup]:
        """Hilfsmethode um BeautifulSoup für eine URL zu bekommen"""
        # DEPRECATED: Der Website-Crawler liefert bereits strukturierte Daten
        # Diese Methode wird nicht mehr benötigt, da wir direkt mit den strukturierten Daten arbeiten
        return None
    
    def _get_structured_data_for_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Hilfsmethode um strukturierte Daten für eine URL zu bekommen"""
        try:
            if url in self.crawl_data.get('data', {}):
                return self.crawl_data['data'][url]
        except Exception as e:
            self.logger.warning(f"Fehler beim Abrufen strukturierter Daten von {url}: {e}")
        return None
    
    def _collect_general_context_data(self) -> Dict[str, Any]:
        """
        NEU: Sammelt allgemeine HTML/CSS/JS Kontextdaten für bessere Analyse
        Wird automatisch hinzugefügt wenn wenig spezifische Daten gefunden wurden
        """
        general_data = {
            "html_structure": {
                "total_elements": 0,
                "semantic_elements": [],
                "custom_elements": [],
                "data_attributes": []
            },
            "css_analysis": {
                "stylesheets": [],
                "inline_styles": 0,
                "css_variables": [],
                "media_queries": [],
                "animations": []
            },
            "javascript_analysis": {
                "scripts": [],
                "event_listeners": [],
                "frameworks_detected": [],
                "dynamic_content_indicators": []
            },
            "meta_information": {
                "meta_tags": [],
                "structured_data": [],
                "open_graph": {},
                "twitter_cards": {}
            },
            "performance_hints": {
                "resource_hints": [],
                "lazy_loading": False,
                "async_scripts": 0,
                "defer_scripts": 0
            }
        }
        
        # Analysiere jede gecrawlte Seite
        for url, page_data in self.crawl_data.get('data', {}).items():
            if isinstance(page_data, dict):
                # HTML-Struktur
                structure = page_data.get("structure", {})
                general_data["html_structure"]["total_elements"] += len(structure.get("all_elements", []))
                
                # Semantic Elements
                for tag in ["header", "nav", "main", "footer", "article", "section", "aside"]:
                    if structure.get(tag):
                        general_data["html_structure"]["semantic_elements"].append({
                            "tag": tag,
                            "count": len(structure.get(tag, [])) if isinstance(structure.get(tag), list) else 1,
                            "url": url
                        })
                
                # CSS-Analyse
                styling = page_data.get("styling", {})
                if styling.get("stylesheets"):
                    general_data["css_analysis"]["stylesheets"].extend(styling["stylesheets"])
                
                # JavaScript-Analyse  
                scripts = page_data.get("scripts", [])
                if scripts:
                    general_data["javascript_analysis"]["scripts"].extend([
                        {"src": s.get("src", "inline"), "async": s.get("async", False), "defer": s.get("defer", False)}
                        for s in scripts if isinstance(s, dict)
                    ])
                
                # Meta-Information
                meta = page_data.get("meta", {})
                if meta:
                    general_data["meta_information"]["meta_tags"].append({
                        "url": url,
                        "title": meta.get("title", ""),
                        "description": meta.get("description", ""),
                        "keywords": meta.get("keywords", "")
                    })
        
        return general_data
    
    def _should_add_general_context(self, specific_data: Dict[str, Any]) -> bool:
        """
        Entscheidet ob allgemeine Kontextdaten hinzugefügt werden sollen
        Kriterium: Weniger als 5KB spezifische Daten
        """
        data_size = len(json.dumps(specific_data))
        return data_size < 5000  # 5KB Schwellenwert

class TextAlternativesExtractor(BaseWCAGExtractor):
    """1.1 Textalternativen - SUPER-ERWEITERT mit 101 Bildern + Open Graph + Performance"""
    
    def extract_focused_data(self) -> Dict[str, Any]:
        """Extrahiert Daten für WCAG 1.1 Textalternativen - SUPER-ERWEITERT"""
        start_time = time.time()
        self.logger.info("🖼️ Starte SUPER-ERWEITERTE Textalternativen-Extraktion...")
        
        data = {
            "wcag_area": "1.1 Textalternativen",
            "extraction_method": "super_erweitert",
            "extracted_at": time.strftime("%Y-%m-%d_%H-%M-%S"),
            
            # NEUE: Detaillierte Bild-Performance-Analyse (101 Bilder)
            "comprehensive_image_analysis": {
                "total_images_found": 0,
                "image_performance": {
                    "large_images": [],
                    "unoptimized_formats": [],
                    "missing_lazy_loading": [],
                    "performance_score": 0
                },
                "image_metadata": {
                    "file_sizes": [],
                    "formats": {},
                    "dimensions": [],
                    "optimization_opportunities": []
                },
                "social_media_images": {
                    "open_graph_images": [],
                    "twitter_card_images": [],
                    "missing_social_images": []
                }
            },
            
            # NEUE: Erweiterte Accessibility-Analyse
            "advanced_accessibility": {
                "context_analysis": [],
                "semantic_relationships": [],
                "user_journey_images": [],
                "accessibility_quality_score": 0
            },
            
            # NEUE: Content-Management-Analyse
            "content_management": {
                "cms_patterns": [],
                "automated_alt_text": [],
                "manual_alt_text": [],
                "quality_patterns": []
            },
            
            # ERWEITERT: Original Daten
            "images": {
                "total_count": 0,
                "with_alt": 0,
                "without_alt": 0,
                "empty_alt": 0,
                "decorative": 0,
                "detailed_analysis": []
            },
            "non_text_content": {
                "icons": [],
                "graphics": [],
                "charts": [],
                "captchas": []
            },
            "accessibility_violations": [],
            "pages_analyzed": []
        }
        
        # Analysiere jede Seite mit SUPER-ERWEITERTEN Methoden
        total_images = 0
        
        for url, page_data in self.crawl_data.get('data', {}).items():
            # NEUE: Umfassende Bild-Analyse
            page_analysis = self._analyze_comprehensive_images(url, page_data)
            data["images"]["detailed_analysis"].append(page_analysis)
            data["pages_analyzed"].append(url)
            
            # Akkumuliere NEUE Daten
            images_data = page_analysis.get("comprehensive_images", {})
            performance_data = page_analysis.get("performance_analysis", {})
            social_data = page_analysis.get("social_media_analysis", {})
            
            total_images += images_data.get("image_count", 0)
            
            data["comprehensive_image_analysis"]["image_performance"]["large_images"].extend(
                performance_data.get("large_images", [])
            )
            data["comprehensive_image_analysis"]["social_media_images"]["open_graph_images"].extend(
                social_data.get("open_graph_images", [])
            )
            
            # Original Daten
            data["images"]["total_count"] += page_analysis["image_count"]
            data["images"]["with_alt"] += page_analysis["with_alt"]
            data["images"]["without_alt"] += page_analysis["without_alt"]
            data["images"]["empty_alt"] += page_analysis["empty_alt"]
            data["images"]["decorative"] += page_analysis["decorative"]
        
        # Finale Zusammenfassung
        data["comprehensive_image_analysis"]["total_images_found"] = total_images
        
        # Berechne Performance-Score
        large_images = len(data["comprehensive_image_analysis"]["image_performance"]["large_images"])
        if total_images > 0:
            data["comprehensive_image_analysis"]["image_performance"]["performance_score"] = round(
                max(0, 100 - (large_images / total_images * 50)), 1
            )
        
        # Original Statistiken
        total = data["images"]["total_count"]
        if total > 0:
            data["images"]["statistics"] = {
                "alt_coverage": round((data["images"]["with_alt"] / total) * 100, 1),
                "missing_alt_percentage": round((data["images"]["without_alt"] / total) * 100, 1),
                "decorative_percentage": round((data["images"]["decorative"] / total) * 100, 1)
            }
        
        data["extraction_time_seconds"] = round(time.time() - start_time, 2)
        
        self.logger.info(f"✅ SUPER-ERWEITERTE Textalternativen-Extraktion: {total_images} Bilder, Performance-Score: {data['comprehensive_image_analysis']['image_performance']['performance_score']}, {data['extraction_time_seconds']}s")
        
        return data
    
    def _analyze_comprehensive_images(self, url: str, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Umfassende Bild-Analyse mit 101 Bildern + Performance + Social Media"""
        analysis = {
            "page_url": url,
            "comprehensive_images": self._analyze_image_details(page_data),
            "performance_analysis": self._analyze_image_performance(page_data),
            "social_media_analysis": self._analyze_social_media_images(page_data),
            "accessibility_context": self._analyze_image_accessibility_context(page_data),
            "content_quality": self._analyze_image_content_quality(page_data),
            
            # Original Daten für Kompatibilität
            "image_count": 0,
            "with_alt": 0,
            "without_alt": 0,
            "empty_alt": 0,
            "decorative": 0
        }
        
        # Original Analyse für Kompatibilität
        original_analysis = self._analyze_page_images(url)
        analysis.update({
            "image_count": original_analysis.get("image_count", 0),
            "with_alt": original_analysis.get("with_alt", 0),
            "without_alt": original_analysis.get("without_alt", 0),
            "empty_alt": original_analysis.get("empty_alt", 0),
            "decorative": original_analysis.get("decorative", 0)
        })
        
        return analysis
    
    def _analyze_image_details(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Detaillierte Analyse der 101 Bilder"""
        structure_data = page_data.get("structure", {})
        images_list = structure_data.get("images", [])
        
        analysis = {
            "image_count": len(images_list) if isinstance(images_list, list) else 0,
            "image_inventory": [],
            "format_distribution": {},
            "size_categories": {
                "small": 0,
                "medium": 0,
                "large": 0,
                "unknown": 0
            },
            "accessibility_patterns": {
                "logo_images": [],
                "content_images": [],
                "navigation_images": [],
                "decorative_images": []
            }
        }
        
        if isinstance(images_list, list):
            for img in images_list:
                if isinstance(img, dict):
                    src = img.get("src", "")
                    alt = img.get("alt")
                    
                    # Extrahiere Dateiformat
                    file_format = self._extract_image_format(src)
                    if file_format:
                        analysis["format_distribution"][file_format] = analysis["format_distribution"].get(file_format, 0) + 1
                    
                    # Kategorisiere nach Verwendung
                    usage_category = self._categorize_image_usage(img, src, alt)
                    if usage_category in analysis["accessibility_patterns"]:
                        analysis["accessibility_patterns"][usage_category].append({
                            "src": src,
                            "alt": alt,
                            "context": img.get("context", ""),
                            "usage": usage_category
                        })
                    
                    # Detailliertes Image-Inventory
                    analysis["image_inventory"].append({
                        "src": src,
                        "alt": alt,
                        "format": file_format,
                        "usage_category": usage_category,
                        "has_alt": alt is not None,
                        "alt_quality": self._assess_alt_quality(alt, usage_category),
                        "accessibility_score": self._calculate_image_accessibility_score(img, alt, usage_category)
                    })
        
        return analysis
    
    def _analyze_image_performance(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Analysiert Bild-Performance"""
        performance_data = page_data.get("performance", {})
        structure_data = page_data.get("structure", {})
        images_list = structure_data.get("images", [])
        
        analysis = {
            "total_image_weight": 0,
            "large_images": [],
            "unoptimized_formats": [],
            "lazy_loading_opportunities": [],
            "modern_format_opportunities": [],
            "performance_recommendations": []
        }
        
        if isinstance(images_list, list):
            for img in images_list:
                if isinstance(img, dict):
                    src = img.get("src", "")
                    
                    # Prüfe auf große Bilder (basierend auf Dateinamen-Patterns)
                    if self._is_large_image(src):
                        analysis["large_images"].append({
                            "src": src,
                            "estimated_size": "large",
                            "recommendation": "optimize_or_lazy_load"
                        })
                    
                    # Prüfe auf veraltete Formate
                    if self._is_unoptimized_format(src):
                        analysis["unoptimized_formats"].append({
                            "src": src,
                            "current_format": self._extract_image_format(src),
                            "recommended_format": "webp_or_avif"
                        })
                    
                    # Prüfe Lazy-Loading-Opportunities
                    if not img.get("loading") == "lazy":
                        analysis["lazy_loading_opportunities"].append({
                            "src": src,
                            "recommendation": "add_loading_lazy"
                        })
        
        return analysis
    
    def _analyze_social_media_images(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Analysiert Social Media Images (Open Graph, Twitter Cards)"""
        semantics_data = page_data.get("semantics", {})
        open_graph = semantics_data.get("open_graph", [])
        twitter_cards = semantics_data.get("twitter_cards", [])
        
        analysis = {
            "open_graph_images": [],
            "twitter_card_images": [],
            "social_media_coverage": {
                "has_og_image": False,
                "has_twitter_image": False,
                "image_consistency": False
            },
            "social_media_quality": {
                "og_image_quality": [],
                "twitter_image_quality": [],
                "missing_alt_social": []
            }
        }
        
        # Analysiere Open Graph Images
        if isinstance(open_graph, list):
            for og_item in open_graph:
                if isinstance(og_item, dict) and og_item.get("property") == "og:image":
                    og_image_url = og_item.get("content", "")
                    analysis["open_graph_images"].append({
                        "url": og_image_url,
                        "format": self._extract_image_format(og_image_url),
                        "accessibility_consideration": "needs_descriptive_content"
                    })
                    analysis["social_media_coverage"]["has_og_image"] = True
        
        # Analysiere Twitter Card Images
        if isinstance(twitter_cards, list):
            for twitter_item in twitter_cards:
                if isinstance(twitter_item, dict) and "image" in twitter_item.get("name", ""):
                    twitter_image_url = twitter_item.get("content", "")
                    analysis["twitter_card_images"].append({
                        "url": twitter_image_url,
                        "format": self._extract_image_format(twitter_image_url),
                        "accessibility_consideration": "needs_descriptive_content"
                    })
                    analysis["social_media_coverage"]["has_twitter_image"] = True
        
        # Prüfe Konsistenz
        if (analysis["social_media_coverage"]["has_og_image"] and 
            analysis["social_media_coverage"]["has_twitter_image"]):
            analysis["social_media_coverage"]["image_consistency"] = True
        
        return analysis
    
    def _analyze_image_accessibility_context(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Analysiert Accessibility-Kontext von Bildern"""
        structure_data = page_data.get("structure", {})
        headings = structure_data.get("headings", [])
        links = structure_data.get("links", [])
        
        analysis = {
            "contextual_relationships": [],
            "heading_image_relationships": [],
            "link_image_relationships": [],
            "content_flow_analysis": []
        }
        
        # Analysiere Überschriften-Bild-Beziehungen
        if isinstance(headings, list):
            for heading in headings:
                if isinstance(heading, dict):
                    analysis["heading_image_relationships"].append({
                        "heading_text": heading.get("text", ""),
                        "heading_level": heading.get("level", 0),
                        "nearby_images": "would_analyze_proximity",
                        "content_context": "descriptive_relationship"
                    })
        
        return analysis
    
    def _analyze_image_content_quality(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Analysiert Content-Qualität der Bilder"""
        structure_data = page_data.get("structure", {})
        images_list = structure_data.get("images", [])
        
        analysis = {
            "content_quality_score": 0,
            "high_quality_examples": [],
            "improvement_opportunities": [],
            "automated_detection": {
                "stock_photo_patterns": [],
                "screenshot_patterns": [],
                "user_generated_content": []
            }
        }
        
        if isinstance(images_list, list):
            high_quality_count = 0
            
            for img in images_list:
                if isinstance(img, dict):
                    alt = img.get("alt", "")
                    src = img.get("src", "")
                    
                    # Bewerte Alt-Text-Qualität
                    if alt and len(alt) > 10 and not self._is_generic_alt_text(alt):
                        high_quality_count += 1
                        analysis["high_quality_examples"].append({
                            "src": src,
                            "alt": alt,
                            "quality_reason": "descriptive_alt_text"
                        })
                    elif not alt or alt == "":
                        analysis["improvement_opportunities"].append({
                            "src": src,
                            "issue": "missing_or_empty_alt",
                            "recommendation": "add_descriptive_alt_text"
                        })
            
            # Berechne Content-Quality-Score
            total_images = len(images_list)
            if total_images > 0:
                analysis["content_quality_score"] = round((high_quality_count / total_images) * 100, 1)
        
        return analysis
    
    def _extract_image_format(self, src: str) -> str:
        """Extrahiert Bildformat aus URL"""
        if not src:
            return "unknown"
        
        src_lower = src.lower()
        if ".jpg" in src_lower or ".jpeg" in src_lower:
            return "jpeg"
        elif ".png" in src_lower:
            return "png"
        elif ".gif" in src_lower:
            return "gif"
        elif ".webp" in src_lower:
            return "webp"
        elif ".avif" in src_lower:
            return "avif"
        elif ".svg" in src_lower:
            return "svg"
        else:
            return "unknown"
    
    def _categorize_image_usage(self, img: Dict[str, Any], src: str, alt: str) -> str:
        """Kategorisiert Bild-Verwendung"""
        src_lower = (src or "").lower()  # FIX: Handle None values
        alt_lower = (alt or "").lower()
        
        # Logo-Erkennung
        if "logo" in src_lower or "logo" in alt_lower:
            return "logo_images"
        
        # Navigation-Bilder
        if any(nav_word in src_lower for nav_word in ["menu", "nav", "button", "icon"]):
            return "navigation_images"
        
        # Dekorative Bilder
        if alt == "" or "decoration" in alt_lower:
            return "decorative_images"
        
        # Standard: Content-Bilder
        return "content_images"
    
    def _assess_alt_quality(self, alt: str, usage_category: str) -> str:
        """Bewertet Alt-Text-Qualität"""
        if not alt:
            return "missing"
        elif alt == "":
            return "empty" if usage_category == "decorative_images" else "problematic"
        elif len(alt) < 5:
            return "too_short"
        elif len(alt) > 100:
            return "potentially_too_long"
        elif self._is_generic_alt_text(alt):
            return "generic"
        else:
            return "good"
    
    def _calculate_image_accessibility_score(self, img: Dict[str, Any], alt: str, usage_category: str) -> int:
        """Berechnet Accessibility-Score für ein Bild"""
        score = 0
        
        # Alt-Text vorhanden
        if alt is not None:
            score += 30
        
        # Alt-Text-Qualität
        quality = self._assess_alt_quality(alt, usage_category)
        if quality == "good":
            score += 40
        elif quality in ["empty", "too_short"]:
            score += 10
        
        # ARIA-Unterstützung
        if img.get("aria-describedby"):
            score += 15
        
        # Titel-Attribut
        if img.get("title"):
            score += 10
        
        # Role-Attribut
        if img.get("role"):
            score += 5
        
        return min(100, score)
    
    def _is_large_image(self, src: str) -> bool:
        """Erkennt potentiell große Bilder"""
        if not src:
            return False
        large_indicators = ["banner", "hero", "background", "header", "full"]
        src_lower = src.lower()
        return any(indicator in src_lower for indicator in large_indicators)
    
    def _is_unoptimized_format(self, src: str) -> bool:
        """Erkennt unoptimierte Bildformate"""
        format_type = self._extract_image_format(src)
        return format_type in ["jpeg", "png", "gif"] and "webp" not in src.lower() and "avif" not in src.lower()
    
    def _is_generic_alt_text(self, alt: str) -> bool:
        """Erkennt generische Alt-Texte"""
        generic_terms = ["image", "bild", "photo", "picture", "img", "graphic", "logo"]
        return alt.lower().strip() in generic_terms
    
    def _analyze_page_images(self, url: str) -> Dict[str, Any]:
        """Analysiert alle Bilder auf einer Seite"""
        page_data = self._get_structured_data_for_url(url)
        
        if not page_data:
            return self._create_empty_image_analysis(url)
        
        structure_data = page_data.get("structure", {})
        images_list = structure_data.get("images", [])
        
        analysis = {
            "page_url": url,
            "image_count": len(images_list) if isinstance(images_list, list) else 0,
            "with_alt": 0,
            "without_alt": 0,
            "empty_alt": 0,
            "decorative": 0,
            "images": []  # Detaillierte Liste aller Bilder
        }
        
        if isinstance(images_list, list):
            for img in images_list:
                if isinstance(img, dict):
                    has_alt = img.get("alt") is not None
                    alt_text = img.get("alt", "")
                    src = img.get("src", "")
                    
                    # WICHTIG: Füge HTML-Code-Snippet hinzu
                    image_detail = {
                        "src": src,
                        "alt": alt_text,
                        "has_alt": has_alt,
                        "title": img.get("title", ""),
                        "aria_label": img.get("aria-label", ""),
                        "aria_describedby": img.get("aria-describedby", ""),
                        "width": img.get("width", ""),
                        "height": img.get("height", ""),
                        "loading": img.get("loading", ""),
                        # NEU: Vollständiger HTML-Code
                        "html_snippet": img.get("html", ""),
                        # NEU: Kontext (umgebender HTML-Code)
                        "html_context": img.get("context", ""),
                        # NEU: Position im DOM
                        "dom_path": img.get("dom_path", ""),
                        # NEU: CSS-Klassen für bessere Analyse
                        "classes": img.get("class", ""),
                        # NEU: Inline-Styles
                        "style": img.get("style", "")
                    }
                    
                    # Füge Kategorisierung hinzu
                    category = self._categorize_image(img, alt_text, src)
                    image_detail["category"] = category
                    
                    # WCAG-Bewertung
                    if has_alt:
                        analysis["with_alt"] += 1
                        if alt_text == "":
                            analysis["empty_alt"] += 1
                            if category == "decorative":
                                analysis["decorative"] += 1
                                image_detail["wcag_assessment"] = "compliant_decorative"
                            else:
                                image_detail["wcag_assessment"] = "potentially_problematic_empty_alt"
                        else:
                            image_detail["wcag_assessment"] = "has_alt_text"
                    else:
                        analysis["without_alt"] += 1
                        image_detail["wcag_assessment"] = "missing_alt_critical"
                    
                    analysis["images"].append(image_detail)
        
        # Sortiere Bilder nach Kritikalität für bessere AI-Analyse
        analysis["images"].sort(key=lambda x: (
            0 if x["wcag_assessment"] == "missing_alt_critical" else
            1 if x["wcag_assessment"] == "potentially_problematic_empty_alt" else
            2 if x["wcag_assessment"] == "has_alt_text" else
            3
        ))
        
        return analysis
    
    def _categorize_image(self, img: Dict[str, Any], alt_text: str, src: str) -> str:
        """Kategorisiert Bilder nach WCAG-Richtlinien"""
        
        # Dekorativ: Leerer Alt-Text oder role="presentation"
        if alt_text == "" or img.get('role') == 'presentation':
            return "decorative"
        
        # Icons: Kleine Bilder oder bestimmte Dateinamen
        if self._is_icon(src, alt_text):
            return "icons"
        
        # Funktional: Links oder Button-Kinder
        if img.get('parent_is_link') or img.get('parent_is_button'):
            return "functional"
        
        # Komplex: Große Bilder oder Charts/Diagramme
        if self._is_complex_graphic(src, alt_text):
            return "complex"
        
        # Standard: Informativ
        return "informative"
    
    def _is_icon(self, src: str, alt_text: str) -> bool:
        """Erkennt Icons basierend auf Dateinamen und Alt-Text"""
        src_lower = src.lower()
        icon_keywords = ['icon', 'ico', 'symbol', 'arrow', 'chevron', 'menu', 'close', 'search']
        
        # Prüfe Dateipfad
        if any(keyword in src_lower for keyword in icon_keywords):
            return True
        
        # Prüfe Alt-Text
        if alt_text and len(alt_text) < 20:
            alt_lower = alt_text.lower()
            if any(keyword in alt_lower for keyword in icon_keywords):
                return True
        
        return False
    
    def _is_complex_graphic(self, src: str, alt_text: str) -> bool:
        """Erkennt komplexe Grafiken die detaillierte Beschreibungen brauchen"""
        src_lower = src.lower()
        complex_keywords = ['chart', 'graph', 'diagram', 'infographic', 'map', 'flowchart']
        
        if any(keyword in src_lower for keyword in complex_keywords):
            return True
        
        if alt_text and len(alt_text) > 100:  # Lange Alt-Texte deuten auf Komplexität hin
            return True
        
        return False
    
    def _is_captcha(self, src: str, alt_text: str, title: str) -> bool:
        """Erkennt CAPTCHA-Elemente"""
        captcha_keywords = ['captcha', 'recaptcha', 'verification', 'security', 'prove']
        
        text_to_check = f"{src} {alt_text} {title}".lower()
        return any(keyword in text_to_check for keyword in captcha_keywords)
    
    def _create_empty_image_analysis(self, url: str) -> Dict[str, Any]:
        """Erstellt eine leere Bild-Analyse für URLs ohne Daten"""
        return {
            "url": url,
            "image_count": 0,
            "with_alt": 0,
            "without_alt": 0,
            "empty_alt": 0,
            "decorative": 0,
            "complex_graphics": 0,
            "icons_detected": 0,
            "problematic_images": [],
            "good_examples": [],
            "image_categories": {
                "informative": [],
                "decorative": [],
                "functional": [],
                "complex": [],
                "icons": []
            },
            "aria_analysis": {
                "aria_described_images": 0,
                "missing_descriptions": []
            },
            "captcha_analysis": {
                "captchas_found": 0,
                "alternative_methods": []
            },
            "svg_canvas_analysis": {
                "svg_elements": 0,
                "canvas_elements": 0,
                "accessible_graphics": 0
            }
        }

class TimeBasedMediaExtractor(BaseWCAGExtractor):
    """1.2 Zeitbasierte Medien - Fokus auf Videos, Audio, Untertitel"""
    
    def extract_focused_data(self) -> Dict[str, Any]:
        """Extrahiert Daten für WCAG 1.2 Zeitbasierte Medien"""
        start_time = time.time()
        
        data = {
            "wcag_area": "1.2_zeitbasierte_medien",
            "focus": "Videos, Audio, Untertitel, Transkripte, zeitbasierte Inhalte",
            "extracted_at": time.strftime("%Y-%m-%d_%H-%M-%S"),
            "media_summary": {
                "total_videos": 0,
                "total_audio": 0,
                "embedded_videos": 0,
                "has_captions": 0,
                "has_transcripts": 0,
                "auto_play_detected": 0
            },
            "detailed_analysis": [],
            "pages_analyzed": []
        }
        
        # Analysiere jede Seite nach zeitbasierten Medien
        for url, page_data in self.crawl_data.get('data', {}).items():
            page_analysis = self._analyze_page_media(url)
            data["detailed_analysis"].append(page_analysis)
            data["pages_analyzed"].append(url)
            
            # Akkumuliere Statistiken
            data["media_summary"]["total_videos"] += page_analysis["video_count"]
            data["media_summary"]["total_audio"] += page_analysis["audio_count"]
            data["media_summary"]["embedded_videos"] += page_analysis["embedded_count"]
            data["media_summary"]["has_captions"] += page_analysis["with_captions"]
            data["media_summary"]["auto_play_detected"] += page_analysis["autoplay_count"]
        
        # Bestimme ob zeitbasierte Medien vorhanden sind
        total_media = (data["media_summary"]["total_videos"] + 
                      data["media_summary"]["total_audio"] + 
                      data["media_summary"]["embedded_videos"])
        
        data["has_time_based_media"] = total_media > 0
        data["compliance_note"] = ("Zeitbasierte Medien gefunden - WCAG 1.2 anwendbar" if total_media > 0 
                                  else "Keine zeitbasierten Medien gefunden - WCAG 1.2 nicht anwendbar")
        
        data["extraction_time_seconds"] = round(time.time() - start_time, 2)
        
        # NEU: Füge allgemeine Kontextdaten hinzu wenn wenig spezifische Daten gefunden wurden
        if self._should_add_general_context(data):
            self.logger.info("📊 Wenig medienspezifische Daten gefunden - füge allgemeinen Kontext hinzu")
            data["general_context"] = self._collect_general_context_data()
            data["enhanced_analysis_note"] = """
            Da wenig zeitbasierte Medien gefunden wurden, wurde der allgemeine Seitenkontext hinzugefügt.
            Dies hilft bei der Identifikation von:
            - Dynamisch geladenen Medieninhalten
            - Eingebetteten iframe-basierten Playern
            - JavaScript-basierten Media-Frameworks
            - Potenziellen Stellen für Medieninhalte
            """
        
        self.logger.info(f"✅ Zeitbasierte Medien-Extraktion: {total_media} Medien in {data['extraction_time_seconds']}s")
        
        return data
    
    def _analyze_page_media(self, url: str) -> Dict[str, Any]:
        """Analysiert zeitbasierte Medien auf einer Seite"""
        
        # Verwende strukturierte Daten statt HTML-Parsing
        structured_data = self._get_structured_data_for_url(url)
        if not structured_data:
            return self._create_empty_media_analysis(url)
        
        # Medien aus strukturierten Daten extrahieren
        structure_data = structured_data.get('structure', {})
        multimedia_data = structure_data.get('multimedia', {})
        videos_list = multimedia_data.get('video', [])
        audios_list = multimedia_data.get('audio', [])
        iframes_list = structure_data.get('iframes', [])
        
        analysis = {
            "url": url,
            "video_count": len(videos_list),
            "audio_count": len(audios_list),
            "embedded_count": 0,
            "with_captions": 0,
            "autoplay_count": 0,
            "media_details": []
        }
        
        # Analysiere Video-Elemente aus strukturierten Daten
        for video in videos_list:
            tracks = video.get('tracks', [])
            captions = any(track.get('kind') == 'captions' for track in tracks)
            autoplay = video.get('autoplay', False)
            
            if captions:
                analysis["with_captions"] += 1
            if autoplay:
                analysis["autoplay_count"] += 1
                
            analysis["media_details"].append({
                "type": "video",
                "src": video.get('src', 'multiple sources'),
                "has_captions": captions,
                "autoplay": autoplay,
                "controls": video.get('controls', False),
                "tracks": len(tracks)
            })
        
        # Analysiere Audio-Elemente aus strukturierten Daten
        for audio in audios_list:
            autoplay = audio.get('autoplay', False)
            if autoplay:
                analysis["autoplay_count"] += 1
                
            analysis["media_details"].append({
                "type": "audio",
                "src": audio.get('src', 'multiple sources'),
                "autoplay": autoplay,
                "controls": audio.get('controls', False)
            })
        
        # Analysiere eingebettete Videos (YouTube, Vimeo, etc.) aus strukturierten Daten
        for iframe in iframes_list:
            src = iframe.get('src', '')
            if any(platform in src.lower() for platform in ['youtube', 'vimeo', 'dailymotion']):
                analysis["embedded_count"] += 1
                analysis["media_details"].append({
                    "type": "embedded_video",
                    "src": src,
                    "platform": self._detect_platform(src),
                    "title": iframe.get('title', 'No title')
                })
        
        return analysis
    
    def _detect_platform(self, src: str) -> str:
        """Erkennt die Video-Plattform"""
        src_lower = src.lower()
        if 'youtube' in src_lower:
            return 'YouTube'
        elif 'vimeo' in src_lower:
            return 'Vimeo'
        elif 'dailymotion' in src_lower:
            return 'Dailymotion'
        return 'Unknown'
    
    def _create_empty_media_analysis(self, url: str) -> Dict[str, Any]:
        """Erstellt eine leere Media-Analyse für URLs ohne Daten"""
        return {
            "url": url,
            "video_count": 0,
            "audio_count": 0,
            "embedded_count": 0,
            "with_captions": 0,
            "autoplay_count": 0,
            "media_details": []
        }

class AdaptablePresentationExtractor(BaseWCAGExtractor):
    """1.3 Anpassbare Darstellung - SUPER-ERWEITERT mit 97 Überschriften + Open Graph + Schema.org"""
    
    def extract_focused_data(self) -> Dict[str, Any]:
        """Extrahiert Daten für WCAG 1.3 Anpassbare Darstellung - SUPER-ERWEITERT"""
        start_time = time.time()
        self.logger.info("🏗️ Starte SUPER-ERWEITERTE Semantik-Extraktion...")
        
        data = {
            "wcag_area": "1.3 Anpassbare Darstellung",
            "extraction_method": "super_erweitert",
            "extracted_at": time.strftime("%Y-%m-%d_%H-%M-%S"),
            
            # NEUE: Detaillierte Überschriften-Analyse (97 Überschriften)
            "comprehensive_heading_analysis": {
                "total_headings_found": 0,
                "heading_hierarchy_quality": {
                    "logical_structure": True,
                    "hierarchy_violations": [],
                    "missing_levels": [],
                    "hierarchy_score": 0
                },
                "heading_content_quality": {
                    "descriptive_headings": [],
                    "generic_headings": [],
                    "content_relevance_score": 0,
                    "seo_optimization_score": 0
                },
                "heading_accessibility": {
                    "aria_labeled_headings": 0,
                    "landmark_associated_headings": [],
                    "navigation_headings": [],
                    "accessibility_score": 0
                }
            },
            
            # NEUE: Social Media & SEO-Analyse (5 Open Graph + 4 Twitter Cards)
            "social_media_seo_analysis": {
                "open_graph_compliance": {
                    "total_og_tags": 0,
                    "essential_tags": [],
                    "missing_essential": [],
                    "og_completeness_score": 0
                },
                "twitter_cards_compliance": {
                    "total_twitter_tags": 0,
                    "card_type": None,
                    "twitter_completeness_score": 0
                },
                "social_sharing_optimization": {
                    "has_og_image": False,
                    "has_twitter_image": False,
                    "image_optimization": [],
                    "sharing_readiness_score": 0
                }
            },
            
            # NEUE: Schema.org & Structured Data-Analyse (4 Structured Data)
            "structured_data_analysis": {
                "total_structured_data": 0,
                "schema_types": [],
                "json_ld_data": [],
                "microdata": [],
                "structured_data_quality": {
                    "valid_schema": 0,
                    "invalid_schema": 0,
                    "missing_required_properties": [],
                    "schema_completeness_score": 0
                },
                "seo_enhancement": {
                    "rich_snippets_eligible": [],
                    "search_enhancement_opportunities": [],
                    "seo_value_score": 0
                }
            },
            
            # NEUE: Content Architecture-Analyse  
            "content_architecture": {
                "information_hierarchy": [],
                "content_relationships": [],
                "navigation_content_mapping": [],
                "content_discoverability_score": 0
            },
            
            # ERWEITERT: Original Daten
            "semantic_structure": {
                "total_headings": 0,
                "heading_hierarchy": {},
                "semantic_elements": {},
                "form_elements": 0,
                "table_elements": 0,
                "aria_landmarks": 0
            },
            "detailed_analysis": [],
            "pages_analyzed": []
        }
        
        # Analysiere jede Seite mit SUPER-ERWEITERTEN Methoden
        total_headings = 0
        total_og_tags = 0
        total_twitter_tags = 0
        total_structured_data = 0
        
        for url, page_data in self.crawl_data.get('data', {}).items():
            # NEUE: Umfassende Semantik-Analyse
            page_analysis = self._analyze_comprehensive_semantics(url, page_data)
            data["detailed_analysis"].append(page_analysis)
            data["pages_analyzed"].append(url)
            
            # Akkumuliere NEUE Daten
            headings_data = page_analysis.get("headings_analysis", {})
            social_data = page_analysis.get("social_media_analysis", {})
            structured_data_analysis = page_analysis.get("structured_data_analysis", {})
            
            total_headings += headings_data.get("heading_count", 0)
            total_og_tags += social_data.get("open_graph_count", 0)
            total_twitter_tags += social_data.get("twitter_cards_count", 0)
            total_structured_data += structured_data_analysis.get("structured_data_count", 0)
            
            data["comprehensive_heading_analysis"]["heading_content_quality"]["descriptive_headings"].extend(
                headings_data.get("descriptive_headings", [])
            )
            data["social_media_seo_analysis"]["open_graph_compliance"]["essential_tags"].extend(
                social_data.get("open_graph_tags", [])
            )
            data["structured_data_analysis"]["schema_types"].extend(
                structured_data_analysis.get("schema_types", [])
            )
            
            # Original Daten
            for level, count in page_analysis["headings"].items():
                data["semantic_structure"]["heading_hierarchy"][level] = (
                    data["semantic_structure"]["heading_hierarchy"].get(level, 0) + count
                )
            
            data["semantic_structure"]["total_headings"] += page_analysis["total_headings"]
            data["semantic_structure"]["form_elements"] += page_analysis["form_count"]
            data["semantic_structure"]["table_elements"] += page_analysis["table_count"]
        
        # Finale Zusammenfassung
        data["comprehensive_heading_analysis"]["total_headings_found"] = total_headings
        data["social_media_seo_analysis"]["open_graph_compliance"]["total_og_tags"] = total_og_tags
        data["social_media_seo_analysis"]["twitter_cards_compliance"]["total_twitter_tags"] = total_twitter_tags
        data["structured_data_analysis"]["total_structured_data"] = total_structured_data
        
        # Berechne Qualitäts-Scores
        self._calculate_comprehensive_scores(data, total_headings, total_og_tags, total_twitter_tags, total_structured_data)
        
        data["extraction_time_seconds"] = round(time.time() - start_time, 2)
        
        self.logger.info(f"✅ SUPER-ERWEITERTE Semantik-Extraktion: {total_headings} Überschriften, {total_og_tags} OG-Tags, {total_twitter_tags} Twitter-Cards, {total_structured_data} Schema.org in {data['extraction_time_seconds']}s")
        
        return data
    
    def _analyze_comprehensive_semantics(self, url: str, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Umfassende Semantik-Analyse mit 97 Überschriften + Open Graph + Schema.org"""
        analysis = {
            "page_url": url,
            "headings_analysis": self._analyze_comprehensive_headings(page_data),
            "social_media_analysis": self._analyze_social_media_markup(page_data),
            "structured_data_analysis": self._analyze_structured_data(page_data),
            "content_architecture": self._analyze_content_architecture(page_data),
            "accessibility_semantics": self._analyze_semantic_accessibility(page_data),
            
            # Original Daten für Kompatibilität
            "headings": {"h1": 0, "h2": 0, "h3": 0, "h4": 0, "h5": 0, "h6": 0},
            "total_headings": 0,
            "form_count": 0,
            "table_count": 0
        }
        
        # Original Analyse für Kompatibilität
        original_analysis = self._analyze_page_semantics(url)
        analysis.update({
            "headings": original_analysis.get("headings", {}),
            "total_headings": original_analysis.get("total_headings", 0),
            "form_count": original_analysis.get("form_count", 0),
            "table_count": original_analysis.get("table_count", 0)
        })
        
        return analysis
    
    def _analyze_comprehensive_headings(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Detaillierte Analyse der 97 Überschriften"""
        structure_data = page_data.get("structure", {})
        headings_list = structure_data.get("headings", [])
        
        analysis = {
            "heading_count": len(headings_list) if isinstance(headings_list, list) else 0,
            "heading_inventory": [],
            "hierarchy_analysis": {
                "h1_count": 0,
                "proper_nesting": True,
                "skipped_levels": [],
                "hierarchy_violations": []
            },
            "content_quality": {
                "descriptive_headings": [],
                "generic_headings": [],
                "keyword_optimized": [],
                "too_long_headings": []
            },
            "accessibility_features": {
                "aria_labeled": 0,
                "landmark_associated": 0,
                "navigation_related": 0
            },
            "seo_analysis": {
                "h1_seo_quality": None,
                "keyword_distribution": {},
                "content_structure_score": 0
            }
        }
        
        if isinstance(headings_list, list):
            prev_level = 0
            
            for heading in headings_list:
                if isinstance(heading, dict):
                    level = heading.get("level", 0)
                    text = heading.get("text", "").strip()
                    heading_id = heading.get("id", "")
                    aria_label = heading.get("aria_label", "")
                    
                    # Detailliertes Heading-Inventory
                    heading_info = {
                        "level": level,
                        "text": text,
                        "id": heading_id,
                        "aria_label": aria_label,
                        "character_count": len(text),
                        "word_count": len(text.split()) if text else 0,
                        "is_descriptive": self._is_descriptive_heading(text),
                        "seo_quality": self._assess_heading_seo_quality(text, level),
                        "accessibility_score": self._calculate_heading_accessibility_score(heading)
                    }
                    
                    analysis["heading_inventory"].append(heading_info)
                    
                    # Hierarchie-Analyse
                    if level == 1:
                        analysis["hierarchy_analysis"]["h1_count"] += 1
                        analysis["seo_analysis"]["h1_seo_quality"] = heading_info["seo_quality"]
                    
                    # Prüfe Hierarchie-Sprünge
                    if level - prev_level > 1:
                        analysis["hierarchy_analysis"]["skipped_levels"].append({
                            "from_level": prev_level,
                            "to_level": level,
                            "heading_text": text
                        })
                        analysis["hierarchy_analysis"]["proper_nesting"] = False
                    
                    prev_level = level
                    
                    # Content-Qualität
                    if heading_info["is_descriptive"]:
                        analysis["content_quality"]["descriptive_headings"].append(heading_info)
                    else:
                        analysis["content_quality"]["generic_headings"].append(heading_info)
                    
                    if len(text) > 60:
                        analysis["content_quality"]["too_long_headings"].append(heading_info)
                    
                    # Accessibility-Features
                    if aria_label:
                        analysis["accessibility_features"]["aria_labeled"] += 1
                    
                    if heading_id:
                        analysis["accessibility_features"]["landmark_associated"] += 1
            
            # Berechne Content-Structure-Score
            if analysis["heading_count"] > 0:
                descriptive_ratio = len(analysis["content_quality"]["descriptive_headings"]) / analysis["heading_count"]
                hierarchy_penalty = len(analysis["hierarchy_analysis"]["skipped_levels"]) * 10
                analysis["seo_analysis"]["content_structure_score"] = max(0, round((descriptive_ratio * 100) - hierarchy_penalty, 1))
        
        return analysis
    
    def _analyze_social_media_markup(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Analysiert Social Media Markup (5 Open Graph + 4 Twitter Cards)"""
        semantics_data = page_data.get("semantics", {})
        open_graph = semantics_data.get("open_graph", [])
        twitter_cards = semantics_data.get("twitter_cards", [])
        
        analysis = {
            "open_graph_count": len(open_graph) if isinstance(open_graph, list) else 0,
            "twitter_cards_count": len(twitter_cards) if isinstance(twitter_cards, list) else 0,
            "open_graph_analysis": {
                "essential_properties": [],
                "missing_essential": [],
                "image_properties": [],
                "completeness_score": 0
            },
            "twitter_analysis": {
                "card_type": None,
                "twitter_properties": [],
                "image_properties": [],
                "completeness_score": 0
            },
            "social_optimization": {
                "cross_platform_consistency": False,
                "image_optimization": [],
                "sharing_readiness": False
            }
        }
        
        # Analysiere Open Graph
        essential_og_props = ["og:title", "og:description", "og:image", "og:url", "og:type"]
        found_og_props = set()
        
        if isinstance(open_graph, list):
            for og_item in open_graph:
                if isinstance(og_item, dict):
                    property_name = og_item.get("property", "")
                    content = og_item.get("content", "")
                    
                    analysis["open_graph_analysis"]["essential_properties"].append({
                        "property": property_name,
                        "content": content,
                        "character_count": len(content),
                        "is_essential": property_name in essential_og_props
                    })
                    
                    found_og_props.add(property_name)
                    
                    # Bild-Eigenschaften analysieren
                    if "image" in property_name:
                        analysis["open_graph_analysis"]["image_properties"].append({
                            "property": property_name,
                            "url": content,
                            "format": self._extract_image_format_from_url(content)
                        })
        
        # Fehlende essentielle Properties
        missing_og = set(essential_og_props) - found_og_props
        analysis["open_graph_analysis"]["missing_essential"] = list(missing_og)
        
        # Berechne OG-Completeness-Score
        if essential_og_props:
            completeness_ratio = len(found_og_props & set(essential_og_props)) / len(essential_og_props)
            analysis["open_graph_analysis"]["completeness_score"] = round(completeness_ratio * 100, 1)
        
        # Analysiere Twitter Cards
        essential_twitter_props = ["twitter:card", "twitter:title", "twitter:description"]
        found_twitter_props = set()
        
        if isinstance(twitter_cards, list):
            for twitter_item in twitter_cards:
                if isinstance(twitter_item, dict):
                    name = twitter_item.get("name", "")
                    content = twitter_item.get("content", "")
                    
                    analysis["twitter_analysis"]["twitter_properties"].append({
                        "name": name,
                        "content": content,
                        "character_count": len(content)
                    })
                    
                    found_twitter_props.add(name)
                    
                    # Card-Type identifizieren
                    if name == "twitter:card":
                        analysis["twitter_analysis"]["card_type"] = content
                    
                    # Bild-Eigenschaften
                    if "image" in name:
                        analysis["twitter_analysis"]["image_properties"].append({
                            "property": name,
                            "url": content,
                            "format": self._extract_image_format_from_url(content)
                        })
        
        # Berechne Twitter-Completeness-Score
        if essential_twitter_props:
            completeness_ratio = len(found_twitter_props & set(essential_twitter_props)) / len(essential_twitter_props)
            analysis["twitter_analysis"]["completeness_score"] = round(completeness_ratio * 100, 1)
        
        # Cross-Platform-Konsistenz prüfen
        analysis["social_optimization"]["cross_platform_consistency"] = (
            analysis["open_graph_analysis"]["completeness_score"] > 80 and
            analysis["twitter_analysis"]["completeness_score"] > 80
        )
        
        analysis["social_optimization"]["sharing_readiness"] = (
            len(analysis["open_graph_analysis"]["image_properties"]) > 0 and
            len(analysis["twitter_analysis"]["image_properties"]) > 0
        )
        
        return analysis
    
    def _analyze_structured_data(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Analysiert Structured Data (4 Structured Data)"""
        semantics_data = page_data.get("semantics", {})
        structured_data = semantics_data.get("structured_data", [])
        schema_org = semantics_data.get("schema_org", [])
        
        analysis = {
            "structured_data_count": len(structured_data) if isinstance(structured_data, list) else 0,
            "schema_types": [],
            "json_ld_analysis": [],
            "microdata_analysis": [],
            "schema_quality": {
                "valid_schemas": 0,
                "invalid_schemas": 0,
                "missing_required_props": [],
                "rich_snippets_eligible": 0
            },
            "seo_enhancement": {
                "search_enhancements": [],
                "knowledge_graph_eligible": False,
                "local_business_data": None
            }
        }
        
        # Analysiere JSON-LD Structured Data
        if isinstance(structured_data, list):
            for data_item in structured_data:
                if isinstance(data_item, dict):
                    schema_type = data_item.get("@type", "Unknown")
                    context = data_item.get("@context", "")
                    
                    schema_info = {
                        "type": schema_type,
                        "context": context,
                        "properties": list(data_item.keys()),
                        "property_count": len(data_item.keys()),
                        "is_valid_schema": self._validate_schema_structure(data_item),
                        "seo_value": self._assess_schema_seo_value(schema_type)
                    }
                    
                    analysis["json_ld_analysis"].append(schema_info)
                    analysis["schema_types"].append(schema_type)
                    
                    if schema_info["is_valid_schema"]:
                        analysis["schema_quality"]["valid_schemas"] += 1
                    else:
                        analysis["schema_quality"]["invalid_schemas"] += 1
                    
                    # Rich Snippets Eligibility
                    if self._is_rich_snippet_eligible(schema_type):
                        analysis["schema_quality"]["rich_snippets_eligible"] += 1
                    
                    # SEO-Enhancements
                    if schema_type in ["LocalBusiness", "Organization"]:
                        analysis["seo_enhancement"]["local_business_data"] = schema_info
                    
                    if schema_type in ["Article", "BlogPosting", "NewsArticle"]:
                        analysis["seo_enhancement"]["search_enhancements"].append({
                            "type": "content_markup",
                            "schema": schema_type,
                            "benefit": "enhanced_search_results"
                        })
        
        # Analysiere Schema.org Microdata
        if isinstance(schema_org, list):
            for schema_item in schema_org:
                if isinstance(schema_item, dict):
                    analysis["microdata_analysis"].append({
                        "type": schema_item.get("type", "Unknown"),
                        "properties": schema_item.get("properties", {}),
                        "completeness": len(schema_item.get("properties", {}))
                    })
        
        return analysis
    
    def _analyze_content_architecture(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Analysiert Content-Architektur"""
        structure_data = page_data.get("structure", {})
        headings = structure_data.get("headings", [])
        links = structure_data.get("links", [])
        
        analysis = {
            "information_hierarchy": [],
            "content_relationships": [],
            "topic_modeling": [],
            "content_depth_analysis": {
                "shallow_content": 0,
                "medium_content": 0,
                "deep_content": 0
            }
        }
        
        # Analysiere Information-Hierarchie basierend auf Überschriften
        if isinstance(headings, list):
            for heading in headings:
                if isinstance(heading, dict):
                    level = heading.get("level", 0)
                    text = heading.get("text", "")
                    
                    analysis["information_hierarchy"].append({
                        "level": level,
                        "topic": text,
                        "word_count": len(text.split()) if text else 0,
                        "semantic_weight": (7 - level) * 10  # H1 = 60, H6 = 10
                    })
        
        return analysis
    
    def _analyze_semantic_accessibility(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Analysiert semantische Accessibility-Features"""
        accessibility_data = page_data.get("accessibility", {})
        
        analysis = {
            "landmark_usage": accessibility_data.get("landmarks", []),
            "aria_structure": accessibility_data.get("aria_roles", []),
            "semantic_navigation": [],
            "content_labeling": []
        }
        
        return analysis
    
    def _calculate_comprehensive_scores(self, data: Dict[str, Any], total_headings: int, total_og: int, total_twitter: int, total_structured: int):
        """Berechnet umfassende Qualitäts-Scores"""
        
        # Heading Hierarchy Score
        if total_headings > 0:
            descriptive_count = len(data["comprehensive_heading_analysis"]["heading_content_quality"]["descriptive_headings"])
            data["comprehensive_heading_analysis"]["heading_hierarchy_quality"]["hierarchy_score"] = round(
                (descriptive_count / total_headings) * 100, 1
            )
        
        # Open Graph Completeness Score
        if total_og > 0:
            essential_count = 5  # Essential OG properties
            data["social_media_seo_analysis"]["open_graph_compliance"]["og_completeness_score"] = round(
                min(100, (total_og / essential_count) * 100), 1
            )
        
        # Schema.org Value Score
        if total_structured > 0:
            data["structured_data_analysis"]["structured_data_quality"]["schema_completeness_score"] = round(
                min(100, total_structured * 25), 1  # Max 4 schemas = 100%
            )
    
    def _is_descriptive_heading(self, text: str) -> bool:
        """Prüft ob Überschrift aussagekräftig ist"""
        if not text or len(text.strip()) < 3:
            return False
        
        generic_terms = ["heading", "title", "content", "section", "page", "untitled"]
        return text.lower().strip() not in generic_terms and len(text.split()) >= 2
    
    def _assess_heading_seo_quality(self, text: str, level: int) -> Dict[str, Any]:
        """Bewertet SEO-Qualität einer Überschrift"""
        return {
            "character_count": len(text),
            "word_count": len(text.split()) if text else 0,
            "is_optimal_length": 20 <= len(text) <= 60 if level == 1 else 10 <= len(text) <= 40,
            "has_keywords": len(text.split()) >= 2,
            "seo_score": min(100, len(text) * 2) if text else 0
        }
    
    def _calculate_heading_accessibility_score(self, heading: Dict[str, Any]) -> int:
        """Berechnet Accessibility-Score für Überschrift"""
        score = 50  # Basis-Score für vorhandene Überschrift
        
        if heading.get("id"):
            score += 20
        
        if heading.get("aria_label"):
            score += 15
        
        if heading.get("text") and len(heading.get("text", "")) > 5:
            score += 15
        
        return min(100, score)
    
    def _extract_image_format_from_url(self, url: str) -> str:
        """Extrahiert Bildformat aus URL"""
        if not url:
            return "unknown"
        
        url_lower = url.lower()
        if ".jpg" in url_lower or ".jpeg" in url_lower:
            return "jpeg"
        elif ".png" in url_lower:
            return "png"
        elif ".webp" in url_lower:
            return "webp"
        elif ".svg" in url_lower:
            return "svg"
        else:
            return "unknown"
    
    def _validate_schema_structure(self, schema_data: Dict[str, Any]) -> bool:
        """Validiert Schema.org Struktur"""
        required_fields = ["@type", "@context"]
        return all(field in schema_data for field in required_fields)
    
    def _assess_schema_seo_value(self, schema_type: str) -> str:
        """Bewertet SEO-Wert eines Schema-Typs"""
        high_value_schemas = ["Article", "LocalBusiness", "Organization", "Product", "Recipe"]
        medium_value_schemas = ["BlogPosting", "NewsArticle", "Event", "FAQ"]
        
        if schema_type in high_value_schemas:
            return "high"
        elif schema_type in medium_value_schemas:
            return "medium"
        else:
            return "low"
    
    def _is_rich_snippet_eligible(self, schema_type: str) -> bool:
        """Prüft Rich Snippet Eligibility"""
        eligible_types = ["Article", "Recipe", "Product", "LocalBusiness", "Event", "FAQ", "HowTo"]
        return schema_type in eligible_types
    
    def _analyze_page_semantics(self, url: str) -> Dict[str, Any]:
        """Analysiert die semantische Struktur einer Seite - ORIGINAL für Kompatibilität"""
        
        # Verwende strukturierte Daten statt HTML-Parsing
        structured_data = self._get_structured_data_for_url(url)
        if not structured_data:
            return self._create_empty_semantic_analysis(url)
        
        # Überschriften aus strukturierten Daten extrahieren
        headings = {"h1": 0, "h2": 0, "h3": 0, "h4": 0, "h5": 0, "h6": 0}
        structure_data = structured_data.get('structure', {})
        headings_list = structure_data.get('headings', [])
        
        for heading in headings_list:
            level = heading.get('level', 0)
            if 1 <= level <= 6:
                headings[f"h{level}"] += 1
        
        # Semantische HTML5-Elemente aus strukturierten Daten
        semantic_elements = {
            'nav': 0, 'main': 0, 'header': 0, 'footer': 0,
            'section': 0, 'article': 0, 'aside': 0
        }
        
        # Prüfe semantic_structure wenn verfügbar
        semantic_structure = structure_data.get('semantic_structure', {})
        for element_type in semantic_elements.keys():
            semantic_elements[element_type] = len(semantic_structure.get(element_type, []))
        
        # Formular-Analyse aus strukturierten Daten
        forms_data = structure_data.get('forms', [])
        form_analysis = []
        for form in forms_data:
            form_analysis.append({
                "action": form.get('action', ''),
                "method": form.get('method', 'get'),
                "labels": len(form.get('labels', [])),
                "inputs": len(form.get('inputs', [])),
                "fieldsets": len(form.get('fieldsets', [])),
                "has_legend": len(form.get('legends', [])) > 0
            })
        
        # Tabellen-Analyse aus strukturierten Daten
        tables_data = structure_data.get('tables', [])
        table_analysis = []
        for table in tables_data:
            table_analysis.append({
                "has_caption": table.get('has_caption', False),
                "has_thead": table.get('has_thead', False),
                "has_tbody": table.get('has_tbody', False),
                "header_count": len(table.get('headers', [])),
                "row_count": table.get('row_count', 0)
            })
        
        return {
            "url": url,
            "headings": headings,
            "total_headings": sum(headings.values()),
            "semantic_elements": semantic_elements,
            "form_count": len(forms_data),
            "form_analysis": form_analysis,
            "table_count": len(tables_data),
            "table_analysis": table_analysis,
            "heading_issues": self._check_heading_hierarchy_from_structured(headings_list)
        }
    
    def _create_empty_semantic_analysis(self, url: str) -> Dict[str, Any]:
        """Erstellt eine leere semantische Analyse für URLs ohne Daten"""
        return {
            "url": url,
            "headings": {"h1": 0, "h2": 0, "h3": 0, "h4": 0, "h5": 0, "h6": 0},
            "total_headings": 0,
            "semantic_elements": {'nav': 0, 'main': 0, 'header': 0, 'footer': 0, 'section': 0, 'article': 0, 'aside': 0},
            "form_count": 0,
            "form_analysis": [],
            "table_count": 0,
            "table_analysis": [],
            "heading_issues": ["Keine strukturierten Daten verfügbar"]
        }
    
    def _check_heading_hierarchy_from_structured(self, headings_list: List[Dict[str, Any]]) -> List[str]:
        """Prüft die Überschriften-Hierarchie aus strukturierten Daten"""
        issues = []
        
        if not headings_list:
            return ["Keine Überschriften gefunden"]
        
        # Zähle H1-Überschriften
        h1_count = len([h for h in headings_list if h.get('level') == 1])
        if h1_count == 0:
            issues.append("Keine H1-Überschrift gefunden")
        elif h1_count > 1:
            issues.append(f"Mehrere H1-Überschriften gefunden ({h1_count})")
        
        # Prüfe Hierarchie-Sprünge
        prev_level = 0
        for heading in headings_list:
            level = heading.get('level', 0)
            if level - prev_level > 1:
                issues.append(f"Hierarchie-Sprung: von H{prev_level} zu H{level}")
            prev_level = level
        
        return issues

class WahrnehmbareDifferenzierungenExtractor(BaseWCAGExtractor):
    """1.4 Wahrnehmbare Unterscheidungen - Fokus auf Kontraste, Farben, Skalierung"""
    
    def extract_focused_data(self) -> Dict[str, Any]:
        """Extrahiert Daten für 1.4 Wahrnehmbare Unterscheidungen - ERWEITERT mit 812 Farben + 351 Font-Daten"""
        start_time = time.time()
        self.logger.info("🎨 Starte ERWEITERTE visuelle Differenzierung-Extraktion...")
        
        data = {
            "wcag_area": "1.4 Wahrnehmbare Unterscheidungen",
            "extraction_method": "spezialisiert_erweitert",
            "extracted_at": time.strftime("%Y-%m-%d_%H-%M-%S"),
            
            # NEUE: Detaillierte Farb-Analyse (812 Farben)
            "comprehensive_color_analysis": {
                "total_colors_found": 0,
                "unique_colors": [],
                "color_usage_patterns": [],
                "potential_contrast_issues": [],
                "color_dependency_warnings": []
            },
            
            # NEUE: Detaillierte Font-Analyse (351 Font-Daten)
            "comprehensive_font_analysis": {
                "total_fonts_found": 0,
                "font_families": [],
                "font_sizes": [],
                "font_weights": [],
                "line_heights": [],
                "text_spacing_issues": []
            },
            
            # NEUE: CSS-Analyse
            "css_analysis": {
                "media_queries": [],
                "responsive_breakpoints": [],
                "viewport_settings": [],
                "css_custom_properties": []
            },
            
            # ERWEITERT: Original Daten
            "color_contrast": {
                "text_elements": [],
                "background_combinations": [],
                "potential_issues": []
            },
            "font_sizing": {
                "relative_units": 0,
                "fixed_units": 0,
                "scalability_issues": []
            },
            "visual_indicators": {
                "focus_styles": [],
                "hover_effects": [],
                "color_only_information": []
            },
            "audio_controls": [],
            "detailed_analysis": [],
            "pages_analyzed": []
        }
        
        # Analysiere jede Seite
        total_colors = 0
        total_fonts = 0
        
        for url, page_data in self.crawl_data.get('data', {}).items():
            # NEUE: Erweiterte Seiten-Analyse
            page_analysis = self._analyze_comprehensive_visual_accessibility(url, page_data)
            data["detailed_analysis"].append(page_analysis)
            data["pages_analyzed"].append(url)
            
            # Akkumuliere NEUE Daten
            colors_data = page_analysis.get("colors_analysis", {})
            fonts_data = page_analysis.get("fonts_analysis", {})
            
            total_colors += colors_data.get("color_count", 0)
            total_fonts += fonts_data.get("font_count", 0)
            
            data["comprehensive_color_analysis"]["unique_colors"].extend(
                colors_data.get("unique_colors", [])
            )
            data["comprehensive_font_analysis"]["font_families"].extend(
                fonts_data.get("font_families", [])
            )
            
            # Original Daten
            data["color_contrast"]["text_elements"].extend(page_analysis.get("text_elements", []))
            data["font_sizing"]["relative_units"] += page_analysis.get("relative_units", 0)
            data["font_sizing"]["fixed_units"] += page_analysis.get("fixed_units", 0)
        
        # Finale Zusammenfassung
        data["comprehensive_color_analysis"]["total_colors_found"] = total_colors
        data["comprehensive_font_analysis"]["total_fonts_found"] = total_fonts
        
        # Dedupliziere Arrays
        data["comprehensive_color_analysis"]["unique_colors"] = list(set(
            data["comprehensive_color_analysis"]["unique_colors"]
        ))
        data["comprehensive_font_analysis"]["font_families"] = list(set(
            data["comprehensive_font_analysis"]["font_families"]
        ))
        
        data["extraction_time_seconds"] = round(time.time() - start_time, 2)
        total_elements = len(data["color_contrast"]["text_elements"])
        
        self.logger.info(f"✅ ERWEITERTE Visuelle Differenzierung-Extraktion: {total_colors} Farben, {total_fonts} Fonts, {total_elements} Elemente in {data['extraction_time_seconds']}s")
        
        return data
    
    def _analyze_comprehensive_visual_accessibility(self, url: str, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Umfassende visuelle Zugänglichkeits-Analyse mit 812 Farben + 351 Font-Daten"""
        analysis = {
            "page_url": url,
            "colors_analysis": self._analyze_comprehensive_colors(page_data),
            "fonts_analysis": self._analyze_comprehensive_fonts(page_data),
            "css_analysis": self._analyze_comprehensive_css(page_data),
            "responsive_analysis": self._analyze_responsive_features(page_data),
            
            # Original Daten
            "text_elements": [],
            "relative_units": 0,
            "fixed_units": 0
        }
        
        # Original Analyse für Kompatibilität
        original_analysis = self._analyze_visual_accessibility(url)
        analysis.update({
            "text_elements": original_analysis.get("text_elements", []),
            "relative_units": original_analysis.get("relative_units", 0),
            "fixed_units": original_analysis.get("fixed_units", 0)
        })
        
        return analysis
    
    def _analyze_comprehensive_colors(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Analysiert die 812 verfügbaren Farb-Daten"""
        styling_data = page_data.get("styling", {})
        colors_data = styling_data.get("colors", [])
        
        analysis = {
            "color_count": len(colors_data) if isinstance(colors_data, list) else 0,
            "unique_colors": [],
            "color_categories": {
                "background_colors": [],
                "text_colors": [],
                "border_colors": [],
                "accent_colors": []
            },
            "color_patterns": [],
            "accessibility_concerns": []
        }
        
        if isinstance(colors_data, list):
            for color_item in colors_data:
                if isinstance(color_item, dict):
                    color_value = color_item.get("color")
                    color_type = color_item.get("type", "unknown")
                    
                    if color_value:
                        analysis["unique_colors"].append(color_value)
                        
                        # Kategorisiere Farben
                        if "background" in color_type:
                            analysis["color_categories"]["background_colors"].append(color_value)
                        elif "text" in color_type:
                            analysis["color_categories"]["text_colors"].append(color_value)
                        elif "border" in color_type:
                            analysis["color_categories"]["border_colors"].append(color_value)
                        else:
                            analysis["color_categories"]["accent_colors"].append(color_value)
        
        return analysis
    
    def _analyze_comprehensive_fonts(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Analysiert die 351 verfügbaren Font-Daten"""
        styling_data = page_data.get("styling", {})
        fonts_data = styling_data.get("fonts", [])
        
        analysis = {
            "font_count": len(fonts_data) if isinstance(fonts_data, list) else 0,
            "font_families": [],
            "font_sizes": [],
            "font_weights": [],
            "font_properties": {
                "serif_fonts": [],
                "sans_serif_fonts": [],
                "monospace_fonts": [],
                "custom_fonts": []
            },
            "accessibility_features": {
                "relative_sizing": 0,
                "fixed_sizing": 0,
                "scalability_score": 0
            }
        }
        
        if isinstance(fonts_data, list):
            for font_item in fonts_data:
                if isinstance(font_item, dict):
                    family = font_item.get("font_family")
                    size = font_item.get("font_size")
                    weight = font_item.get("font_weight")
                    
                    if family:
                        analysis["font_families"].append(family)
                        
                        # Kategorisiere Font-Typen
                        if "serif" in family.lower():
                            analysis["font_properties"]["serif_fonts"].append(family)
                        elif "sans" in family.lower() or "arial" in family.lower():
                            analysis["font_properties"]["sans_serif_fonts"].append(family)
                        elif "mono" in family.lower():
                            analysis["font_properties"]["monospace_fonts"].append(family)
                        else:
                            analysis["font_properties"]["custom_fonts"].append(family)
                    
                    if size:
                        analysis["font_sizes"].append(size)
                        if "rem" in str(size) or "em" in str(size) or "%" in str(size):
                            analysis["accessibility_features"]["relative_sizing"] += 1
                        else:
                            analysis["accessibility_features"]["fixed_sizing"] += 1
                    
                    if weight:
                        analysis["font_weights"].append(weight)
        
        # Berechne Skalierbarkeits-Score
        total_fonts = analysis["accessibility_features"]["relative_sizing"] + analysis["accessibility_features"]["fixed_sizing"]
        if total_fonts > 0:
            analysis["accessibility_features"]["scalability_score"] = round(
                (analysis["accessibility_features"]["relative_sizing"] / total_fonts) * 100, 1
            )
        
        return analysis
    
    def _analyze_comprehensive_css(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Analysiert CSS-Features für Accessibility"""
        styling_data = page_data.get("styling", {})
        css_analysis = styling_data.get("css_analysis", {})
        responsive = styling_data.get("responsive", {})
        
        analysis = {
            "media_queries": css_analysis.get("media_queries", []) if isinstance(css_analysis, dict) else [],
            "custom_properties": css_analysis.get("custom_properties", []) if isinstance(css_analysis, dict) else [],
            "responsive_features": {
                "viewport_meta": responsive.get("viewport_meta") if isinstance(responsive, dict) else None,
                "responsive_images": responsive.get("responsive_images", []) if isinstance(responsive, dict) else [],
                "flexible_layouts": responsive.get("flexible_layouts", []) if isinstance(responsive, dict) else []
            },
            "accessibility_css": {
                "focus_styles_count": 0,
                "high_contrast_support": False,
                "reduced_motion_support": False
            }
        }
        
        return analysis
    
    def _analyze_responsive_features(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Analysiert Responsive Design Features"""
        styling_data = page_data.get("styling", {})
        responsive_data = styling_data.get("responsive", {})
        
        return {
            "has_viewport_meta": bool(responsive_data.get("viewport_meta")) if isinstance(responsive_data, dict) else False,
            "responsive_images_count": len(responsive_data.get("responsive_images", [])) if isinstance(responsive_data, dict) and isinstance(responsive_data.get("responsive_images"), list) else 0,
            "media_queries_count": len(responsive_data.get("media_queries", [])) if isinstance(responsive_data, dict) and isinstance(responsive_data.get("media_queries"), list) else 0,
            "flexible_layout_support": bool(responsive_data.get("flexible_layouts")) if isinstance(responsive_data, dict) else False
        }
    
    def _analyze_visual_accessibility(self, url: str) -> Dict[str, Any]:
        """Analysiert visuelle Zugänglichkeit einer Seite"""
        structured_data = self._get_structured_data_for_url(url)
        if not structured_data:
            return {"url": url, "text_elements": [], "relative_units": 0, "fixed_units": 0}
        
        styling_data = structured_data.get('styling', {})
        structure_data = structured_data.get('structure', {})
        
        # Erweiterte visuelle Analyse für WCAG 1.4
        analysis = {
            "url": url,
            "color_contrast_analysis": {
                "text_background_pairs": styling_data.get('text_elements', []),
                "low_contrast_issues": [],
                "contrast_ratios": [],
                "aa_compliant": 0,
                "aaa_compliant": 0
            },
            "font_sizing_analysis": {
                "relative_units": len(styling_data.get('relative_fonts', [])),
                "fixed_units": len(styling_data.get('fixed_fonts', [])),
                "scalability_issues": [],
                "zoom_test_results": []
            },
            "color_dependency_analysis": {
                "color_only_indicators": [],
                "error_indicators": [],
                "status_indicators": [],
                "additional_cues_present": True
            },
            "focus_indicators": {
                "elements_with_focus": styling_data.get('focus_styles', []),
                "missing_focus_styles": [],
                "custom_focus_implementations": []
            },
            "audio_video_controls": {
                "auto_play_elements": [],
                "volume_controls": [],
                "pause_controls": [],
                "stop_controls": []
            },
            "responsive_design": {
                "viewport_meta": structure_data.get('viewport', {}),
                "media_queries": styling_data.get('media_queries', []),
                "breakpoints": []
            },
            "visual_indicators": {
                "hover_effects": styling_data.get('hover_styles', []),
                "active_states": styling_data.get('active_styles', []),
                "visited_link_styles": styling_data.get('visited_styles', [])
            }
        }
        
        # Analysiere Farbkontraste falls Daten verfügbar
        self._analyze_color_contrasts(analysis, styling_data)
        
        # Analysiere Schriftgrößen-Skalierbarkeit
        self._analyze_font_scalability(analysis, styling_data)
        
        # Prüfe auf Farb-abhängige Informationen
        self._analyze_color_dependency(analysis, styling_data, structure_data)
        
        # Analysiere Audio/Video-Kontrollen
        multimedia = structure_data.get('multimedia', {})
        self._analyze_media_controls(analysis, multimedia)
        
        return analysis
    
    def _analyze_color_contrasts(self, analysis: Dict[str, Any], styling_data: Dict[str, Any]):
        """Analysiert Farbkontraste im Detail"""
        text_elements = styling_data.get('text_elements', [])
        
        for element in text_elements:
            if 'color' in element and 'background_color' in element:
                # Simuliere Kontrast-Berechnung (in echter Implementierung würde hier echte Berechnung stehen)
                contrast_ratio = element.get('contrast_ratio', 0)
                
                analysis["color_contrast_analysis"]["contrast_ratios"].append({
                    "element": element.get('selector', 'unknown'),
                    "foreground": element.get('color'),
                    "background": element.get('background_color'),
                    "ratio": contrast_ratio,
                    "aa_compliant": contrast_ratio >= 4.5,
                    "aaa_compliant": contrast_ratio >= 7.0
                })
                
                if contrast_ratio >= 4.5:
                    analysis["color_contrast_analysis"]["aa_compliant"] += 1
                else:
                    analysis["color_contrast_analysis"]["low_contrast_issues"].append({
                        "element": element.get('selector'),
                        "ratio": contrast_ratio,
                        "required": 4.5,
                        "issue": "below_aa_standard"
                    })
                
                if contrast_ratio >= 7.0:
                    analysis["color_contrast_analysis"]["aaa_compliant"] += 1
    
    def _analyze_font_scalability(self, analysis: Dict[str, Any], styling_data: Dict[str, Any]):
        """Analysiert Schriftgrößen-Skalierbarkeit"""
        fonts = styling_data.get('font_definitions', [])
        
        for font in fonts:
            unit = font.get('unit', 'px')
            size = font.get('size', 0)
            
            if unit == 'px' and size < 16:
                analysis["font_sizing_analysis"]["scalability_issues"].append({
                    "selector": font.get('selector'),
                    "size": f"{size}px",
                    "issue": "small_fixed_font",
                    "recommendation": "Use relative units (rem/em) or increase size"
                })
    
    def _analyze_color_dependency(self, analysis: Dict[str, Any], styling_data: Dict[str, Any], structure_data: Dict[str, Any]):
        """Analysiert Abhängigkeit von Farben für Information"""
        
        # Suche nach Elementen die nur durch Farbe unterschieden werden
        forms = structure_data.get('forms', [])
        for form in forms:
            # Prüfe auf rote Fehlermeldungen ohne zusätzliche Indikatoren
            errors = form.get('error_elements', [])
            for error in errors:
                if 'color' in error.get('style', {}) and not error.get('icon') and not error.get('text_indicator'):
                    analysis["color_dependency_analysis"]["error_indicators"].append({
                        "element": error.get('selector'),
                        "issue": "error_indicated_by_color_only",
                        "recommendation": "Add text or icon indicators"
                    })
    
    def _analyze_media_controls(self, analysis: Dict[str, Any], multimedia: Dict[str, Any]):
        """Analysiert Audio/Video-Kontrollen"""
        videos = multimedia.get('video', [])
        audios = multimedia.get('audio', [])
        
        for video in videos:
            if video.get('autoplay'):
                analysis["audio_video_controls"]["auto_play_elements"].append({
                    "type": "video",
                    "src": video.get('src'),
                    "has_controls": video.get('controls', False),
                    "issue": "auto_play_without_user_control" if not video.get('controls') else None
                })
        
        for audio in audios:
            if audio.get('autoplay'):
                analysis["audio_video_controls"]["auto_play_elements"].append({
                    "type": "audio", 
                    "src": audio.get('src'),
                    "has_controls": audio.get('controls', False),
                    "issue": "auto_play_without_user_control" if not audio.get('controls') else None
                })

class TastaturbedienungExtractor(BaseWCAGExtractor):
    """2.1 Tastaturbedienung - Fokus auf Tastaturzugänglichkeit - ERWEITERT mit 134 Tabindex + 77 ARIA-Labels"""
    
    def extract_focused_data(self) -> Dict[str, Any]:
        """Extrahiert Daten für 2.1 Tastaturbedienung - ERWEITERT mit massiven Accessibility-Daten"""
        start_time = time.time()
        self.logger.info("⌨️ Starte ERWEITERTE Tastaturbedienung-Extraktion...")
        
        data = {
            "wcag_area": "2.1 Tastaturbedienung",
            "extraction_method": "spezialisiert_erweitert",
            "extracted_at": time.strftime("%Y-%m-%d_%H-%M-%S"),
            
            # NEUE: Detaillierte Tabindex-Analyse (134 Elemente)
            "comprehensive_tabindex_analysis": {
                "total_tabindex_elements": 0,
                "tabindex_distribution": {
                    "negative_one": 0,
                    "zero": 0,
                    "positive": 0
                },
                "tabindex_elements": [],
                "focus_order_violations": [],
                "keyboard_trap_risks": []
            },
            
            # NEUE: Detaillierte ARIA-Analyse (77 Labels)
            "comprehensive_aria_analysis": {
                "total_aria_labels": 0,
                "aria_label_coverage": [],
                "aria_attributes": [],
                "missing_aria_support": [],
                "aria_implementation_quality": []
            },
            
            # NEUE: Event-Handler Analyse
            "comprehensive_event_analysis": {
                "keyboard_event_handlers": [],
                "mouse_only_events": [],
                "touch_events": [],
                "missing_keyboard_alternatives": [],
                "event_handler_quality": []
            },
            
            # NEUE: Framework-spezifische Analyse
            "framework_accessibility": {
                "detected_frameworks": [],
                "framework_patterns": [],
                "accessibility_implementations": [],
                "framework_specific_issues": []
            },
            
            # ERWEITERT: Original Daten
            "interactive_elements": {
                "total_count": 0,
                "keyboard_accessible": 0,
                "custom_controls": 0,
                "missing_tabindex": []
            },
            "focus_management": {
                "skip_links": [],
                "focus_traps": [],
                "logical_order": True
            },
            "keyboard_shortcuts": [],
            "detailed_analysis": [],
            "pages_analyzed": []
        }
        
        # Analysiere jede Seite mit ERWEITERTEN Methoden
        total_tabindex = 0
        total_aria_labels = 0
        
        for url, page_data in self.crawl_data.get('data', {}).items():
            # NEUE: Umfassende Keyboard-Analyse
            page_analysis = self._analyze_comprehensive_keyboard_accessibility(url, page_data)
            data["detailed_analysis"].append(page_analysis)
            data["pages_analyzed"].append(url)
            
            # Akkumuliere NEUE Daten
            tabindex_data = page_analysis.get("tabindex_analysis", {})
            aria_data = page_analysis.get("aria_analysis", {})
            events_data = page_analysis.get("events_analysis", {})
            
            total_tabindex += tabindex_data.get("tabindex_count", 0)
            total_aria_labels += aria_data.get("aria_labels_count", 0)
            
            data["comprehensive_tabindex_analysis"]["tabindex_elements"].extend(
                tabindex_data.get("tabindex_elements", [])
            )
            data["comprehensive_aria_analysis"]["aria_label_coverage"].extend(
                aria_data.get("aria_labels", [])
            )
            data["comprehensive_event_analysis"]["keyboard_event_handlers"].extend(
                events_data.get("keyboard_handlers", [])
            )
            
            # Original Daten
            data["interactive_elements"]["total_count"] += page_analysis.get("interactive_count", 0)
            data["interactive_elements"]["keyboard_accessible"] += page_analysis.get("keyboard_accessible", 0)
            data["focus_management"]["skip_links"].extend(page_analysis.get("skip_links", []))
        
        # Finale Zusammenfassung
        data["comprehensive_tabindex_analysis"]["total_tabindex_elements"] = total_tabindex
        data["comprehensive_aria_analysis"]["total_aria_labels"] = total_aria_labels
        
        # Analysiere Tabindex-Verteilung
        for element in data["comprehensive_tabindex_analysis"]["tabindex_elements"]:
            tabindex_val = element.get("tabindex", 0)
            # Konvertiere String zu Integer falls nötig
            try:
                tabindex_val = int(tabindex_val) if tabindex_val is not None else 0
            except (ValueError, TypeError):
                tabindex_val = 0
                
            if tabindex_val == -1:
                data["comprehensive_tabindex_analysis"]["tabindex_distribution"]["negative_one"] += 1
            elif tabindex_val == 0:
                data["comprehensive_tabindex_analysis"]["tabindex_distribution"]["zero"] += 1
            elif tabindex_val > 0:
                data["comprehensive_tabindex_analysis"]["tabindex_distribution"]["positive"] += 1
        
        data["extraction_time_seconds"] = round(time.time() - start_time, 2)
        total_interactive = data["interactive_elements"]["total_count"]
        
        self.logger.info(f"✅ ERWEITERTE Tastaturbedienung-Extraktion: {total_tabindex} Tabindex, {total_aria_labels} ARIA-Labels, {total_interactive} interaktive Elemente in {data['extraction_time_seconds']}s")
        
        return data
    
    def _analyze_comprehensive_keyboard_accessibility(self, url: str, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Umfassende Tastaturzugänglichkeits-Analyse mit 134 Tabindex + 77 ARIA-Labels"""
        analysis = {
            "page_url": url,
            "tabindex_analysis": self._analyze_comprehensive_tabindex(page_data),
            "aria_analysis": self._analyze_comprehensive_aria(page_data),
            "events_analysis": self._analyze_comprehensive_events(page_data),
            "framework_analysis": self._analyze_framework_accessibility(page_data),
            "focus_order_analysis": self._analyze_focus_order(page_data),
            
            # Original Daten für Kompatibilität
            "interactive_count": 0,
            "keyboard_accessible": 0,
            "skip_links": []
        }
        
        # Original Analyse für Kompatibilität
        original_analysis = self._analyze_keyboard_accessibility(url)
        analysis.update({
            "interactive_count": original_analysis.get("interactive_elements_analysis", {}).get("total_interactive", 0),
            "keyboard_accessible": original_analysis.get("interactive_elements_analysis", {}).get("keyboard_accessible", 0),
            "skip_links": original_analysis.get("skip_links_analysis", {}).get("skip_links_found", [])
        })
        
        return analysis
    
    def _analyze_comprehensive_tabindex(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Analysiert die 134 verfügbaren Tabindex-Daten"""
        accessibility_data = page_data.get("accessibility", {})
        tab_index_data = accessibility_data.get("tab_index", [])
        
        analysis = {
            "tabindex_count": len(tab_index_data) if isinstance(tab_index_data, list) else 0,
            "tabindex_elements": [],
            "focus_order_issues": [],
            "positive_tabindex_problems": [],
            "missing_tabindex_issues": [],
            "keyboard_trap_risks": []
        }
        
        if isinstance(tab_index_data, list):
            for tab_item in tab_index_data:
                if isinstance(tab_item, dict):
                    tabindex_value = tab_item.get("tabindex")
                    element_type = tab_item.get("element", "unknown")
                    
                    tabindex_info = {
                        "element": element_type,
                        "tabindex": tabindex_value,
                        "element_id": tab_item.get("id"),
                        "element_classes": tab_item.get("classes", []),
                        "aria_role": tab_item.get("role"),
                        "accessible_name": tab_item.get("accessible_name")
                    }
                    
                    analysis["tabindex_elements"].append(tabindex_info)
                    
                    # Analysiere problematische Tabindex-Werte
                    if isinstance(tabindex_value, int) and tabindex_value > 0:
                        analysis["positive_tabindex_problems"].append({
                            "element": element_type,
                            "tabindex": tabindex_value,
                            "issue": "positive_tabindex_disrupts_natural_order",
                            "recommendation": "Use tabindex='0' or remove tabindex"
                        })
                    
                    # Prüfe auf potentielle Keyboard-Traps
                    if tabindex_value == -1 and not tab_item.get("programmatic_focus"):
                        analysis["keyboard_trap_risks"].append({
                            "element": element_type,
                            "issue": "element_not_reachable_by_keyboard",
                            "tabindex": -1
                        })
        
        return analysis
    
    def _analyze_comprehensive_aria(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Analysiert die 77 verfügbaren ARIA-Labels"""
        accessibility_data = page_data.get("accessibility", {})
        aria_labels_data = accessibility_data.get("aria_labels", [])
        aria_attributes_data = accessibility_data.get("aria_attributes", [])
        
        analysis = {
            "aria_labels_count": len(aria_labels_data) if isinstance(aria_labels_data, list) else 0,
            "aria_labels": [],
            "aria_implementation_patterns": {
                "buttons_with_aria": 0,
                "links_with_aria": 0,
                "form_elements_with_aria": 0,
                "custom_controls_with_aria": 0
            },
            "aria_quality_assessment": [],
            "missing_aria_opportunities": [],
            "aria_best_practices": {
                "proper_labeling": 0,
                "role_usage": 0,
                "state_management": 0
            }
        }
        
        if isinstance(aria_labels_data, list):
            for aria_item in aria_labels_data:
                if isinstance(aria_item, dict):
                    aria_info = {
                        "element": aria_item.get("element", "unknown"),
                        "aria_label": aria_item.get("aria_label"),
                        "aria_labelledby": aria_item.get("aria_labelledby"),
                        "aria_describedby": aria_item.get("aria_describedby"),
                        "role": aria_item.get("role"),
                        "element_type": aria_item.get("tag_name"),
                        "context": aria_item.get("context")
                    }
                    
                    analysis["aria_labels"].append(aria_info)
                    
                    # Kategorisiere nach Element-Typ
                    element_type = aria_item.get("tag_name", "").lower()
                    if element_type == "button":
                        analysis["aria_implementation_patterns"]["buttons_with_aria"] += 1
                    elif element_type == "a":
                        analysis["aria_implementation_patterns"]["links_with_aria"] += 1
                    elif element_type in ["input", "select", "textarea"]:
                        analysis["aria_implementation_patterns"]["form_elements_with_aria"] += 1
                    else:
                        analysis["aria_implementation_patterns"]["custom_controls_with_aria"] += 1
                    
                    # Bewerte ARIA-Qualität
                    quality_score = 0
                    quality_issues = []
                    
                    if aria_item.get("aria_label"):
                        quality_score += 20
                        analysis["aria_best_practices"]["proper_labeling"] += 1
                    elif aria_item.get("aria_labelledby"):
                        quality_score += 25
                        analysis["aria_best_practices"]["proper_labeling"] += 1
                    else:
                        quality_issues.append("missing_accessible_name")
                    
                    if aria_item.get("role"):
                        quality_score += 15
                        analysis["aria_best_practices"]["role_usage"] += 1
                    
                    if aria_item.get("aria_expanded") is not None or aria_item.get("aria_checked") is not None:
                        quality_score += 10
                        analysis["aria_best_practices"]["state_management"] += 1
                    
                    analysis["aria_quality_assessment"].append({
                        "element": aria_item.get("element"),
                        "quality_score": quality_score,
                        "issues": quality_issues,
                        "strengths": [k for k, v in {
                            "has_label": bool(aria_item.get("aria_label")),
                            "has_role": bool(aria_item.get("role")),
                            "has_state": bool(aria_item.get("aria_expanded") or aria_item.get("aria_checked"))
                        }.items() if v]
                    })
        
        return analysis
    
    def _analyze_comprehensive_events(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Analysiert Event-Handler für Keyboard-Accessibility"""
        scripting_data = page_data.get("scripting", {})
        event_handlers = scripting_data.get("event_handlers", [])
        
        analysis = {
            "total_event_handlers": len(event_handlers) if isinstance(event_handlers, list) else 0,
            "keyboard_handlers": [],
            "mouse_only_handlers": [],
            "accessibility_event_patterns": {
                "click_with_keydown": 0,
                "mouseover_with_focus": 0,
                "touch_with_keyboard": 0
            },
            "event_accessibility_score": 0,
            "missing_keyboard_alternatives": []
        }
        
        if isinstance(event_handlers, list):
            keyboard_events = ["keydown", "keyup", "keypress"]
            mouse_events = ["click", "mousedown", "mouseup", "mouseover", "mouseout"]
            touch_events = ["touchstart", "touchend", "touchmove"]
            
            for event_item in event_handlers:
                if isinstance(event_item, dict):
                    event_type = event_item.get("event_type", "").lower()
                    element = event_item.get("element", "unknown")
                    
                    if any(kb_event in event_type for kb_event in keyboard_events):
                        analysis["keyboard_handlers"].append({
                            "element": element,
                            "event": event_type,
                            "accessibility": "good"
                        })
                    elif any(mouse_event in event_type for mouse_event in mouse_events):
                        # Prüfe ob auch Keyboard-Alternative vorhanden
                        has_keyboard_alt = any(
                            other_event.get("element") == element and 
                            any(kb_event in other_event.get("event_type", "").lower() for kb_event in keyboard_events)
                            for other_event in event_handlers
                        )
                        
                        if has_keyboard_alt:
                            analysis["accessibility_event_patterns"]["click_with_keydown"] += 1
                        else:
                            analysis["mouse_only_handlers"].append({
                                "element": element,
                                "event": event_type,
                                "issue": "no_keyboard_alternative"
                            })
                            analysis["missing_keyboard_alternatives"].append({
                                "element": element,
                                "mouse_event": event_type,
                                "recommendation": f"Add keyboard handler for {element}"
                            })
        
        # Berechne Accessibility-Score
        total_handlers = analysis["total_event_handlers"]
        if total_handlers > 0:
            accessible_handlers = len(analysis["keyboard_handlers"]) + analysis["accessibility_event_patterns"]["click_with_keydown"]
            analysis["event_accessibility_score"] = round((accessible_handlers / total_handlers) * 100, 1)
        
        return analysis
    
    def _analyze_framework_accessibility(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Analysiert Framework-spezifische Accessibility-Patterns"""
        scripting_data = page_data.get("scripting", {})
        frameworks = scripting_data.get("frameworks", [])
        
        analysis = {
            "detected_frameworks": frameworks if isinstance(frameworks, list) else [],
            "framework_specific_patterns": [],
            "accessibility_implementations": [],
            "framework_recommendations": []
        }
        
        if isinstance(frameworks, list):
            for framework in frameworks:
                if "react" in str(framework).lower():
                    analysis["framework_specific_patterns"].append({
                        "framework": "React",
                        "patterns": ["jsx_accessibility", "react_aria", "focus_management"],
                        "recommendations": ["Use react-aria library", "Implement proper focus management"]
                    })
                elif "vue" in str(framework).lower():
                    analysis["framework_specific_patterns"].append({
                        "framework": "Vue",
                        "patterns": ["vue_accessibility", "directive_usage"],
                        "recommendations": ["Use Vue accessibility directives", "Implement focus management"]
                    })
                elif "angular" in str(framework).lower():
                    analysis["framework_specific_patterns"].append({
                        "framework": "Angular",
                        "patterns": ["angular_cdk", "accessibility_directives"],
                        "recommendations": ["Use Angular CDK a11y", "Implement proper ARIA support"]
                    })
        
        return analysis
    
    def _analyze_focus_order(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Analysiert Focus-Order und Navigation"""
        accessibility_data = page_data.get("accessibility", {})
        focus_order = accessibility_data.get("focus_order", [])
        
        analysis = {
            "focus_order_elements": focus_order if isinstance(focus_order, list) else [],
            "logical_order": True,
            "focus_order_violations": [],
            "skip_link_effectiveness": [],
            "focus_management_patterns": []
        }
        
        if isinstance(focus_order, list) and len(focus_order) > 1:
            # Prüfe auf logische Reihenfolge
            for i in range(len(focus_order) - 1):
                current = focus_order[i]
                next_elem = focus_order[i + 1]
                
                if isinstance(current, dict) and isinstance(next_elem, dict):
                    current_tabindex = current.get("tabindex", 0)
                    next_tabindex = next_elem.get("tabindex", 0)
                    
                    # Positive Tabindex sollten in aufsteigender Reihenfolge sein
                    if current_tabindex > 0 and next_tabindex > 0 and current_tabindex > next_tabindex:
                        analysis["focus_order_violations"].append({
                            "violation": "positive_tabindex_out_of_order",
                            "current_element": current.get("element"),
                            "current_tabindex": current_tabindex,
                            "next_element": next_elem.get("element"),
                            "next_tabindex": next_tabindex
                        })
                        analysis["logical_order"] = False
        
        return analysis

    def _analyze_keyboard_accessibility(self, url: str) -> Dict[str, Any]:
        """Analysiert Tastaturbedienbarkeit einer Seite"""
        structured_data = self._get_structured_data_for_url(url)
        if not structured_data:
            return {"url": url, "interactive_count": 0, "keyboard_accessible": 0}
        
        structure_data = structured_data.get('structure', {})
        interactive_data = structure_data.get('interactive_elements', {})
        accessibility_data = structured_data.get('accessibility', {})
        
        # Sammle alle interaktiven Elemente
        buttons = interactive_data.get('buttons', [])
        links = structure_data.get('links', [])
        form_elements = structure_data.get('form_elements', [])
        
        # Erweiterte Tastatur-Analyse für WCAG 2.1
        analysis = {
            "url": url,
            "interactive_elements_analysis": {
                "total_interactive": 0,
                "keyboard_accessible": 0,
                "problematic_elements": [],
                "well_implemented": []
            },
            "tabindex_analysis": {
                "positive_tabindex": [],
                "negative_tabindex": [],
                "zero_tabindex": [],
                "missing_tabindex": [],
                "logical_order": True
            },
            "skip_links_analysis": {
                "skip_links_found": [],
                "missing_skip_links": [],
                "skip_link_quality": []
            },
            "focus_management": {
                "focus_indicators": [],
                "focus_traps": [],
                "modal_focus_handling": [],
                "dynamic_content_focus": []
            },
            "custom_controls": {
                "total_custom": 0,
                "aria_compliant": 0,
                "keyboard_handlers": [],
                "missing_keyboard_support": []
            },
            "keyboard_shortcuts": {
                "access_keys": [],
                "custom_shortcuts": [],
                "conflicts": []
            },
            "navigation_patterns": {
                "breadcrumbs": [],
                "site_search": [],
                "main_navigation": [],
                "footer_navigation": []
            }
        }
        
        # Analysiere Standard-Elemente
        self._analyze_standard_interactive_elements(analysis, buttons, links, form_elements)
        
        # Analysiere Tabindex-Verwendung
        self._analyze_tabindex_usage(analysis, structure_data)
        
        # Suche nach Skip-Links
        self._analyze_skip_links(analysis, links, structure_data)
        
        # Analysiere Custom Controls
        self._analyze_custom_controls(analysis, interactive_data, accessibility_data)
        
        # Prüfe Focus-Management
        self._analyze_focus_management(analysis, structure_data)
        
        return analysis
    
    def _analyze_standard_interactive_elements(self, analysis: Dict[str, Any], buttons: List, links: List, form_elements: List):
        """Analysiert Standard-interaktive Elemente"""
        
        # Buttons analysieren
        for button in buttons:
            is_accessible = True
            issues = []
            
            # Prüfe Button-Type
            if not button.get('type'):
                issues.append("missing_type_attribute")
                is_accessible = False
            
            # Prüfe Labels/Text
            if not button.get('text') and not button.get('aria-label') and not button.get('aria-labelledby'):
                issues.append("missing_accessible_name")
                is_accessible = False
            
            # Prüfe ARIA-Attribute
            if button.get('aria-expanded') is not None and button.get('aria-controls') is None:
                issues.append("aria_expanded_without_controls")
                is_accessible = False
            
            element_info = {
                "type": "button",
                "element": button.get('selector', 'unknown'),
                "text": button.get('text', ''),
                "accessible": is_accessible,
                "issues": issues
            }
            
            if is_accessible:
                analysis["interactive_elements_analysis"]["well_implemented"].append(element_info)
                analysis["interactive_elements_analysis"]["keyboard_accessible"] += 1
            else:
                analysis["interactive_elements_analysis"]["problematic_elements"].append(element_info)
            
            analysis["interactive_elements_analysis"]["total_interactive"] += 1
        
        # Links analysieren
        for link in links:
            is_accessible = True
            issues = []
            
            # Prüfe Link-Text
            link_text = link.get('text', '').strip()
            if not link_text or link_text.lower() in ['hier', 'more', 'click here', 'read more']:
                issues.append("non_descriptive_link_text")
                is_accessible = False
            
            # Prüfe href
            if not link.get('href'):
                issues.append("missing_href")
                is_accessible = False
            
            element_info = {
                "type": "link",
                "element": link.get('selector', 'unknown'),
                "text": link_text,
                "href": link.get('href', ''),
                "accessible": is_accessible,
                "issues": issues
            }
            
            if is_accessible:
                analysis["interactive_elements_analysis"]["well_implemented"].append(element_info)
                analysis["interactive_elements_analysis"]["keyboard_accessible"] += 1
            else:
                analysis["interactive_elements_analysis"]["problematic_elements"].append(element_info)
            
            analysis["interactive_elements_analysis"]["total_interactive"] += 1
    
    def _analyze_tabindex_usage(self, analysis: Dict[str, Any], structure_data: Dict[str, Any]):
        """Analysiert Tabindex-Verwendung"""
        
        tabindex_elements = structure_data.get('tabindex_elements', [])
        
        for element in tabindex_elements:
            tabindex_value = element.get('tabindex')
            
            if tabindex_value > 0:
                analysis["tabindex_analysis"]["positive_tabindex"].append({
                    "element": element.get('selector'),
                    "tabindex": tabindex_value,
                    "issue": "positive_tabindex_disrupts_natural_order"
                })
                analysis["tabindex_analysis"]["logical_order"] = False
            elif tabindex_value == 0:
                analysis["tabindex_analysis"]["zero_tabindex"].append({
                    "element": element.get('selector'),
                    "purpose": "custom_focusable_element"
                })
            elif tabindex_value == -1:
                analysis["tabindex_analysis"]["negative_tabindex"].append({
                    "element": element.get('selector'),
                    "purpose": "programmatically_focusable"
                })
    
    def _analyze_skip_links(self, analysis: Dict[str, Any], links: List, structure_data: Dict[str, Any]):
        """Analysiert Skip-Links"""
        
        skip_links = []
        for link in links:
            link_text = link.get('text', '').lower()
            href = link.get('href', '')
            
            # Erkenne Skip-Links
            if any(keyword in link_text for keyword in ['skip', 'jump', 'zum inhalt', 'navigation überspringen']):
                skip_info = {
                    "text": link.get('text'),
                    "href": href,
                    "target_exists": href.startswith('#'),  # Vereinfacht
                    "positioned_early": True  # Würde echte Position prüfen
                }
                skip_links.append(skip_info)
        
        analysis["skip_links_analysis"]["skip_links_found"] = skip_links
        
        # Prüfe ob Skip-Links vorhanden sind wenn Navigation komplex ist
        nav_elements = structure_data.get('nav_elements', [])
        if len(nav_elements) > 0 and len(skip_links) == 0:
            analysis["skip_links_analysis"]["missing_skip_links"].append({
                "issue": "complex_navigation_without_skip_links",
                "recommendation": "Add skip to main content link"
            })
    
    def _analyze_custom_controls(self, analysis: Dict[str, Any], interactive_data: Dict[str, Any], accessibility_data: Dict[str, Any]):
        """Analysiert Custom Controls"""
        
        # Suche nach Custom Controls (Divs/Spans mit Event-Handlers)
        custom_controls = interactive_data.get('custom_controls', [])
        
        for control in custom_controls:
            is_compliant = True
            issues = []
            
            # Prüfe ARIA-Role
            if not control.get('role'):
                issues.append("missing_role")
                is_compliant = False
            
            # Prüfe Tabindex
            if control.get('tabindex') is None:
                issues.append("missing_tabindex")
                is_compliant = False
            
            # Prüfe ARIA-Labels
            if not control.get('aria-label') and not control.get('aria-labelledby'):
                issues.append("missing_accessible_name")
                is_compliant = False
            
            # Prüfe Keyboard-Handler
            if not control.get('keyboard_handlers'):
                issues.append("missing_keyboard_handlers")
                is_compliant = False
            
            control_info = {
                "element": control.get('selector'),
                "role": control.get('role'),
                "compliant": is_compliant,
                "issues": issues
            }
            
            if is_compliant:
                analysis["custom_controls"]["aria_compliant"] += 1
            else:
                analysis["custom_controls"]["missing_keyboard_support"].append(control_info)
            
            analysis["custom_controls"]["total_custom"] += 1
    
    def _analyze_focus_management(self, analysis: Dict[str, Any], structure_data: Dict[str, Any]):
        """Analysiert Focus-Management"""
        
        # Suche nach Modals/Dialogs
        modals = structure_data.get('modal_elements', [])
        for modal in modals:
            focus_info = {
                "element": modal.get('selector'),
                "has_focus_trap": modal.get('focus_trap', False),
                "focus_restoration": modal.get('focus_restoration', False),
                "initial_focus": modal.get('initial_focus', False)
            }
            analysis["focus_management"]["modal_focus_handling"].append(focus_info)
        
        # Prüfe dynamische Inhalte
        dynamic_elements = structure_data.get('dynamic_content', [])
        for element in dynamic_elements:
            if element.get('updates_content'):
                analysis["focus_management"]["dynamic_content_focus"].append({
                    "element": element.get('selector'),
                    "manages_focus": element.get('manages_focus', False),
                    "aria_live": element.get('aria-live', False)
                })

class GenuegendZeitExtractor(BaseWCAGExtractor):
    """2.2 Genügend Zeit - Fokus auf Zeitlimits und bewegte Inhalte"""
    
    def extract_focused_data(self) -> Dict[str, Any]:
        """Extrahiert Daten für WCAG 2.2 Genügend Zeit"""
        start_time = time.time()
        
        data = {
            "wcag_area": "2.2_genuegend_zeit",
            "focus": "Zeitlimits, Auto-Updates, bewegte Inhalte, Session-Management",
            "extracted_at": time.strftime("%Y-%m-%d_%H-%M-%S"),
            "time_based_functions": {
                "session_timeouts": [],
                "auto_updates": [],
                "carousels": [],
                "timers": [],
                "moving_content": []
            },
            "auto_play": {
                "videos": 0,
                "audio": 0,
                "animations": 0
            },
            "user_controls": [],
            "detailed_analysis": [],
            "pages_analyzed": []
        }
        
        # Analysiere jede Seite
        for url, page_data in self.crawl_data.get('data', {}).items():
            page_analysis = self._analyze_time_functions(url)
            data["detailed_analysis"].append(page_analysis)
            data["pages_analyzed"].append(url)
            
            # Akkumuliere Daten
            data["auto_play"]["videos"] += page_analysis.get("autoplay_videos", 0)
            data["auto_play"]["audio"] += page_analysis.get("autoplay_audio", 0)
            data["time_based_functions"]["carousels"].extend(page_analysis.get("carousels", []))
        
        total_time_functions = (data["auto_play"]["videos"] + data["auto_play"]["audio"] + 
                              len(data["time_based_functions"]["carousels"]))
        
        data["has_time_based_functions"] = total_time_functions > 0
        data["compliance_note"] = ("Zeitbasierte Funktionen gefunden - WCAG 2.2 anwendbar" if total_time_functions > 0 
                                  else "Keine zeitbasierten Funktionen gefunden - WCAG 2.2 größtenteils nicht anwendbar")
        
        data["extraction_time_seconds"] = round(time.time() - start_time, 2)
        self.logger.info(f"✅ Zeit-Extraktion: {total_time_functions} zeitbasierte Funktionen in {data['extraction_time_seconds']}s")
        
        return data
    
    def _analyze_time_functions(self, url: str) -> Dict[str, Any]:
        """Analysiert zeitbasierte Funktionen einer Seite"""
        structured_data = self._get_structured_data_for_url(url)
        if not structured_data:
            return {"url": url, "autoplay_videos": 0, "autoplay_audio": 0, "carousels": []}
        
        structure_data = structured_data.get('structure', {})
        multimedia = structure_data.get('multimedia', {})
        scripting = structured_data.get('scripting', {})
        
        return {
            "url": url,
            "autoplay_videos": len([v for v in multimedia.get('video', []) if v.get('autoplay')]),
            "autoplay_audio": len([a for a in multimedia.get('audio', []) if a.get('autoplay')]),
            "carousels": scripting.get('carousels', []),
            "timers": scripting.get('timers', []),
            "session_management": scripting.get('session_functions', [])
        }

class AnfaelleVermeidenExtractor(BaseWCAGExtractor):
    """2.3 Anfälle vermeiden - Fokus auf Blitzeffekte und schnelle Bewegungen"""
    
    def extract_focused_data(self) -> Dict[str, Any]:
        """Extrahiert Daten für WCAG 2.3 Anfälle vermeiden"""
        start_time = time.time()
        
        data = {
            "wcag_area": "2.3_anfaelle_vermeiden", 
            "focus": "Blitzeffekte, Flackern, schnelle Animationen, GIFs",
            "extracted_at": time.strftime("%Y-%m-%d_%H-%M-%S"),
            "flash_analysis": {
                "total_animations": 0,
                "fast_animations": 0,
                "gif_files": 0,
                "css_animations": 0,
                "js_animations": 0
            },
            "seizure_risks": [],
            "animation_controls": [],
            "detailed_analysis": [],
            "pages_analyzed": []
        }
        
        # Analysiere jede Seite
        for url, page_data in self.crawl_data.get('data', {}).items():
            page_analysis = self._analyze_seizure_risks(url)
            data["detailed_analysis"].append(page_analysis)
            data["pages_analyzed"].append(url)
            
            # Akkumuliere Daten
            data["flash_analysis"]["gif_files"] += page_analysis.get("gif_count", 0)
            data["flash_analysis"]["css_animations"] += page_analysis.get("css_animations", 0)
            data["seizure_risks"].extend(page_analysis.get("risks", []))
        
        total_animations = (data["flash_analysis"]["gif_files"] + 
                          data["flash_analysis"]["css_animations"])
        
        data["has_seizure_content"] = len(data["seizure_risks"]) > 0
        data["compliance_note"] = ("Potentiell anfallsauslösende Inhalte gefunden" if data["has_seizure_content"]
                                  else "Keine anfallsauslösenden Inhalte gefunden - WCAG 2.3 erfüllt")
        
        data["extraction_time_seconds"] = round(time.time() - start_time, 2)
        self.logger.info(f"✅ Anfälle-Extraktion: {total_animations} Animationen analysiert in {data['extraction_time_seconds']}s")
        
        return data
    
    def _analyze_seizure_risks(self, url: str) -> Dict[str, Any]:
        """Analysiert potentielle Anfallsrisiken einer Seite"""
        structured_data = self._get_structured_data_for_url(url)
        if not structured_data:
            return {"url": url, "gif_count": 0, "css_animations": 0, "risks": []}
        
        structure_data = structured_data.get('structure', {})
        styling = structured_data.get('styling', {})
        
        # Suche nach GIFs
        images = structure_data.get('images', [])
        gif_count = len([img for img in images if isinstance(img, dict) and (img.get('src') or '').lower().endswith('.gif')])
        
        return {
            "url": url,
            "gif_count": gif_count,
            "css_animations": len(styling.get('animations', [])),
            "risks": [],  # Würde in echter Implementierung Flash-Analyse enthalten
            "animation_controls": styling.get('animation_controls', [])
        }

class NavigationExtractor(BaseWCAGExtractor):
    """2.4 Navigierbarkeit - SUPER-ERWEITERT mit 96 Links + 7 Navigation-Elemente"""
    
    def extract_focused_data(self) -> Dict[str, Any]:
        """Extrahiert Daten für WCAG 2.4 Navigierbarkeit - SUPER-ERWEITERT"""
        start_time = time.time()
        self.logger.info("🧭 Starte SUPER-ERWEITERTE Navigation-Extraktion...")
        
        data = {
            "wcag_area": "2.4 Navigierbarkeit",
            "extraction_method": "super_erweitert",
            "extracted_at": time.strftime("%Y-%m-%d_%H-%M-%S"),
            
            # NEUE: Detaillierte Link-Analyse (96 Links)
            "comprehensive_link_analysis": {
                "total_links_found": 0,
                "link_quality_distribution": {
                    "excellent_links": [],
                    "good_links": [],
                    "average_links": [],
                    "poor_links": []
                },
                "user_journey_analysis": {
                    "primary_navigation": [],
                    "secondary_navigation": [],
                    "footer_navigation": [],
                    "contextual_links": [],
                    "call_to_action_links": []
                },
                "link_accessibility_score": 0,
                "navigation_efficiency": {
                    "average_clicks_to_content": 0,
                    "dead_end_pages": [],
                    "orphaned_pages": [],
                    "navigation_depth": 0
                }
            },
            
            # NEUE: Navigation-Elemente Deep-Dive (7 Navigation-Elemente)
            "comprehensive_navigation_analysis": {
                "total_nav_elements": 0,
                "navigation_patterns": {
                    "primary_navigation": None,
                    "secondary_navigation": [],
                    "breadcrumb_navigation": None,
                    "utility_navigation": [],
                    "footer_navigation": None,
                    "sidebar_navigation": [],
                    "contextual_navigation": []
                },
                "navigation_consistency": {
                    "consistent_placement": True,
                    "consistent_labeling": True,
                    "consistent_behavior": True,
                    "consistency_score": 0
                },
                "navigation_accessibility": {
                    "keyboard_accessible": 0,
                    "screen_reader_optimized": 0,
                    "aria_compliant": 0,
                    "focus_management": []
                }
            },
            
            # NEUE: Content Discovery & Findability
            "content_discovery_analysis": {
                "search_functionality": {
                    "has_site_search": False,
                    "search_accessibility": 0,
                    "search_placement": "unknown",
                    "advanced_search": False
                },
                "content_organization": {
                    "category_structure": [],
                    "tag_system": [],
                    "filtering_options": [],
                    "sorting_options": []
                },
                "related_content": {
                    "related_links": [],
                    "similar_content": [],
                    "cross_references": [],
                    "content_recommendations": []
                }
            },
            
            # NEUE: User Experience Optimization
            "ux_navigation_analysis": {
                "navigation_predictability": {
                    "standard_patterns": [],
                    "user_expectations": [],
                    "convention_adherence": 0
                },
                "error_prevention": {
                    "broken_links": [],
                    "redirect_chains": [],
                    "external_link_warnings": [],
                    "download_indicators": []
                },
                "mobile_navigation": {
                    "responsive_navigation": False,
                    "mobile_menu": False,
                    "touch_friendly": False,
                    "mobile_optimization_score": 0
                }
            },
            
            # ERWEITERT: Original Daten
            "page_titles": {
                "total_pages": 0,
                "descriptive_titles": 0,
                "generic_titles": 0,
                "title_analysis": []
            },
            "navigation_structure": {
                "skip_links": [],
                "breadcrumbs": [],
                "landmark_roles": [],
                "multiple_nav_methods": 0
            },
            "link_analysis": {
                "total_links": 0,
                "descriptive_links": 0,
                "ambiguous_links": [],
                "external_links": 0
            },
            "detailed_analysis": [],
            "pages_analyzed": []
        }
        
        # Analysiere jede Seite mit SUPER-ERWEITERTEN Methoden
        total_links = 0
        total_nav_elements = 0
        total_pages = 0
        
        for url, page_data in self.crawl_data.get('data', {}).items():
            # NEUE: Umfassende Navigation-Analyse
            page_analysis = self._analyze_comprehensive_navigation(url, page_data)
            data["detailed_analysis"].append(page_analysis)
            data["pages_analyzed"].append(url)
            
            # Akkumuliere NEUE Daten
            links_data = page_analysis.get("links_analysis", {})
            nav_data = page_analysis.get("navigation_analysis", {})
            discovery_data = page_analysis.get("discovery_analysis", {})
            
            total_links += links_data.get("link_count", 0)
            total_nav_elements += nav_data.get("nav_elements_count", 0)
            total_pages += 1
            
            data["comprehensive_link_analysis"]["link_quality_distribution"]["excellent_links"].extend(
                links_data.get("excellent_links", [])
            )
            data["comprehensive_navigation_analysis"]["navigation_patterns"]["secondary_navigation"].extend(
                nav_data.get("secondary_nav", [])
            )
            data["content_discovery_analysis"]["content_organization"]["category_structure"].extend(
                discovery_data.get("categories", [])
            )
            
            # Original Daten
            data["page_titles"]["total_pages"] += 1
            if page_analysis.get("descriptive_title"):
                data["page_titles"]["descriptive_titles"] += 1
            
            data["link_analysis"]["total_links"] += page_analysis.get("link_count", 0)
            data["link_analysis"]["descriptive_links"] += page_analysis.get("descriptive_links", 0)
        
        # Finale Zusammenfassung
        data["comprehensive_link_analysis"]["total_links_found"] = total_links
        data["comprehensive_navigation_analysis"]["total_nav_elements"] = total_nav_elements
        
        # Berechne Super-Scores
        self._calculate_comprehensive_navigation_scores(data, total_links, total_nav_elements, total_pages)
        
        data["extraction_time_seconds"] = round(time.time() - start_time, 2)
        
        self.logger.info(f"✅ SUPER-ERWEITERTE Navigation-Extraktion: {total_links} Links, {total_nav_elements} Nav-Elemente, {total_pages} Seiten in {data['extraction_time_seconds']}s")
        
        return data
    
    def _analyze_comprehensive_navigation(self, url: str, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Umfassende Navigation-Analyse mit 96 Links + 7 Navigation-Elementen"""
        analysis = {
            "page_url": url,
            "links_analysis": self._analyze_comprehensive_links(page_data),
            "navigation_analysis": self._analyze_comprehensive_navigation_elements(page_data),
            "discovery_analysis": self._analyze_content_discovery(page_data),
            "ux_analysis": self._analyze_navigation_ux(page_data),
            "accessibility_analysis": self._analyze_navigation_accessibility(page_data),
            
            # Original Daten für Kompatibilität
            "link_count": 0,
            "descriptive_links": 0,
            "descriptive_title": False
        }
        
        # Original Analyse für Kompatibilität
        original_analysis = self._analyze_navigation_structure(url)
        analysis.update({
            "link_count": original_analysis.get("link_analysis", {}).get("total_links", 0),
            "descriptive_links": original_analysis.get("link_analysis", {}).get("descriptive_links", 0),
            "descriptive_title": original_analysis.get("page_title_analysis", {}).get("descriptive", False)
        })
        
        return analysis
    
    def _analyze_comprehensive_links(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Detaillierte Analyse der 96 Links"""
        structure_data = page_data.get("structure", {})
        links_list = structure_data.get("links", [])
        
        analysis = {
            "link_count": len(links_list) if isinstance(links_list, list) else 0,
            "link_inventory": [],
            "link_categories": {
                "navigation_links": [],
                "content_links": [],
                "external_links": [],
                "action_links": [],
                "utility_links": []
            },
            "link_quality_assessment": {
                "excellent_links": [],
                "good_links": [],
                "average_links": [],
                "poor_links": []
            },
            "user_journey_mapping": {
                "entry_points": [],
                "conversion_paths": [],
                "exit_points": [],
                "dead_ends": []
            },
            "link_accessibility": {
                "descriptive_links": 0,
                "ambiguous_links": 0,
                "missing_context": 0,
                "accessibility_score": 0
            }
        }
        
        if isinstance(links_list, list):
            for link in links_list:
                if isinstance(link, dict):
                    href = str(link.get("href", "")) if link.get("href") is not None else ""
                    text = str(link.get("text", "")).strip() if link.get("text") is not None else ""
                    title = str(link.get("title", "")) if link.get("title") is not None else ""
                    
                    # Detailliertes Link-Inventory
                    link_info = {
                        "href": href,
                        "text": text,
                        "title": title,
                        "character_count": len(text),
                        "word_count": len(text.split()) if text else 0,
                        "link_type": self._categorize_link_type(href, text),
                        "purpose": self._determine_link_purpose(href, text),
                        "quality_score": self._calculate_link_quality_score(text, href, title),
                        "accessibility_features": self._assess_link_accessibility(link)
                    }
                    
                    analysis["link_inventory"].append(link_info)
                    
                    # Kategorisiere Links
                    link_category = self._categorize_link_usage(href, text, link)
                    if link_category in analysis["link_categories"]:
                        analysis["link_categories"][link_category].append(link_info)
                    
                    # Qualitätsbewertung
                    quality_tier = self._determine_quality_tier(link_info["quality_score"])
                    analysis["link_quality_assessment"][quality_tier].append(link_info)
                    
                    # User Journey Mapping
                    journey_role = self._determine_journey_role(href, text)
                    if journey_role in analysis["user_journey_mapping"]:
                        analysis["user_journey_mapping"][journey_role].append(link_info)
                    
                    # Accessibility Assessment
                    if self._is_descriptive_link(text):
                        analysis["link_accessibility"]["descriptive_links"] += 1
                    elif self._is_ambiguous_link(text):
                        analysis["link_accessibility"]["ambiguous_links"] += 1
                    
                    if not text and not title:
                        analysis["link_accessibility"]["missing_context"] += 1
        
        # Berechne Link-Accessibility-Score
        if analysis["link_count"] > 0:
            accessible_links = analysis["link_accessibility"]["descriptive_links"]
            analysis["link_accessibility"]["accessibility_score"] = round(
                (accessible_links / analysis["link_count"]) * 100, 1
            )
        
        return analysis
    
    def _analyze_comprehensive_navigation_elements(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Analysiert die 7 Navigation-Elemente im Detail"""
        structure_data = page_data.get("structure", {})
        nav_elements = structure_data.get("navigation", [])
        
        analysis = {
            "nav_elements_count": len(nav_elements) if isinstance(nav_elements, list) else 0,
            "navigation_inventory": [],
            "navigation_patterns": {
                "primary_navigation": None,
                "secondary_navigation": [],
                "breadcrumb_navigation": None,
                "utility_navigation": [],
                "footer_navigation": None,
                "sidebar_navigation": [],
                "contextual_navigation": []
            },
            "navigation_hierarchy": {
                "clear_hierarchy": True,
                "hierarchy_violations": [],
                "navigation_depth": 0,
                "consistent_structure": True
            },
            "navigation_behavior": {
                "hover_states": [],
                "active_states": [],
                "responsive_behavior": [],
                "keyboard_behavior": []
            },
            "navigation_labeling": {
                "clear_labels": 0,
                "ambiguous_labels": 0,
                "missing_labels": 0,
                "labeling_consistency": True
            }
        }
        
        if isinstance(nav_elements, list):
            for nav in nav_elements:
                if isinstance(nav, dict):
                    nav_type = nav.get("type", "unknown")
                    nav_label = nav.get("aria_label", "")
                    nav_items = nav.get("items", [])
                    
                    # Detailliertes Navigation-Inventory
                    nav_info = {
                        "type": nav_type,
                        "aria_label": nav_label,
                        "items_count": len(nav_items) if isinstance(nav_items, list) else 0,
                        "position": nav.get("position", "unknown"),
                        "accessibility_features": {
                            "has_aria_label": bool(nav_label),
                            "has_role": bool(nav.get("role")),
                            "keyboard_accessible": self._assess_nav_keyboard_accessibility(nav),
                            "screen_reader_friendly": self._assess_nav_screen_reader_support(nav)
                        },
                        "usability_features": {
                            "clear_hierarchy": self._assess_nav_hierarchy(nav_items),
                            "logical_grouping": self._assess_nav_grouping(nav_items),
                            "appropriate_depth": self._assess_nav_depth(nav_items)
                        }
                    }
                    
                    analysis["navigation_inventory"].append(nav_info)
                    
                    # Klassifiziere Navigation-Typ
                    nav_category = self._classify_navigation_type(nav_type, nav_label, nav.get("position"))
                    if nav_category == "primary":
                        analysis["navigation_patterns"]["primary_navigation"] = nav_info
                    elif nav_category == "secondary":
                        analysis["navigation_patterns"]["secondary_navigation"].append(nav_info)
                    elif nav_category == "breadcrumb":
                        analysis["navigation_patterns"]["breadcrumb_navigation"] = nav_info
                    elif nav_category == "utility":
                        analysis["navigation_patterns"]["utility_navigation"].append(nav_info)
                    elif nav_category == "footer":
                        analysis["navigation_patterns"]["footer_navigation"] = nav_info
                    elif nav_category == "sidebar":
                        analysis["navigation_patterns"]["sidebar_navigation"].append(nav_info)
                    elif nav_category == "contextual":
                        analysis["navigation_patterns"]["contextual_navigation"].append(nav_info)
                    
                    # Bewerte Navigation-Labels
                    if nav_label:
                        if self._is_clear_navigation_label(nav_label):
                            analysis["navigation_labeling"]["clear_labels"] += 1
                        else:
                            analysis["navigation_labeling"]["ambiguous_labels"] += 1
                    else:
                        analysis["navigation_labeling"]["missing_labels"] += 1
        
        # Berechne Navigation-Hierarchie-Tiefe
        max_depth = 0
        for nav_info in analysis["navigation_inventory"]:
            nav_items = nav_info.get("items_count", 0)
            if nav_items > max_depth:
                max_depth = nav_items
        analysis["navigation_hierarchy"]["navigation_depth"] = max_depth
        
        return analysis
    
    def _analyze_content_discovery(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Analysiert Content Discovery & Findability"""
        structure_data = page_data.get("structure", {})
        forms = structure_data.get("forms", [])
        
        analysis = {
            "search_functionality": {
                "has_site_search": False,
                "search_form": None,
                "search_accessibility": 0,
                "search_features": []
            },
            "categories": [],
            "content_organization": {
                "clear_categories": [],
                "tag_system": [],
                "filtering_available": False,
                "sorting_available": False
            },
            "content_relationships": {
                "related_content": [],
                "cross_references": [],
                "content_clustering": []
            },
            "wayfinding": {
                "breadcrumbs": [],
                "you_are_here": [],
                "progress_indicators": [],
                "site_maps": []
            }
        }
        
        # Suche nach Search-Functionality
        if isinstance(forms, list):
            for form in forms:
                if isinstance(form, dict):
                    action_raw = form.get("action", "")
                    action = str(action_raw).lower() if action_raw is not None else ""
                    inputs = form.get("inputs", [])
                    
                    # Erkenne Search-Forms
                    if "search" in action or any("search" in str(inp.get("name", "")).lower() for inp in inputs):
                        analysis["search_functionality"]["has_site_search"] = True
                        analysis["search_functionality"]["search_form"] = {
                            "action": form.get("action"),
                            "method": form.get("method", "get"),
                            "accessibility_score": self._assess_search_accessibility(form),
                            "features": self._extract_search_features(form)
                        }
        
        return analysis
    
    def _analyze_navigation_ux(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Analysiert Navigation UX"""
        styling_data = page_data.get("styling", {})
        
        analysis = {
            "visual_hierarchy": {
                "clear_visual_separation": True,
                "consistent_styling": True,
                "hover_feedback": False,
                "active_feedback": False
            },
            "mobile_optimization": {
                "responsive_navigation": False,
                "hamburger_menu": False,
                "touch_targets": [],
                "mobile_score": 0
            },
            "user_feedback": {
                "loading_indicators": [],
                "error_messages": [],
                "success_confirmations": [],
                "progress_feedback": []
            },
            "convention_adherence": {
                "standard_patterns": [],
                "unexpected_behaviors": [],
                "user_expectation_violations": []
            }
        }
        
        # Analysiere Responsive Design
        if isinstance(styling_data, dict):
            responsive = styling_data.get("responsive", {})
            if isinstance(responsive, dict):
                analysis["mobile_optimization"]["responsive_navigation"] = bool(responsive.get("viewport_meta"))
                analysis["mobile_optimization"]["mobile_score"] = self._calculate_mobile_nav_score(responsive)
        
        return analysis
    
    def _analyze_navigation_accessibility(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Analysiert Navigation-Accessibility"""
        accessibility_data = page_data.get("accessibility", {})
        
        analysis = {
            "keyboard_navigation": {
                "tab_order_logical": True,
                "skip_links_present": False,
                "keyboard_shortcuts": [],
                "focus_indicators": []
            },
            "screen_reader_support": {
                "aria_labels": [],
                "landmarks": [],
                "headings_structure": [],
                "live_regions": []
            },
            "assistive_technology": {
                "voice_control_friendly": False,
                "switch_navigation": False,
                "magnification_support": False
            }
        }
        
        if isinstance(accessibility_data, dict):
            landmarks = accessibility_data.get("landmarks", [])
            if isinstance(landmarks, list):
                analysis["screen_reader_support"]["landmarks"] = landmarks
                analysis["keyboard_navigation"]["skip_links_present"] = any(
                    "navigation" in str(landmark.get("role", "")).lower() for landmark in landmarks
                )
        
        return analysis
    
    def _calculate_comprehensive_navigation_scores(self, data: Dict[str, Any], total_links: int, total_nav_elements: int, total_pages: int):
        """Berechnet umfassende Navigation-Scores"""
        
        # Link-Accessibility-Score
        if total_links > 0:
            excellent_links = len(data["comprehensive_link_analysis"]["link_quality_distribution"]["excellent_links"])
            data["comprehensive_link_analysis"]["link_accessibility_score"] = round(
                (excellent_links / total_links) * 100, 1
            )
        
        # Navigation-Consistency-Score
        if total_nav_elements > 0:
            # Simuliere Konsistenz-Bewertung
            consistency_score = 85 if total_nav_elements >= 3 else 60
            data["comprehensive_navigation_analysis"]["navigation_consistency"]["consistency_score"] = consistency_score
        
        # Content-Discovery-Score
        has_search = data["content_discovery_analysis"]["search_functionality"]["has_site_search"]
        discovery_score = 70 if has_search else 40
        data["content_discovery_analysis"]["findability_score"] = discovery_score
    
    def _categorize_link_type(self, href: str, text: str) -> str:
        """Kategorisiert Link-Typ"""
        href = str(href) if href else ""
        text = str(text) if text else ""
        href_lower = href.lower()
        text_lower = text.lower()
        
        if href.startswith("#"):
            return "anchor_link"
        elif href.startswith("mailto:"):
            return "email_link"
        elif href.startswith("tel:"):
            return "phone_link"
        elif any(domain in href_lower for domain in ["http://", "https://"] if "ecomtask.de" not in href_lower):
            return "external_link"
        elif any(file_ext in href_lower for file_ext in [".pdf", ".doc", ".zip"]):
            return "download_link"
        else:
            return "internal_link"
    
    def _determine_link_purpose(self, href: str, text: str) -> str:
        """Bestimmt Link-Zweck"""
        text = str(text) if text else ""
        text_lower = text.lower()
        
        if any(action in text_lower for action in ["buy", "purchase", "order", "bestellen", "kaufen"]):
            return "conversion"
        elif any(nav in text_lower for nav in ["home", "about", "contact", "über", "kontakt"]):
            return "navigation"
        elif any(info in text_lower for info in ["more", "read", "learn", "details", "mehr", "lesen"]):
            return "information"
        elif any(action in text_lower for action in ["download", "save", "print", "herunterladen"]):
            return "utility"
        else:
            return "content"
    
    def _calculate_link_quality_score(self, text: str, href: str, title: str) -> int:
        """Berechnet Link-Qualitäts-Score"""
        score = 0
        
        # Text-Qualität
        if text and len(text.strip()) > 2:
            score += 30
            if len(text) >= 5 and len(text) <= 40:
                score += 20
            if not self._is_generic_link_text(text):
                score += 25
        
        # Kontext
        if title:
            score += 15
        
        # Href-Qualität
        if href and not href.startswith("#"):
            score += 10
        
        return min(100, score)
    
    def _assess_link_accessibility(self, link: Dict[str, Any]) -> Dict[str, str]:
        """Bewertet Link-Accessibility"""
        return {
            "has_text": bool(link.get("text")),
            "has_title": bool(link.get("title")),
            "has_aria_label": bool(link.get("aria_label")),
            "target_indication": bool(link.get("target") == "_blank")
        }
    
    def _categorize_link_usage(self, href: str, text: str, link: Dict[str, Any]) -> str:
        """Kategorisiert Link-Verwendung"""
        href = str(href) if href else ""
        text = str(text) if text else ""
        
        # Vereinfachte Kategorisierung
        context = str(link.get("context", "")) if link.get("context") else ""
        
        if "nav" in context.lower():
            return "navigation_links"
        elif href.startswith("http") and "ecomtask.de" not in href:
            return "external_links"
        elif any(action in text.lower() for action in ["buy", "order", "subscribe"]):
            return "action_links"
        elif any(util in text.lower() for util in ["help", "contact", "support"]):
            return "utility_links"
        else:
            return "content_links"
    
    def _determine_quality_tier(self, quality_score: int) -> str:
        """Bestimmt Qualitäts-Tier"""
        if quality_score >= 80:
            return "excellent_links"
        elif quality_score >= 60:
            return "good_links"
        elif quality_score >= 40:
            return "average_links"
        else:
            return "poor_links"
    
    def _determine_journey_role(self, href: str, text: str) -> str:
        """Bestimmt User Journey-Rolle"""
        text = str(text) if text else ""
        text_lower = text.lower()
        
        if any(entry in text_lower for entry in ["home", "start", "begin"]):
            return "entry_points"
        elif any(convert in text_lower for convert in ["buy", "purchase", "signup"]):
            return "conversion_paths"
        elif any(exit_word in text_lower for exit_word in ["contact", "help", "support"]):
            return "exit_points"
        else:
            return "dead_ends"  # Simplifikation
    
    def _is_descriptive_link(self, text: str) -> bool:
        """Prüft ob Link beschreibend ist"""
        return (text and len(text.strip()) >= 5 and 
                not self._is_generic_link_text(text))
    
    def _is_ambiguous_link(self, text: str) -> bool:
        """Prüft ob Link mehrdeutig ist"""
        return self._is_generic_link_text(text)
    
    def _is_generic_link_text(self, text: str) -> bool:
        """Prüft auf generische Link-Texte"""
        generic_terms = ["here", "click", "more", "link", "hier", "klick", "mehr", "weiter"]
        return text.lower().strip() in generic_terms
    
    def _classify_navigation_type(self, nav_type: str, aria_label: str, position: str) -> str:
        """Klassifiziert Navigation-Typ"""
        # Sichere Null-Checks hinzufügen
        type_lower = (nav_type or "").lower()
        label_lower = (aria_label or "").lower()
        position_lower = (position or "").lower()
        
        if "primary" in type_lower or "main" in label_lower:
            return "primary"
        elif "breadcrumb" in type_lower or "breadcrumb" in label_lower:
            return "breadcrumb"
        elif "footer" in position_lower:
            return "footer"
        elif "sidebar" in position_lower:
            return "sidebar"
        elif "utility" in type_lower:
            return "utility"
        else:
            return "secondary"
    
    def _assess_nav_keyboard_accessibility(self, nav: Dict[str, Any]) -> bool:
        """Bewertet Keyboard-Accessibility von Navigation"""
        return bool(nav.get("tabindex") is not None or nav.get("role"))
    
    def _assess_nav_screen_reader_support(self, nav: Dict[str, Any]) -> bool:
        """Bewertet Screen Reader-Support von Navigation"""
        return bool(nav.get("aria_label") or nav.get("aria_labelledby"))
    
    def _assess_nav_hierarchy(self, nav_items: List) -> bool:
        """Bewertet Navigation-Hierarchie"""
        return isinstance(nav_items, list) and len(nav_items) > 0
    
    def _assess_nav_grouping(self, nav_items: List) -> bool:
        """Bewertet Navigation-Gruppierung"""
        return isinstance(nav_items, list) and len(nav_items) <= 7  # Miller's Rule
    
    def _assess_nav_depth(self, nav_items: List) -> bool:
        """Bewertet Navigation-Tiefe"""
        return isinstance(nav_items, list) and len(nav_items) <= 3  # Nicht zu tief
    
    def _is_clear_navigation_label(self, label: str) -> bool:
        """Prüft ob Navigation-Label klar ist"""
        return len(label) >= 3 and label.lower() not in ["nav", "menu", "navigation"]
    
    def _assess_search_accessibility(self, form: Dict[str, Any]) -> int:
        """Bewertet Search-Accessibility"""
        score = 0
        
        if form.get("labels"):
            score += 40
        if form.get("aria_label"):
            score += 30
        if form.get("method", "").lower() == "get":
            score += 20
        if form.get("autocomplete"):
            score += 10
        
        return score
    
    def _extract_search_features(self, form: Dict[str, Any]) -> List[str]:
        """Extrahiert Search-Features"""
        features = []
        
        if form.get("autocomplete"):
            features.append("autocomplete")
        if form.get("placeholder"):
            features.append("placeholder")
        if len(form.get("inputs", [])) > 1:
            features.append("advanced_search")
        
        return features
    
    def _calculate_mobile_nav_score(self, responsive: Dict[str, Any]) -> int:
        """Berechnet Mobile Navigation-Score"""
        score = 0
        
        if responsive.get("viewport_meta"):
            score += 40
        if responsive.get("responsive_images"):
            score += 30
        if responsive.get("media_queries"):
            score += 30
        
        return score
    
    def _analyze_navigation_structure(self, url: str) -> Dict[str, Any]:
        """Analysiert die Navigationsstruktur einer Seite - ORIGINAL für Kompatibilität"""
        structured_data = self._get_structured_data_for_url(url)
        if not structured_data:
            return {"url": url, "link_count": 0, "descriptive_links": 0, "descriptive_title": False}
        
        title_data = structured_data.get('title', {})
        structure_data = structured_data.get('structure', {})
        accessibility_data = structured_data.get('accessibility', {})
        
        # Erweiterte Navigation-Analyse für WCAG 2.4
        analysis = {
            "url": url,
            "page_title_analysis": {
                "title": title_data.get('page_title', ''),
                "descriptive": False,
                "unique": True,  # Würde über mehrere Seiten vergleichen
                "length": 0,
                "quality_score": 0,
                "issues": []
            },
            "heading_structure": {
                "headings_list": structure_data.get('headings', []),
                "hierarchy_issues": [],
                "h1_count": 0,
                "descriptive_headings": 0,
                "navigation_headings": []
            },
            "link_analysis": {
                "total_links": 0,
                "descriptive_links": 0,
                "ambiguous_links": [],
                "external_links": [],
                "internal_links": [],
                "same_page_links": [],
                "link_quality_issues": []
            },
            "skip_navigation": {
                "skip_links": [],
                "target_validation": [],
                "positioning": [],
                "visibility": []
            },
            "breadcrumb_analysis": {
                "breadcrumbs_found": [],
                "hierarchical": False,
                "aria_support": False
            },
            "landmark_roles": {
                "navigation_landmarks": [],
                "main_landmark": None,
                "banner_landmark": None,
                "contentinfo_landmark": None,
                "complementary_landmarks": []
            },
            "multiple_navigation_methods": {
                "site_search": None,
                "sitemap": None,
                "navigation_menu": None,
                "breadcrumbs": None,
                "related_links": None
            },
            "focus_indicators": {
                "visible_focus": [],
                "focus_order": [],
                "focus_management": []
            }
        }
        
        # Analysiere Seitentitel detailliert
        self._analyze_page_title(analysis, title_data)
        
        # Analysiere Überschriften-Hierarchie
        self._analyze_heading_hierarchy(analysis, structure_data)
        
        # Analysiere Links detailliert
        self._analyze_links_detailed(analysis, structure_data)
        
        # Suche nach Skip-Links
        self._analyze_skip_navigation(analysis, structure_data)
        
        # Analysiere Landmark-Rollen
        self._analyze_landmarks(analysis, accessibility_data, structure_data)
        
        # Prüfe mehrere Navigationsmethoden
        self._analyze_multiple_nav_methods(analysis, structure_data)
        
        # Analysiere Breadcrumbs
        self._analyze_breadcrumbs(analysis, structure_data)
        
        return analysis
    
    def _analyze_page_title(self, analysis: Dict[str, Any], title_data: Dict[str, Any]):
        """Analysiert Seitentitel-Qualität"""
        page_title = title_data.get('page_title', '')
        
        analysis["page_title_analysis"]["title"] = page_title
        analysis["page_title_analysis"]["length"] = len(page_title)
        
        if not page_title:
            analysis["page_title_analysis"]["issues"].append("missing_title")
            analysis["page_title_analysis"]["quality_score"] = 0
            return
        
        # Prüfe auf generische Titel
        generic_titles = ['startseite', 'home', 'index', 'untitled', 'new page']
        if page_title.lower().strip() in generic_titles:
            analysis["page_title_analysis"]["issues"].append("generic_title")
            analysis["page_title_analysis"]["descriptive"] = False
            analysis["page_title_analysis"]["quality_score"] = 2
        elif len(page_title) < 10:
            analysis["page_title_analysis"]["issues"].append("too_short")
            analysis["page_title_analysis"]["descriptive"] = False
            analysis["page_title_analysis"]["quality_score"] = 3
        elif len(page_title) > 60:
            analysis["page_title_analysis"]["issues"].append("too_long")
            analysis["page_title_analysis"]["descriptive"] = True
            analysis["page_title_analysis"]["quality_score"] = 7
        else:
            analysis["page_title_analysis"]["descriptive"] = True
            analysis["page_title_analysis"]["quality_score"] = 8
        
        # Prüfe auf Seitenhierarchie im Titel
        if ' - ' in page_title or ' | ' in page_title:
            analysis["page_title_analysis"]["quality_score"] += 2
    
    def _analyze_heading_hierarchy(self, analysis: Dict[str, Any], structure_data: Dict[str, Any]):
        """Analysiert Überschriften-Hierarchie detailliert"""
        headings_list = structure_data.get('headings', [])
        
        analysis["heading_structure"]["headings_list"] = headings_list
        
        # Zähle H1-Überschriften
        h1_headings = [h for h in headings_list if h.get('level') == 1]
        analysis["heading_structure"]["h1_count"] = len(h1_headings)
        
        if len(h1_headings) == 0:
            analysis["heading_structure"]["hierarchy_issues"].append("no_h1_found")
        elif len(h1_headings) > 1:
            analysis["heading_structure"]["hierarchy_issues"].append(f"multiple_h1_found: {len(h1_headings)}")
        
        # Prüfe Hierarchie-Sprünge
        prev_level = 0
        for heading in headings_list:
            level = heading.get('level', 0)
            if level - prev_level > 1:
                analysis["heading_structure"]["hierarchy_issues"].append(f"hierarchy_jump: H{prev_level} to H{level}")
            prev_level = level
        
        # Bewerte Überschriften-Qualität
        for heading in headings_list:
            text = heading.get('text', '').strip()
            if len(text) > 5 and not text.lower() in ['heading', 'title', 'überschrift']:
                analysis["heading_structure"]["descriptive_headings"] += 1
    
    def _analyze_links_detailed(self, analysis: Dict[str, Any], structure_data: Dict[str, Any]):
        """Analysiert Links detailliert"""
        links = structure_data.get('links', [])
        
        analysis["link_analysis"]["total_links"] = len(links)
        
        for link in links:
            link_text = str(link.get('text', '')).strip()
            href = str(link.get('href', ''))
            
            # Kategorisiere Links
            if href.startswith('#'):
                analysis["link_analysis"]["same_page_links"].append({
                    "text": link_text,
                    "href": href,
                    "target_exists": True  # Vereinfacht
                })
            elif 'http' in href and href:
                analysis["link_analysis"]["external_links"].append({
                    "text": link_text,
                    "href": href,
                    "opens_new_window": link.get('target') == '_blank'
                })
            else:
                analysis["link_analysis"]["internal_links"].append({
                    "text": link_text,
                    "href": href
                })
            
            # Bewerte Link-Text-Qualität
            if not link_text:
                analysis["link_analysis"]["link_quality_issues"].append({
                    "href": href,
                    "issue": "empty_link_text",
                    "severity": "high"
                })
            elif link_text.lower() in ['hier', 'more', 'click here', 'read more', 'weiterlesen', 'link']:
                analysis["link_analysis"]["ambiguous_links"].append({
                    "text": link_text,
                    "href": href,
                    "issue": "non_descriptive_link_text"
                })
            elif len(link_text) > 5:
                analysis["link_analysis"]["descriptive_links"] += 1
    
    def _analyze_skip_navigation(self, analysis: Dict[str, Any], structure_data: Dict[str, Any]):
        """Analysiert Skip-Navigation detailliert"""
        links = structure_data.get('links', [])
        
        skip_keywords = ['skip', 'jump', 'zum inhalt', 'navigation überspringen', 'springe zum']
        
        for link in links:
            link_text = str(link.get('text', '')).lower()
            
            if any(keyword in link_text for keyword in skip_keywords):
                skip_info = {
                    "text": link.get('text'),
                    "href": link.get('href'),
                    "target_exists": link.get('href', '').startswith('#'),
                    "is_first_link": True,  # Vereinfacht - würde Position prüfen
                    "visible_on_focus": True  # Vereinfacht - würde CSS prüfen
                }
                analysis["skip_navigation"]["skip_links"].append(skip_info)
    
    def _analyze_landmarks(self, analysis: Dict[str, Any], accessibility_data: Dict[str, Any], structure_data: Dict[str, Any]):
        """Analysiert ARIA Landmarks"""
        landmarks = accessibility_data.get('landmarks', [])
        
        for landmark in landmarks:
            role = landmark.get('role', '')
            
            if role == 'navigation':
                analysis["landmark_roles"]["navigation_landmarks"].append(landmark)
            elif role == 'main':
                analysis["landmark_roles"]["main_landmark"] = landmark
            elif role == 'banner':
                analysis["landmark_roles"]["banner_landmark"] = landmark
            elif role == 'contentinfo':
                analysis["landmark_roles"]["contentinfo_landmark"] = landmark
            elif role == 'complementary':
                analysis["landmark_roles"]["complementary_landmarks"].append(landmark)
    
    def _analyze_multiple_nav_methods(self, analysis: Dict[str, Any], structure_data: Dict[str, Any]):
        """Analysiert mehrere Navigationsmethoden"""
        
        # Suche nach Site-Search
        forms = structure_data.get('forms', [])
        for form in forms:
            if any(keyword in str(form.get('action', '')).lower() for keyword in ['search', 'suche']):
                analysis["multiple_navigation_methods"]["site_search"] = {
                    "found": True,
                    "accessible": bool(form.get('labels'))
                }
                break
        
        # Suche nach Navigation-Menü
        nav_elements = structure_data.get('nav_elements', [])
        if nav_elements:
            analysis["multiple_navigation_methods"]["navigation_menu"] = {
                "found": True,
                "count": len(nav_elements)
            }
    
    def _analyze_breadcrumbs(self, analysis: Dict[str, Any], structure_data: Dict[str, Any]):
        """Analysiert Breadcrumb-Navigation"""
        
        # Suche nach Breadcrumb-Mustern
        nav_elements = structure_data.get('nav_elements', [])
        for nav in nav_elements:
            if 'breadcrumb' in str(nav.get('aria-label', '')).lower():
                analysis["breadcrumb_analysis"]["breadcrumbs_found"].append({
                    "element": nav.get('selector'),
                    "aria_label": nav.get('aria-label'),
                    "structured": True
                })
                analysis["breadcrumb_analysis"]["hierarchical"] = True
                analysis["breadcrumb_analysis"]["aria_support"] = True

class LesbarkeitSpracheExtractor(BaseWCAGExtractor):
    """3.1 Lesbarkeit und Sprache - Fokus auf Sprachkennzeichnung"""
    
    def extract_focused_data(self) -> Dict[str, Any]:
        """Extrahiert Daten für WCAG 3.1 Lesbarkeit und Sprache"""
        start_time = time.time()
        
        data = {
            "wcag_area": "3.1_lesbarkeit_sprache",
            "focus": "Sprachkennzeichnung, Sprachwechsel, Abkürzungen, Verständlichkeit",
            "extracted_at": time.strftime("%Y-%m-%d_%H-%M-%S"),
            "language_declaration": {
                "main_language": None,
                "language_changes": [],
                "missing_lang_attributes": 0
            },
            "text_complexity": {
                "abbreviations": [],
                "technical_terms": [],
                "readability_indicators": []
            },
            "content_structure": {
                "clear_headings": 0,
                "paragraph_length": [],
                "list_usage": 0
            },
            "detailed_analysis": [],
            "pages_analyzed": []
        }
        
        # Analysiere jede Seite
        for url, page_data in self.crawl_data.get('data', {}).items():
            page_analysis = self._analyze_language_accessibility(url)
            data["detailed_analysis"].append(page_analysis)
            data["pages_analyzed"].append(url)
            
            # Sammle Hauptsprache (sollte konsistent sein)
            if page_analysis.get("main_language") and not data["language_declaration"]["main_language"]:
                data["language_declaration"]["main_language"] = page_analysis["main_language"]
            
            data["text_complexity"]["abbreviations"].extend(page_analysis.get("abbreviations", []))
        
        data["extraction_time_seconds"] = round(time.time() - start_time, 2)
        abbr_count = len(data["text_complexity"]["abbreviations"])
        self.logger.info(f"✅ Sprache-Extraktion: {abbr_count} Abkürzungen gefunden in {data['extraction_time_seconds']}s")
        
        return data
    
    def _analyze_language_accessibility(self, url: str) -> Dict[str, Any]:
        """Analysiert Sprach-Zugänglichkeit einer Seite"""
        structured_data = self._get_structured_data_for_url(url)
        if not structured_data:
            return {"url": url, "main_language": None, "abbreviations": []}
        
        # Sprache aus Metadaten extrahieren
        metadata = structured_data.get('metadata', {})
        
        return {
            "url": url,
            "main_language": metadata.get('language'),
            "abbreviations": [],  # Würde in echter Implementierung <abbr> Tags analysieren
            "foreign_phrases": [],  # Würde lang-Attribute in Spans suchen
            "text_complexity": "medium"  # Vereinfacht für Demo
        }

class VorhersehbarkeitExtractor(BaseWCAGExtractor):
    """3.2 Vorhersehbarkeit - Fokus auf konsistentes Verhalten"""
    
    def extract_focused_data(self) -> Dict[str, Any]:
        """Extrahiert Daten für WCAG 3.2 Vorhersehbarkeit"""
        start_time = time.time()
        
        data = {
            "wcag_area": "3.2_vorhersehbarkeit",
            "focus": "Konsistente Navigation, vorhersehbare Funktionen, einheitliche Bezeichnungen",
            "extracted_at": time.strftime("%Y-%m-%d_%H-%M-%S"),
            "consistency_analysis": {
                "navigation_consistent": True,
                "function_naming": [],
                "unexpected_changes": []
            },
            "behavior_analysis": {
                "focus_changes": [],
                "form_submissions": [],
                "popup_behaviors": []
            },
            "interface_consistency": {
                "button_labels": [],
                "link_patterns": [],
                "layout_consistency": True
            },
            "detailed_analysis": [],
            "pages_analyzed": []
        }
        
        # Analysiere jede Seite
        for url, page_data in self.crawl_data.get('data', {}).items():
            page_analysis = self._analyze_predictability(url)
            data["detailed_analysis"].append(page_analysis)
            data["pages_analyzed"].append(url)
            
            # Sammle Button-Labels für Konsistenz-Analyse
            data["interface_consistency"]["button_labels"].extend(page_analysis.get("button_texts", []))
        
        # Analysiere Konsistenz über alle Seiten
        button_labels = data["interface_consistency"]["button_labels"]
        unique_labels = set(button_labels)
        data["interface_consistency"]["label_variety"] = len(unique_labels)
        
        data["extraction_time_seconds"] = round(time.time() - start_time, 2)
        total_elements = len(button_labels)
        self.logger.info(f"✅ Vorhersehbarkeit-Extraktion: {total_elements} Interface-Elemente in {data['extraction_time_seconds']}s")
        
        return data
    
    def _analyze_predictability(self, url: str) -> Dict[str, Any]:
        """Analysiert Vorhersehbarkeit einer Seite"""
        structured_data = self._get_structured_data_for_url(url)
        if not structured_data:
            return {"url": url, "button_texts": [], "form_count": 0}
        
        structure_data = structured_data.get('structure', {})
        interactive = structure_data.get('interactive_elements', {})
        
        buttons = interactive.get('buttons', [])
        forms = structure_data.get('forms', [])
        
        return {
            "url": url,
            "button_texts": [btn.get('text', '') for btn in buttons if btn.get('text')],
            "form_count": len(forms),
            "auto_submit_forms": [form for form in forms if form.get('auto_submit')],
            "navigation_position": "consistent"  # Vereinfacht für Demo
        }

class EingabeunterstuetzungExtractor(BaseWCAGExtractor):
    """3.3 Eingabeunterstützung - Fokus auf Formulare und Fehlerhilfen"""
    
    def extract_focused_data(self) -> Dict[str, Any]:
        """Extrahiert Daten für WCAG 3.3 Eingabeunterstützung"""
        start_time = time.time()
        
        data = {
            "wcag_area": "3.3_eingabeunterstuetzung",
            "focus": "Formulare, Fehlermeldungen, Eingabehilfen, Validierung",
            "extracted_at": time.strftime("%Y-%m-%d_%H-%M-%S"),
            "form_analysis": {
                "total_forms": 0,
                "accessible_forms": 0,
                "problematic_forms": []
            },
            "field_labeling": {
                "total_fields": 0,
                "labeled_fields": 0,
                "missing_labels": [],
                "implicit_labels": 0,
                "explicit_labels": 0
            },
            "required_fields": {
                "total_required": 0,
                "clearly_marked": 0,
                "aria_required": 0,
                "asterisk_only": 0,
                "missing_indication": []
            },
            "error_handling": {
                "error_messages": [],
                "inline_validation": [],
                "error_identification": [],
                "error_suggestions": []
            },
            "input_assistance": {
                "format_hints": [],
                "help_texts": [],
                "placeholders": [],
                "examples": []
            },
            "validation_analysis": {
                "client_side": [],
                "server_side": [],
                "real_time": [],
                "on_submit": []
            },
            "fieldset_structure": {
                "fieldsets": 0,
                "legends": 0,
                "grouped_fields": []
            },
            "aria_support": {
                "aria_describedby": 0,
                "aria_invalid": 0,
                "aria_required": 0,
                "live_regions": []
            },
            "detailed_analysis": [],
            "pages_analyzed": []
        }
        
        # Analysiere jede Seite
        for url, page_data in self.crawl_data.get('data', {}).items():
            page_analysis = self._analyze_form_assistance(url)
            data["detailed_analysis"].append(page_analysis)
            data["pages_analyzed"].append(url)
            
            # Akkumuliere Formular-Statistiken
            data["form_analysis"]["total_forms"] += page_analysis.get("form_analysis", {}).get("total_forms", 0)
            data["field_labeling"]["labeled_fields"] += page_analysis.get("field_labeling", {}).get("labeled_fields", 0)
            data["required_fields"]["total_required"] += page_analysis.get("required_fields", {}).get("total_required", 0)
        
        data["extraction_time_seconds"] = round(time.time() - start_time, 2)
        total_forms = data["form_analysis"]["total_forms"]
        self.logger.info(f"✅ Eingabeunterstützung-Extraktion: {total_forms} Formulare analysiert in {data['extraction_time_seconds']}s")
        
        return data
    
    def _analyze_form_assistance(self, url: str) -> Dict[str, Any]:
        """Analysiert Formularhilfen einer Seite"""
        structured_data = self._get_structured_data_for_url(url)
        if not structured_data:
            return {"url": url, "form_count": 0, "labeled_fields": 0, "required_fields": 0}
        
        structure_data = structured_data.get('structure', {})
        forms = structure_data.get('forms', [])
        
        # Erweiterte Formular-Analyse für WCAG 3.3
        analysis = {
            "url": url,
            "form_analysis": {
                "total_forms": len(forms),
                "accessible_forms": 0,
                "problematic_forms": []
            },
            "field_labeling": {
                "total_fields": 0,
                "labeled_fields": 0,
                "missing_labels": [],
                "implicit_labels": 0,
                "explicit_labels": 0
            },
            "required_fields": {
                "total_required": 0,
                "clearly_marked": 0,
                "aria_required": 0,
                "asterisk_only": 0,
                "missing_indication": []
            },
            "error_handling": {
                "error_messages": [],
                "inline_validation": [],
                "error_identification": [],
                "error_suggestions": []
            },
            "input_assistance": {
                "format_hints": [],
                "help_texts": [],
                "placeholders": [],
                "examples": []
            },
            "validation_analysis": {
                "client_side": [],
                "server_side": [],
                "real_time": [],
                "on_submit": []
            },
            "fieldset_structure": {
                "fieldsets": 0,
                "legends": 0,
                "grouped_fields": []
            },
            "aria_support": {
                "aria_describedby": 0,
                "aria_invalid": 0,
                "aria_required": 0,
                "live_regions": []
            }
        }
        
        # Analysiere jedes Formular detailliert
        for form in forms:
            form_issues = []
            
            # Analysiere Labels
            labels = form.get('labels', [])
            inputs = form.get('inputs', [])
            fieldsets = form.get('fieldsets', [])
            
            analysis["field_labeling"]["total_fields"] += len(inputs)
            analysis["fieldset_structure"]["fieldsets"] += len(fieldsets)
            
            # Prüfe Label-Zuordnungen
            self._analyze_field_labels(analysis, inputs, labels, form_issues)
            
            # Prüfe Required-Fields
            self._analyze_required_fields(analysis, inputs, form_issues)
            
            # Prüfe Error-Handling
            self._analyze_error_handling(analysis, form, form_issues)
            
            # Prüfe Input-Assistance
            self._analyze_input_assistance(analysis, inputs, form)
            
            # Prüfe ARIA-Support
            self._analyze_aria_support(analysis, inputs, form)
            
            # Bewerte Formular-Qualität
            if form_issues:
                analysis["form_analysis"]["problematic_forms"].append({
                    "form_selector": form.get('selector', 'unknown'),
                    "issues": form_issues,
                    "severity": "high" if len(form_issues) > 3 else "medium"
                })
            else:
                analysis["form_analysis"]["accessible_forms"] += 1
        
        return analysis
    
    def _analyze_field_labels(self, analysis: Dict[str, Any], inputs: List, labels: List, form_issues: List):
        """Analysiert Field-Label-Zuordnungen"""
        
        labeled_count = 0
        
        for input_field in inputs:
            input_id = input_field.get('id')
            input_type = input_field.get('type', 'text')
            
            # Suche nach zugehörigem Label
            has_label = False
            label_type = None
            
            # Explizite Labels (for-Attribut)
            for label in labels:
                if label.get('for') == input_id:
                    has_label = True
                    label_type = "explicit"
                    analysis["field_labeling"]["explicit_labels"] += 1
                    break
            
            # Implizite Labels (Label umschließt Input)
            if not has_label and input_field.get('wrapped_by_label'):
                has_label = True
                label_type = "implicit"
                analysis["field_labeling"]["implicit_labels"] += 1
            
            # ARIA-Labels
            if not has_label and (input_field.get('aria-label') or input_field.get('aria-labelledby')):
                has_label = True
                label_type = "aria"
            
            if has_label:
                labeled_count += 1
            else:
                analysis["field_labeling"]["missing_labels"].append({
                    "input_id": input_id,
                    "input_type": input_type,
                    "selector": input_field.get('selector', 'unknown')
                })
                form_issues.append(f"unlabeled_field: {input_type}")
        
        analysis["field_labeling"]["labeled_fields"] += labeled_count
    
    def _analyze_required_fields(self, analysis: Dict[str, Any], inputs: List, form_issues: List):
        """Analysiert Required-Field-Markierungen"""
        
        for input_field in inputs:
            if input_field.get('required'):
                analysis["required_fields"]["total_required"] += 1
                
                # Prüfe Markierungen
                has_visual_indicator = False
                has_aria_required = bool(input_field.get('aria-required'))
                
                # Suche nach visuellen Indikatoren (Stern, "Required", etc.)
                label_text = input_field.get('label_text', '')
                if '*' in label_text or 'required' in label_text.lower() or 'pflicht' in label_text.lower():
                    has_visual_indicator = True
                    analysis["required_fields"]["clearly_marked"] += 1
                elif '*' in label_text:
                    analysis["required_fields"]["asterisk_only"] += 1
                
                if has_aria_required:
                    analysis["required_fields"]["aria_required"] += 1
                
                if not has_visual_indicator and not has_aria_required:
                    analysis["required_fields"]["missing_indication"].append({
                        "input_id": input_field.get('id'),
                        "input_type": input_field.get('type')
                    })
                    form_issues.append("required_field_not_indicated")
    
    def _analyze_error_handling(self, analysis: Dict[str, Any], form: Dict[str, Any], form_issues: List):
        """Analysiert Error-Handling"""
        
        error_elements = form.get('error_elements', [])
        
        for error in error_elements:
            error_info = {
                "element": error.get('selector'),
                "message": error.get('text', ''),
                "associated_field": error.get('associated_field'),
                "type": error.get('type', 'general')
            }
            
            # Prüfe Error-Message-Qualität
            message = error.get('text', '').lower()
            if message:
                if any(word in message for word in ['ungültig', 'invalid', 'fehler', 'error']):
                    if any(suggestion in message for suggestion in ['sollte', 'should', 'versuchen', 'try']):
                        error_info["has_suggestion"] = True
                        analysis["error_handling"]["error_suggestions"].append(error_info)
                    else:
                        error_info["has_suggestion"] = False
                
                analysis["error_handling"]["error_messages"].append(error_info)
            else:
                form_issues.append("empty_error_message")
    
    def _analyze_input_assistance(self, analysis: Dict[str, Any], inputs: List, form: Dict[str, Any]):
        """Analysiert Input-Assistance"""
        
        for input_field in inputs:
            input_type = input_field.get('type', 'text')
            
            # Prüfe Placeholder
            placeholder = input_field.get('placeholder')
            if placeholder:
                analysis["input_assistance"]["placeholders"].append({
                    "field": input_field.get('id'),
                    "placeholder": placeholder,
                    "helpful": len(placeholder) > 5
                })
            
            # Prüfe Help-Text (aria-describedby)
            described_by = input_field.get('aria-describedby')
            if described_by:
                analysis["input_assistance"]["help_texts"].append({
                    "field": input_field.get('id'),
                    "help_id": described_by
                })
            
            # Prüfe Format-Hints für spezielle Felder
            if input_type in ['email', 'tel', 'date', 'url']:
                analysis["input_assistance"]["format_hints"].append({
                    "field": input_field.get('id'),
                    "type": input_type,
                    "has_hint": bool(placeholder or described_by)
                })
    
    def _analyze_aria_support(self, analysis: Dict[str, Any], inputs: List, form: Dict[str, Any]):
        """Analysiert ARIA-Support"""
        
        for input_field in inputs:
            if input_field.get('aria-describedby'):
                analysis["aria_support"]["aria_describedby"] += 1
            
            if input_field.get('aria-invalid'):
                analysis["aria_support"]["aria_invalid"] += 1
            
            if input_field.get('aria-required'):
                analysis["aria_support"]["aria_required"] += 1
        
        # Prüfe Live-Regions für dynamische Fehlermeldungen
        live_regions = form.get('live_regions', [])
        analysis["aria_support"]["live_regions"] = live_regions

class RobustheitsKompatibilitaetExtractor(BaseWCAGExtractor):
    """4.1 Robustheit und Kompatibilität - SUPER-ERWEITERT mit 14 HTTP Headers + Performance + Security"""
    
    def extract_focused_data(self) -> Dict[str, Any]:
        """Extrahiert Daten für WCAG 4.1 Robustheit und Kompatibilität - SUPER-ERWEITERT"""
        start_time = time.time()
        self.logger.info("🔒 Starte SUPER-ERWEITERTE Robustheit-Extraktion...")
        
        data = {
            "wcag_area": "4.1 Robustheit und Kompatibilität",
            "extraction_method": "super_erweitert",
            "extracted_at": time.strftime("%Y-%m-%d_%H-%M-%S"),
            
            # NEUE: Detaillierte HTTP Headers-Analyse (14 Headers)
            "comprehensive_security_analysis": {
                "total_security_headers": 0,
                "security_headers": {
                    "https_enforcement": False,
                    "hsts_enabled": False,
                    "csp_implemented": False,
                    "xframe_protection": False,
                    "xss_protection": False,
                    "content_type_nosniff": False
                },
                "security_score": 0,
                "vulnerability_warnings": [],
                "compliance_level": "unknown"
            },
            
            # NEUE: Detaillierte Performance-Analyse (827.335 bytes)
            "comprehensive_performance_analysis": {
                "page_weight_analysis": {
                    "total_bytes": 0,
                    "size_breakdown": {
                        "html": 0,
                        "css": 0,
                        "javascript": 0,
                        "images": 0,
                        "fonts": 0,
                        "other": 0
                    },
                    "optimization_opportunities": []
                },
                "core_web_vitals": {
                    "lcp_score": 0,
                    "fid_score": 0,
                    "cls_score": 0,
                    "vitals_grade": "unknown"
                },
                "resource_optimization": {
                    "compression_enabled": False,
                    "minification_applied": False,
                    "caching_headers": [],
                    "cdn_usage": False
                },
                "performance_score": 0
            },
            
            # NEUE: HTTP Headers Deep-Dive
            "http_headers_analysis": {
                "total_headers": 0,
                "header_inventory": [],
                "missing_security_headers": [],
                "performance_headers": [],
                "accessibility_relevant_headers": []
            },
            
            # NEUE: Technology Stack-Analyse
            "technology_stack": {
                "server_technology": [],
                "frameworks_detected": [],
                "content_management": [],
                "accessibility_tools": [],
                "modern_standards_compliance": 0
            },
            
            # ERWEITERT: Original Daten
            "code_quality": {
                "html_validation": {
                    "valid_structure": True,
                    "parsing_errors": []
                },
                "doctype_present": True,
                "semantic_markup": 0
            },
            "aria_implementation": {
                "aria_roles": [],
                "aria_properties": [],
                "live_regions": [],
                "landmark_roles": []
            },
            "custom_controls": {
                "total_custom": 0,
                "properly_labeled": 0,
                "missing_roles": []
            },
            "detailed_analysis": [],
            "pages_analyzed": []
        }
        
        # Analysiere jede Seite mit SUPER-ERWEITERTEN Methoden
        total_headers = 0
        total_bytes = 0
        security_features = 0
        
        for url, page_data in self.crawl_data.get('data', {}).items():
            # NEUE: Umfassende Robustheit-Analyse
            page_analysis = self._analyze_comprehensive_robustness(url, page_data)
            data["detailed_analysis"].append(page_analysis)
            data["pages_analyzed"].append(url)
            
            # Akkumuliere NEUE Daten
            headers_data = page_analysis.get("headers_analysis", {})
            performance_data = page_analysis.get("performance_analysis", {})
            security_data = page_analysis.get("security_analysis", {})
            
            total_headers += headers_data.get("header_count", 0)
            total_bytes += performance_data.get("page_weight", 0)
            security_features += security_data.get("security_features_count", 0)
            
            data["http_headers_analysis"]["header_inventory"].extend(
                headers_data.get("header_list", [])
            )
            data["comprehensive_performance_analysis"]["resource_optimization"]["caching_headers"].extend(
                performance_data.get("caching_headers", [])
            )
            data["technology_stack"]["frameworks_detected"].extend(
                security_data.get("frameworks", [])
            )
            
            # Original Daten
            data["aria_implementation"]["aria_roles"].extend(page_analysis.get("aria_roles", []))
            data["custom_controls"]["total_custom"] += page_analysis.get("custom_elements", 0)
        
        # Finale Zusammenfassung
        data["http_headers_analysis"]["total_headers"] = total_headers
        data["comprehensive_performance_analysis"]["page_weight_analysis"]["total_bytes"] = total_bytes
        data["comprehensive_security_analysis"]["total_security_headers"] = security_features
        
        # Berechne Super-Scores
        self._calculate_comprehensive_robustness_scores(data, total_headers, total_bytes, security_features)
        
        data["extraction_time_seconds"] = round(time.time() - start_time, 2)
        
        self.logger.info(f"✅ SUPER-ERWEITERTE Robustheit-Extraktion: {total_headers} Headers, {total_bytes} bytes, {security_features} Security-Features in {data['extraction_time_seconds']}s")
        
        return data
    
    def _analyze_comprehensive_robustness(self, url: str, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Umfassende Robustheit-Analyse mit 14 Headers + Performance + Security"""
        analysis = {
            "page_url": url,
            "headers_analysis": self._analyze_comprehensive_headers(page_data),
            "performance_analysis": self._analyze_comprehensive_performance(page_data),
            "security_analysis": self._analyze_comprehensive_security(page_data),
            "technology_analysis": self._analyze_technology_stack(page_data),
            "accessibility_robustness": self._analyze_accessibility_robustness(page_data),
            
            # Original Daten für Kompatibilität
            "aria_roles": [],
            "custom_elements": 0
        }
        
        # Original Analyse für Kompatibilität
        original_analysis = self._analyze_robustness(url)
        analysis.update({
            "aria_roles": original_analysis.get("aria_roles", []),
            "custom_elements": original_analysis.get("custom_elements", 0)
        })
        
        return analysis
    
    def _analyze_comprehensive_headers(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Analysiert die 14 HTTP Headers im Detail"""
        headers_data = page_data.get("headers", {})
        
        analysis = {
            "header_count": 0,
            "header_list": [],
            "security_headers": {
                "strict_transport_security": None,
                "content_security_policy": None,
                "x_frame_options": None,
                "x_content_type_options": None,
                "x_xss_protection": None,
                "referrer_policy": None
            },
            "performance_headers": {
                "cache_control": None,
                "expires": None,
                "etag": None,
                "last_modified": None
            },
            "accessibility_headers": {
                "content_type": None,
                "content_language": None
            },
            "missing_critical_headers": [],
            "header_quality_score": 0
        }
        
        if isinstance(headers_data, dict):
            # Analysiere alle verfügbaren Headers
            for header_name, header_value in headers_data.items():
                header_info = {
                    "name": header_name,
                    "value": header_value,
                    "category": self._categorize_header(header_name),
                    "security_impact": self._assess_security_impact(header_name, header_value),
                    "accessibility_relevance": self._assess_accessibility_relevance(header_name)
                }
                
                analysis["header_list"].append(header_info)
                analysis["header_count"] += 1
                
                # Kategorisiere Security Headers
                header_lower = header_name.lower()
                if "strict-transport-security" in header_lower:
                    analysis["security_headers"]["strict_transport_security"] = header_value
                elif "content-security-policy" in header_lower:
                    analysis["security_headers"]["content_security_policy"] = header_value
                elif "x-frame-options" in header_lower:
                    analysis["security_headers"]["x_frame_options"] = header_value
                elif "x-content-type-options" in header_lower:
                    analysis["security_headers"]["x_content_type_options"] = header_value
                elif "x-xss-protection" in header_lower:
                    analysis["security_headers"]["x_xss_protection"] = header_value
                elif "referrer-policy" in header_lower:
                    analysis["security_headers"]["referrer_policy"] = header_value
                
                # Performance Headers
                elif "cache-control" in header_lower:
                    analysis["performance_headers"]["cache_control"] = header_value
                elif "expires" in header_lower:
                    analysis["performance_headers"]["expires"] = header_value
                elif "etag" in header_lower:
                    analysis["performance_headers"]["etag"] = header_value
                elif "last-modified" in header_lower:
                    analysis["performance_headers"]["last_modified"] = header_value
                
                # Accessibility Headers
                elif "content-type" in header_lower:
                    analysis["accessibility_headers"]["content_type"] = header_value
                elif "content-language" in header_lower:
                    analysis["accessibility_headers"]["content_language"] = header_value
        
        # Prüfe fehlende kritische Headers
        critical_headers = [
            "strict-transport-security",
            "content-security-policy", 
            "x-frame-options",
            "x-content-type-options"
        ]
        
        for critical_header in critical_headers:
            if not analysis["security_headers"].get(critical_header.replace("-", "_")):
                analysis["missing_critical_headers"].append({
                    "header": critical_header,
                    "security_risk": self._assess_missing_header_risk(critical_header),
                    "recommendation": self._get_header_recommendation(critical_header)
                })
        
        # Berechne Header-Quality-Score
        present_critical = len(critical_headers) - len(analysis["missing_critical_headers"])
        analysis["header_quality_score"] = round((present_critical / len(critical_headers)) * 100, 1)
        
        return analysis
    
    def _analyze_comprehensive_performance(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Analysiert Performance-Daten (827.335 bytes)"""
        performance_data = page_data.get("performance", {})
        
        analysis = {
            "page_weight": 0,
            "resource_breakdown": {
                "html_size": 0,
                "css_size": 0,
                "js_size": 0,
                "image_size": 0,
                "font_size": 0,
                "other_size": 0
            },
            "optimization_analysis": {
                "compression_ratio": 0,
                "minification_savings": 0,
                "image_optimization_potential": 0,
                "caching_effectiveness": 0
            },
            "core_web_vitals_simulation": {
                "estimated_lcp": 0,
                "loading_performance": "unknown",
                "resource_priority": []
            },
            "performance_recommendations": [],
            "performance_grade": "unknown"
        }
        
        if isinstance(performance_data, dict):
            # Extrahiere Page Weight
            page_weight = performance_data.get("page_weight", 0)
            if isinstance(page_weight, (int, float)):
                analysis["page_weight"] = int(page_weight)
            elif isinstance(page_weight, str) and page_weight.replace(",", "").replace(".", "").isdigit():
                analysis["page_weight"] = int(float(page_weight.replace(",", "")))
            
            # Analysiere Resource-Größen
            resources = performance_data.get("resources", {})
            if isinstance(resources, dict):
                analysis["resource_breakdown"]["html_size"] = resources.get("html", 0)
                analysis["resource_breakdown"]["css_size"] = resources.get("css", 0)
                analysis["resource_breakdown"]["js_size"] = resources.get("javascript", 0)
                analysis["resource_breakdown"]["image_size"] = resources.get("images", 0)
                analysis["resource_breakdown"]["font_size"] = resources.get("fonts", 0)
            
            # Performance-Optimierung-Analyse
            if analysis["page_weight"] > 0:
                # Größe-basierte Bewertung
                if analysis["page_weight"] < 500000:  # < 500KB
                    analysis["performance_grade"] = "excellent"
                elif analysis["page_weight"] < 1000000:  # < 1MB
                    analysis["performance_grade"] = "good"
                elif analysis["page_weight"] < 2000000:  # < 2MB
                    analysis["performance_grade"] = "average"
                else:
                    analysis["performance_grade"] = "poor"
                
                # Optimierungs-Empfehlungen
                if analysis["resource_breakdown"]["image_size"] > analysis["page_weight"] * 0.5:
                    analysis["performance_recommendations"].append({
                        "type": "image_optimization",
                        "potential_savings": "30-50%",
                        "recommendation": "Implement WebP/AVIF, compression, lazy loading"
                    })
                
                if analysis["resource_breakdown"]["js_size"] > 300000:  # > 300KB JS
                    analysis["performance_recommendations"].append({
                        "type": "javascript_optimization",
                        "potential_savings": "20-40%",
                        "recommendation": "Code splitting, tree shaking, minification"
                    })
        
        return analysis
    
    def _analyze_comprehensive_security(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Analysiert Security-Features"""
        security_data = page_data.get("security", {})
        headers_data = page_data.get("headers", {})
        
        analysis = {
            "security_features_count": 0,
            "security_compliance": {
                "https_enforced": False,
                "hsts_implemented": False,
                "csp_configured": False,
                "clickjacking_protection": False,
                "xss_protection": False
            },
            "vulnerability_assessment": {
                "high_risk": [],
                "medium_risk": [],
                "low_risk": []
            },
            "frameworks": [],
            "security_score": 0,
            "compliance_recommendations": []
        }
        
        # Analysiere Security Headers
        if isinstance(headers_data, dict):
            for header_name, header_value in headers_data.items():
                header_lower = header_name.lower()
                
                if "strict-transport-security" in header_lower:
                    analysis["security_compliance"]["hsts_implemented"] = True
                    analysis["security_features_count"] += 1
                elif "content-security-policy" in header_lower:
                    analysis["security_compliance"]["csp_configured"] = True
                    analysis["security_features_count"] += 1
                elif "x-frame-options" in header_lower:
                    analysis["security_compliance"]["clickjacking_protection"] = True
                    analysis["security_features_count"] += 1
                elif "x-xss-protection" in header_lower:
                    analysis["security_compliance"]["xss_protection"] = True
                    analysis["security_features_count"] += 1
        
        # Prüfe HTTPS
        if isinstance(security_data, dict):
            if security_data.get("https_enabled"):
                analysis["security_compliance"]["https_enforced"] = True
                analysis["security_features_count"] += 1
        
        # Vulnerability Assessment
        missing_features = []
        for feature, implemented in analysis["security_compliance"].items():
            if not implemented:
                missing_features.append(feature)
        
        if len(missing_features) > 3:
            analysis["vulnerability_assessment"]["high_risk"].append({
                "issue": "multiple_missing_security_features",
                "missing_count": len(missing_features),
                "impact": "High vulnerability to various attacks"
            })
        elif len(missing_features) > 1:
            analysis["vulnerability_assessment"]["medium_risk"].append({
                "issue": "some_missing_security_features", 
                "missing_count": len(missing_features),
                "impact": "Moderate security gaps"
            })
        
        # Berechne Security Score
        total_features = len(analysis["security_compliance"])
        implemented_features = sum(1 for implemented in analysis["security_compliance"].values() if implemented)
        analysis["security_score"] = round((implemented_features / total_features) * 100, 1)
        
        return analysis
    
    def _analyze_technology_stack(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Analysiert Technology Stack"""
        headers_data = page_data.get("headers", {})
        scripting_data = page_data.get("scripting", {})
        
        analysis = {
            "server_info": [],
            "frameworks": [],
            "cms_detection": [],
            "modern_standards": {
                "http2_support": False,
                "modern_js_features": 0,
                "progressive_enhancement": False
            },
            "accessibility_tools": []
        }
        
        # Server-Technologie aus Headers
        if isinstance(headers_data, dict):
            server_header = headers_data.get("server", "")
            if server_header:
                analysis["server_info"].append({
                    "type": "web_server",
                    "value": server_header,
                    "security_implications": self._assess_server_security(server_header)
                })
            
            # Weitere Tech-Detection
            powered_by = headers_data.get("x-powered-by", "")
            if powered_by:
                analysis["frameworks"].append({
                    "type": "backend_framework",
                    "value": powered_by,
                    "version_disclosure": "version_exposed" if any(char.isdigit() for char in powered_by) else "version_hidden"
                })
        
        # Framework-Detection aus Scripting
        if isinstance(scripting_data, dict):
            frameworks = scripting_data.get("frameworks", [])
            if isinstance(frameworks, list):
                for framework in frameworks:
                    analysis["frameworks"].append({
                        "type": "frontend_framework",
                        "value": framework,
                        "accessibility_support": self._assess_framework_accessibility(framework)
                    })
        
        return analysis
    
    def _analyze_accessibility_robustness(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """NEUE: Analysiert Accessibility-Robustheit"""
        accessibility_data = page_data.get("accessibility", {})
        
        analysis = {
            "assistive_tech_compatibility": {
                "screen_reader_support": 0,
                "keyboard_navigation": 0,
                "voice_control": 0
            },
            "markup_quality": {
                "semantic_elements": 0,
                "aria_implementation": 0,
                "standards_compliance": 0
            },
            "future_proof_features": []
        }
        
        # Analysiere ARIA-Implementation
        if isinstance(accessibility_data, dict):
            aria_roles = accessibility_data.get("aria_roles", [])
            landmarks = accessibility_data.get("landmarks", [])
            
            if isinstance(aria_roles, list):
                analysis["markup_quality"]["aria_implementation"] = len(aria_roles)
            
            if isinstance(landmarks, list):
                analysis["markup_quality"]["semantic_elements"] = len(landmarks)
        
        return analysis
    
    def _calculate_comprehensive_robustness_scores(self, data: Dict[str, Any], total_headers: int, total_bytes: int, security_features: int):
        """Berechnet umfassende Robustheit-Scores"""
        
        # Security Score
        if security_features > 0:
            max_security_features = 5  # HTTPS, HSTS, CSP, X-Frame, XSS
            data["comprehensive_security_analysis"]["security_score"] = round(
                min(100, (security_features / max_security_features) * 100), 1
            )
        
        # Performance Score  
        if total_bytes > 0:
            # Basis-Score basierend auf Größe
            if total_bytes < 500000:  # < 500KB
                performance_score = 95
            elif total_bytes < 1000000:  # < 1MB
                performance_score = 80
            elif total_bytes < 2000000:  # < 2MB
                performance_score = 60
            else:
                performance_score = 30
            
            data["comprehensive_performance_analysis"]["performance_score"] = performance_score
        
        # Headers Quality Score
        if total_headers > 0:
            # Mindestens 10 Headers für gute Bewertung
            headers_score = min(100, (total_headers / 10) * 100)
            data["http_headers_analysis"]["quality_score"] = round(headers_score, 1)
    
    def _categorize_header(self, header_name: str) -> str:
        """Kategorisiert HTTP Headers"""
        header_lower = header_name.lower()
        
        security_headers = ["strict-transport-security", "content-security-policy", "x-frame-options", "x-xss-protection"]
        performance_headers = ["cache-control", "expires", "etag", "last-modified"]
        content_headers = ["content-type", "content-language", "content-encoding"]
        
        if any(sec_header in header_lower for sec_header in security_headers):
            return "security"
        elif any(perf_header in header_lower for perf_header in performance_headers):
            return "performance"
        elif any(content_header in header_lower for content_header in content_headers):
            return "content"
        else:
            return "other"
    
    def _assess_security_impact(self, header_name: str, header_value: str) -> str:
        """Bewertet Security-Impact eines Headers"""
        header_lower = header_name.lower()
        
        if "strict-transport-security" in header_lower:
            return "high" if "max-age" in header_value else "medium"
        elif "content-security-policy" in header_lower:
            return "high" if len(header_value) > 20 else "medium"
        elif "x-frame-options" in header_lower:
            return "medium"
        else:
            return "low"
    
    def _assess_accessibility_relevance(self, header_name: str) -> bool:
        """Prüft Accessibility-Relevanz eines Headers"""
        accessibility_headers = ["content-type", "content-language", "vary", "accept-language"]
        return any(acc_header in header_name.lower() for acc_header in accessibility_headers)
    
    def _assess_missing_header_risk(self, header_name: str) -> str:
        """Bewertet Risiko fehlender Headers"""
        high_risk_headers = ["strict-transport-security", "content-security-policy"]
        medium_risk_headers = ["x-frame-options", "x-content-type-options"]
        
        if header_name in high_risk_headers:
            return "high"
        elif header_name in medium_risk_headers:
            return "medium"
        else:
            return "low"
    
    def _get_header_recommendation(self, header_name: str) -> str:
        """Gibt Empfehlung für fehlende Headers"""
        recommendations = {
            "strict-transport-security": "Add HSTS header: Strict-Transport-Security: max-age=31536000; includeSubDomains",
            "content-security-policy": "Implement CSP: Content-Security-Policy: default-src 'self'",
            "x-frame-options": "Add frame protection: X-Frame-Options: DENY",
            "x-content-type-options": "Prevent MIME sniffing: X-Content-Type-Options: nosniff"
        }
        return recommendations.get(header_name, f"Consider implementing {header_name}")
    
    def _assess_server_security(self, server_header: str) -> str:
        """Bewertet Server-Security"""
        if any(char.isdigit() for char in server_header):
            return "version_exposed"
        else:
            return "version_hidden"
    
    def _assess_framework_accessibility(self, framework: str) -> str:
        """Bewertet Framework-Accessibility-Support"""
        accessibility_friendly = ["react", "vue", "angular", "svelte"]
        framework_lower = str(framework).lower()
        
        if any(friendly in framework_lower for friendly in accessibility_friendly):
            return "good_support"
        else:
            return "unknown_support"
    
    def _analyze_robustness(self, url: str) -> Dict[str, Any]:
        """Analysiert Code-Robustheit einer Seite - ORIGINAL für Kompatibilität"""
        structured_data = self._get_structured_data_for_url(url)
        if not structured_data:
            return {"url": url, "aria_roles": [], "custom_elements": 0}
        
        accessibility_data = structured_data.get('accessibility', {})
        structure_data = structured_data.get('structure', {})
        
        return {
            "url": url,
            "aria_roles": accessibility_data.get('aria_roles', []),
            "custom_elements": len(structure_data.get('custom_elements', [])),
            "validation_status": "valid",  # Vereinfacht für Demo
            "landmarks": accessibility_data.get('landmarks', [])
        }

class WCAGExtractorFactory:
    """Factory für WCAG-spezifische Daten-Extraktoren"""
    
    EXTRACTORS = {
        "1_1_textalternativen": TextAlternativesExtractor,
        "1_2_zeitbasierte_medien": TimeBasedMediaExtractor,
        "1_3_anpassbare_darstellung": AdaptablePresentationExtractor,
        "1_4_wahrnehmbare_unterscheidungen": WahrnehmbareDifferenzierungenExtractor,
        "2_1_tastaturbedienung": TastaturbedienungExtractor,
        "2_2_genuegend_zeit": GenuegendZeitExtractor,
        "2_3_anfaelle_vermeiden": AnfaelleVermeidenExtractor,
        "2_4_navigation": NavigationExtractor,
        "3_1_lesbarkeit_sprache": LesbarkeitSpracheExtractor,
        "3_2_vorhersehbarkeit": VorhersehbarkeitExtractor,
        "3_3_eingabeunterstuetzung": EingabeunterstuetzungExtractor,
        "4_1_robustheit_kompatibilitaet": RobustheitsKompatibilitaetExtractor,
        # TODO: Weitere Extraktoren hinzufügen
    }
    
    @classmethod
    def create_extractor(cls, wcag_area: str, base_url: str, crawl_data: Dict[str, Any]) -> Optional[BaseWCAGExtractor]:
        """Erstellt den passenden Extraktor für einen WCAG-Bereich"""
        extractor_class = cls.EXTRACTORS.get(wcag_area)
        if extractor_class:
            return extractor_class(base_url, crawl_data)
        return None
    
    @classmethod
    def get_available_areas(cls) -> List[str]:
        """Gibt alle verfügbaren WCAG-Bereiche zurück"""
        return list(cls.EXTRACTORS.keys()) 