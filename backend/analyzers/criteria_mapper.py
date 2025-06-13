import logging
from typing import Dict, Any, List, Optional
import json

class CriteriaMapper:
    """
    Ordnet die gesammelten Daten den WCAG-Prüfkriterien zu.
    """
    
    def __init__(self):
        self.setup_logging()
        
    def setup_logging(self):
        """Konfiguriert das Logging für diese Klasse."""
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
    def _ensure_dict(self, obj: Any) -> bool:
        """Hilfsmethode: Prüft, ob ein Objekt ein Dictionary ist."""
        if not isinstance(obj, dict):
            self.logger.warning(f"Expected dict, got {type(obj)}")
            return False
        return True

    def map_data_to_criteria(self, crawler_data: Dict[str, Any], accessibility_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hauptmethode: Ordnet alle gesammelten Daten den WCAG-Prüfkriterien zu.
        
        Args:
            crawler_data: Daten vom Website-Crawler
            accessibility_results: Ergebnisse der Barrierefreiheitsprüfung
            
        Returns:
            Dict mit nach WCAG-Prinzipien strukturierten Daten
        """
        try:
            self.logger.info("Starte Zuordnung der Daten zu WCAG-Kriterien")
            
            mapped_data = {
                "perceivable": self._map_perceivable_criteria(crawler_data, accessibility_results),
                "operable": self._map_operable_criteria(crawler_data, accessibility_results),
                "understandable": self._map_understandable_criteria(crawler_data, accessibility_results),
                "robust": self._map_robust_criteria(crawler_data, accessibility_results),
                "summary": self._generate_summary(crawler_data, accessibility_results),
                "scores": self._calculate_scores(crawler_data, accessibility_results)
            }
            
            self.logger.info("Zuordnung zu WCAG-Kriterien erfolgreich abgeschlossen")
            return mapped_data
            
        except Exception as e:
            self.logger.error(f"Fehler bei der Zuordnung zu WCAG-Kriterien: {str(e)}")
            return {"error": f"Mapping failed: {str(e)}"}

    def _map_perceivable_criteria(self, crawler_data: Dict[str, Any], accessibility_results: Dict[str, Any]) -> Dict[str, Any]:
        """Ordnet Daten den 'Wahrnehmbar'-Kriterien zu."""
        return {
            "1.1_text_alternatives": {
                    "images": self._collect_image_data(crawler_data),
                    "aria_labels": self._collect_aria_labels(crawler_data),
                "complex_images": self._collect_complex_images(crawler_data)
            },
            "1.2_time_based_media": {
                "audio_content": self._collect_audio_content(crawler_data),
                "video_content": self._collect_video_content(crawler_data),
                "multimedia_alternatives": self._collect_multimedia_alternatives(crawler_data)
            },
            "1.3_adaptable": {
                "semantic_html": self._collect_semantic_html(crawler_data),
                "heading_structure": self._collect_heading_structure(crawler_data),
                "form_labels": self._collect_form_labels(crawler_data),
                "landmarks": self._collect_landmarks(crawler_data)
            },
            "1.4_distinguishable": {
                "color_contrast": self._collect_contrast_data(accessibility_results),
                "color_reliance": self._collect_color_reliance_data(accessibility_results),
                "text_scaling": self._collect_text_scaling_data(accessibility_results),
                "focus_indicators": self._collect_focus_indicators(crawler_data)
            }
        }

    def _map_operable_criteria(self, crawler_data: Dict[str, Any], accessibility_results: Dict[str, Any]) -> Dict[str, Any]:
        """Ordnet Daten den 'Bedienbar'-Kriterien zu."""
        return {
            "2.1_keyboard_accessible": {
                "keyboard_operability": self._collect_keyboard_operability_data(accessibility_results),
                "focus_order": self._collect_focus_order(crawler_data),
                "skip_links": self._collect_skip_links(crawler_data),
                "keyboard_traps": self._collect_keyboard_trap_data(accessibility_results)
            },
            "2.2_enough_time": {
                "time_limits": self._collect_time_limits_data(crawler_data),
                "moving_content": self._collect_moving_content_data(crawler_data)
            },
            "2.3_seizures": {
                "flashing_content": self._collect_flashing_content_data(crawler_data)
            },
            "2.4_navigable": {
                "page_titles": self._collect_page_titles(crawler_data),
                "link_texts": self._collect_link_texts(crawler_data),
                "heading_usage": self._collect_heading_usage(crawler_data),
                "focus_visible": self._collect_focus_visible_data(accessibility_results),
                "multiple_ways": self._collect_multiple_navigation_ways(crawler_data)
            }
        }

    def _map_understandable_criteria(self, crawler_data: Dict[str, Any], accessibility_results: Dict[str, Any]) -> Dict[str, Any]:
        """Ordnet Daten den 'Verständlich'-Kriterien zu."""
        return {
            "3.1_readable": {
                "language_declaration": self._collect_language_declaration(crawler_data),
                "language_changes": self._collect_language_changes(crawler_data)
            },
            "3.2_predictable": {
                "navigation_consistency": self._collect_navigation_consistency(crawler_data),
                "consistent_naming": self._collect_consistent_naming(crawler_data)
            },
            "3.3_input_assistance": {
                "error_identification": self._collect_error_identification(crawler_data),
                "error_description": self._collect_error_description(crawler_data),
                "help_suggestions": self._collect_help_suggestions(crawler_data)
            }
        }

    def _map_robust_criteria(self, crawler_data: Dict[str, Any], accessibility_results: Dict[str, Any]) -> Dict[str, Any]:
        """Ordnet Daten den 'Robust'-Kriterien zu."""
        return {
            "4.1_compatible": {
                "html_validation": self._collect_html_validation(crawler_data, accessibility_results),
                "aria_implementation": self._collect_aria_labels(crawler_data)
            }
        }
    
    # Sammelmethoden für spezifische Daten
    
    def _collect_focus_order(self, crawler_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sammelt Daten zur Fokus-Reihenfolge."""
        return {"message": "Focus order analysis not yet implemented"}
    
    def _collect_skip_links(self, crawler_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sammelt Skip-Links von allen Seiten."""
        skip_links = []
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content):
                    continue
                    
            links = page_content.get("structure", {}).get("links", [])
            if not isinstance(links, list):
                    continue
                
            for link in links:
                if not self._ensure_dict(link):
                        continue
                        
                href = link.get("href") or ""  # Sicherstellen, dass href niemals None ist
                text = str(link.get("text", "")).lower()
                
                # Erkenne Skip-Links
                if (href.startswith("#") and 
                    any(skip_word in text for skip_word in ["skip", "jump", "überspringen", "springe"])):
                    skip_links.append({
                        "page_url": page_url,
                        "text": link.get("text"),
                        "href": href,
                        "target": href[1:] if href.startswith("#") else None
                    })
        
        return skip_links
    
    def _collect_page_titles(self, crawler_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sammelt und analysiert Seitentitel."""
        titles_data = {"with_title": [], "without_title": [], "duplicate_titles": []}
        all_titles = {}
        
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content):
                    continue
                
            page_title = page_content.get("structure", {}).get("title")
            title_info = {"page_url": page_url, "title": page_title}
            
            if page_title and page_title.strip():
                if page_title in all_titles:
                    all_titles[page_title].append(page_url)
                else:
                    all_titles[page_title] = [page_url]
                titles_data["with_title"].append(title_info)
            else:
                titles_data["without_title"].append(title_info)
        
        # Finde doppelte Titel
        for title, urls in all_titles.items():
            if len(urls) > 1:
                titles_data["duplicate_titles"].append({"title": title, "pages": urls})
        
        return titles_data
    
    def _collect_image_data(self, crawler_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Sammelt Bilddaten von allen Seiten."""
        images_data = {"with_alt": [], "without_alt": [], "empty_alt": [], "decorative": []}
        
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content):
                    continue
                
            images = page_content.get("structure", {}).get("images", [])
            if not isinstance(images, list):
                    continue
                    
            for img in images:
                if not self._ensure_dict(img):
                    continue
                
                img_copy = img.copy()
                img_copy["page_url"] = page_url
                
                alt_text = img.get("alt")
                if alt_text is None:
                    images_data["without_alt"].append(img_copy)
                elif alt_text == "":
                    images_data["empty_alt"].append(img_copy)
                elif alt_text.strip():
                    images_data["with_alt"].append(img_copy)
                else:
                    images_data["decorative"].append(img_copy)
        
        return images_data
    
    def _collect_aria_labels(self, crawler_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Sammelt ARIA-Label-Daten."""
        aria_data = {"with_aria_label": [], "with_aria_labelledby": [], "with_aria_describedby": []}
        
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content):
                continue
                
            elements = page_content.get("structure", {}).get("all_elements", [])
            if not isinstance(elements, list):
                    continue
                
            for elem in elements:
                if not self._ensure_dict(elem):
                    continue
                    
                attrs = elem.get("attributes", {})
                if not isinstance(attrs, dict):
                        continue
                        
                elem_copy = elem.copy()
                elem_copy["page_url"] = page_url
                
                if "aria-label" in attrs:
                    aria_data["with_aria_label"].append(elem_copy)
                if "aria-labelledby" in attrs:
                    aria_data["with_aria_labelledby"].append(elem_copy)
                if "aria-describedby" in attrs:
                    aria_data["with_aria_describedby"].append(elem_copy)
        
        return aria_data
    
    def _collect_form_labels(self, crawler_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Sammelt Formularlabel-Daten."""
        form_data = {"labeled_inputs": [], "unlabeled_inputs": [], "labels": []}
        
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content):
                continue
                
            forms = page_content.get("structure", {}).get("forms", [])
            if not isinstance(forms, list):
                continue
            
            for form in forms:
                if not self._ensure_dict(form):
                    continue
                    
                inputs = form.get("inputs", [])
                labels = form.get("labels", [])
                
                # Sammle Labels
                for label in labels:
                    if isinstance(label, dict):
                        label_copy = label.copy()
                        label_copy["page_url"] = page_url
                        form_data["labels"].append(label_copy)
                
                # Sammle Inputs und prüfe Labels
                for input_elem in inputs:
                    if isinstance(input_elem, dict):
                        input_copy = input_elem.copy()
                        input_copy["page_url"] = page_url
                        
                        # Prüfe verschiedene Label-Methoden
                        has_label = (
                            input_elem.get("attributes", {}).get("aria-label") or
                            input_elem.get("attributes", {}).get("aria-labelledby") or
                            input_elem.get("label_text") or
                            input_elem.get("placeholder")
                        )
                        
                        if has_label:
                            form_data["labeled_inputs"].append(input_copy)
                    else:
                            form_data["unlabeled_inputs"].append(input_copy)
        
        return form_data
    
    def _collect_complex_images(self, crawler_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sammelt komplexe Bilder (Charts, Diagramme, etc.)."""
        complex_images = []
        complex_indicators = ["chart", "graph", "diagram", "infographic", "data", "statistics"]
        
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content):
                    continue
                    
            images = page_content.get("structure", {}).get("images", [])
            if not isinstance(images, list):
                    continue
                    
            for img in images:
                if not self._ensure_dict(img):
                    continue
                    
                # Prüfe auf Indikatoren für komplexe Bilder
                src = str(img.get("src", "")).lower()
                alt = str(img.get("alt", "")).lower()
                
                if any(indicator in src or indicator in alt for indicator in complex_indicators):
                    img_copy = img.copy()
                    img_copy["page_url"] = page_url
                    img_copy["complexity_reason"] = "Detected complex content indicators"
                    complex_images.append(img_copy)
        
        return complex_images
    
    def _collect_landmarks(self, crawler_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sammelt Landmark-Daten."""
        landmarks_data = []
        
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content):
                continue
                
            landmarks = page_content.get("structure", {}).get("landmarks", [])
            if isinstance(landmarks, list):
                for landmark in landmarks:
                    if isinstance(landmark, dict):
                        landmark_copy = landmark.copy()
                        landmark_copy["page_url"] = page_url
                        landmarks_data.append(landmark_copy)
        
        return landmarks_data
    
    def _collect_language_declaration(self, crawler_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sammelt Sprachdeklarationen."""
        lang_data = {"pages_language_declaration": [], "text_language_changes": []}
        
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content):
                        continue
                        
            html_attrs = page_content.get("structure", {}).get("html_attributes", {})
            main_lang = html_attrs.get("lang") if isinstance(html_attrs, dict) else None
            
            lang_data["pages_language_declaration"].append({
                "page_url": page_url,
                "declared_lang": main_lang if main_lang else "Not declared"
            })
        
        return lang_data
    
    def _collect_html_validation(self, crawler_data: Dict[str, Any], accessibility_results: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Sammelt HTML-Validierungsdaten."""
        validation_issues = {"doctype_issues": [], "encoding_issues": [], "parsing_errors": []}
        
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content):
                        continue
                        
            structure = page_content.get("structure", {})
            if not self._ensure_dict(structure):
                        continue
                        
            if not structure.get("doctype_present"):
                validation_issues["doctype_issues"].append({
                    "page_url": page_url,
                    "issue": "Doctype missing or not detected"
                })
                
            if not structure.get("charset_declared"):
                validation_issues["encoding_issues"].append({
                    "page_url": page_url,
                    "issue": "Character encoding not declared"
                })
        
        return validation_issues
    
    # Hilfsmethoden für Accessibility-Daten
    
    def _collect_color_reliance_data(self, accessibility_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sammelt Daten zur alleinigen Farbnutzung."""
        color_issues = []
        for violation in accessibility_results.get("violations", []):
            if violation.get("id") == "use-of-color":
                color_issues.append(violation)
        return color_issues
    
    def _collect_contrast_data(self, accessibility_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sammelt Kontrastdaten."""
        contrast_issues = []
        for violation in accessibility_results.get("violations", []):
            if violation.get("id") == "color-contrast":
                contrast_issues.extend(violation.get("nodes", []))
        return contrast_issues
    
    def _collect_keyboard_operability_data(self, accessibility_results: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Sammelt Tastaturbedienbarkeits-Daten."""
        keyboard_data = {"violations": [], "warnings": []}
        
        keyboard_ids = ["keyboard", "focus-order", "no-keyboard-trap", "button-name", "link-name"]
        
        for violation in accessibility_results.get("violations", []):
            if violation.get("id") in keyboard_ids:
                keyboard_data["violations"].append(violation)
        
        return keyboard_data
    
    def _collect_focus_visible_data(self, accessibility_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sammelt Daten zur Fokus-Sichtbarkeit."""
        focus_issues = []
        focus_ids = ["focus-visible", "focus-order"]
        
        for violation in accessibility_results.get("violations", []):
            if violation.get("id") in focus_ids:
                focus_issues.append(violation)
        
        return focus_issues
    
    # Weitere Sammelmethoden (vereinfacht)
    
    def _collect_audio_content(self, crawler_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sammelt Audio-Inhalte."""
        return []  # Vereinfachte Implementierung
    
    def _collect_video_content(self, crawler_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sammelt Video-Inhalte."""
        return []  # Vereinfachte Implementierung
    
    def _collect_multimedia_alternatives(self, crawler_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sammelt Multimedia-Alternativen."""
        return []  # Vereinfachte Implementierung
    
    def _collect_semantic_html(self, crawler_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Sammelt semantische HTML-Daten."""
        return {"semantic_elements": [], "non_semantic_usage": []}  # Vereinfachte Implementierung
    
    def _collect_heading_structure(self, crawler_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Sammelt Überschriftenstruktur."""
        heading_data = {"headings": [], "structure_violations": []}
        
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content):
                continue
                
            headings = page_content.get("structure", {}).get("headings", [])
            if isinstance(headings, list):
                for heading in headings:
                    if isinstance(heading, dict):
                        heading_copy = heading.copy()
                        heading_copy["page_url"] = page_url
                        heading_data["headings"].append(heading_copy)
        
        return heading_data
    
    def _collect_text_scaling_data(self, accessibility_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sammelt Text-Skalierungsdaten."""
        return []  # Vereinfachte Implementierung
    
    def _collect_focus_indicators(self, crawler_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sammelt Fokus-Indikatoren."""
        return []  # Vereinfachte Implementierung
    
    def _collect_time_limits_data(self, crawler_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sammelt Zeitlimit-Daten."""
        return []  # Vereinfachte Implementierung
    
    def _collect_moving_content_data(self, crawler_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sammelt bewegte Inhalte."""
        return []  # Vereinfachte Implementierung
    
    def _collect_flashing_content_data(self, crawler_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sammelt blinkende Inhalte."""
        return []  # Vereinfachte Implementierung
    
    def _collect_link_texts(self, crawler_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Sammelt Link-Texte."""
        link_data = {"descriptive_links": [], "non_descriptive_links": []}
        non_descriptive_patterns = ["click here", "more", "read more", "hier klicken", "mehr"]
        
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content):
                    continue
                    
            links = page_content.get("structure", {}).get("links", [])
            if not isinstance(links, list):
                    continue
                    
            for link in links:
                if not self._ensure_dict(link):
                    continue
                    
                link_copy = link.copy()
                link_copy["page_url"] = page_url
                text = str(link.get("text", "")).lower().strip()
                
                if any(pattern in text for pattern in non_descriptive_patterns) or len(text) < 4:
                    link_data["non_descriptive_links"].append(link_copy)
                else:
                    link_data["descriptive_links"].append(link_copy)
        
        return link_data
    
    def _collect_heading_usage(self, crawler_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Sammelt Überschriften-Nutzung."""
        return {"proper_hierarchy": [], "hierarchy_violations": []}  # Vereinfachte Implementierung
    
    def _collect_multiple_navigation_ways(self, crawler_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Sammelt multiple Navigationswege."""
        return {"navigation_menus": [], "search_functions": [], "sitemaps": []}  # Vereinfachte Implementierung
    
    def _collect_keyboard_trap_data(self, accessibility_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sammelt Keyboard-Trap-Daten."""
        return []  # Vereinfachte Implementierung
    
    def _collect_language_changes(self, crawler_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sammelt Sprachwechsel."""
        return []  # Vereinfachte Implementierung
    
    def _collect_navigation_consistency(self, crawler_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sammelt Navigationskonsistenz."""
        return {"consistent_navs": [], "inconsistent_navs": []}  # Vereinfachte Implementierung
    
    def _collect_consistent_naming(self, crawler_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Sammelt konsistente Benennung."""
        return {"consistent_elements": [], "inconsistent_elements": []}  # Vereinfachte Implementierung
    
    def _collect_error_identification(self, crawler_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sammelt Fehleridentifikation."""
        return []  # Vereinfachte Implementierung
    
    def _collect_error_description(self, crawler_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sammelt Fehlerbeschreibungen."""
        return []  # Vereinfachte Implementierung
    
    def _collect_help_suggestions(self, crawler_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sammelt Hilfevorschläge."""
        return []  # Vereinfachte Implementierung
    
    def _generate_summary(self, crawler_data: Dict[str, Any], accessibility_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generiert eine Zusammenfassung."""
        return {"message": "Summary generation not yet implemented."}
    
    def _calculate_scores(self, crawler_data: Dict[str, Any], accessibility_results: Dict[str, Any]) -> Dict[str, float]:
        """Berechnet WCAG-Scores."""
        return {
            "perceivable": 0.0,
            "operable": 0.0,
            "understandable": 0.0,
            "robust": 0.0,
            "overall": 0.0
        } 