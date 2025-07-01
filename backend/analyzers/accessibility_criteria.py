from typing import Dict, List, Any
import logging
import re
from bs4 import BeautifulSoup
import requests
import json
import traceback

class AccessibilityCriteria:
    def __init__(self):
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def categorize_results(self, crawler_data: Dict[str, Any], accessibility_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kategorisiert die Analyseergebnisse nach WCAG 2.1 Richtlinien und Konformitätsstufen
        """
        try:
            # Detailliertes Logging der Eingabedaten
            self.logger.debug(f"categorize_results - crawler_data TYP: {type(crawler_data)}")
            # self.logger.debug(f"categorize_results - crawler_data Inhalt: {json.dumps(crawler_data, indent=2, ensure_ascii=False)}") # Kann sehr lang sein
            self.logger.debug(f"categorize_results - accessibility_results TYP: {type(accessibility_results)}")
            # self.logger.debug(f"categorize_results - accessibility_results Inhalt: {json.dumps(accessibility_results, indent=2, ensure_ascii=False)}") # Kann sehr lang sein

            categorized = {
                "perceivable": self._analyze_perceivable(crawler_data, accessibility_results),
                "operable": self._analyze_operable(crawler_data, accessibility_results),
                "understandable": self._analyze_understandable(crawler_data, accessibility_results),
                "robust": self._analyze_robust(crawler_data, accessibility_results)
            }
            
            # Kategorisiere nach Konformitätsstufen
            conformance_levels = self._categorize_by_conformance_level(categorized)
            
            return {
                "wcag_categories": categorized,
                "conformance_levels": conformance_levels
            }
        except Exception as e:
            self.logger.error(f"Fehler bei der Kategorisierung: {str(e)}")
            self.logger.error(traceback.format_exc()) # Traceback hinzugefügt
            return {"error": str(e), "traceback": traceback.format_exc()}

    def _analyze_perceivable(self, crawler_data: Dict[str, Any], accessibility_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        1. Wahrnehmbar - Informationen und Benutzeroberflächen müssen wahrnehmbar präsentiert werden
        """
        self.logger.debug(f"_analyze_perceivable - crawler_data TYP: {type(crawler_data)}")
        self.logger.debug(f"_analyze_perceivable - accessibility_results TYP: {type(accessibility_results)}")
        results = {
            "text_alternatives": {
                "images_without_alt": [],
                "decorative_images": [],
                "complex_images": [],
                "captcha_alternatives": [],
                "image_purpose": []  # Unterscheidung zwischen Layout und Information
            },
            "time_based_media": {
                "videos_without_captions": [],
                "audio_without_transcripts": [],
                "video_descriptions": [],
                "live_media": [],
                "audio_description": []
            },
            "adaptable": {
                "content_structure": [],
                "meaningful_sequence": [],
                "orientation": [],  # Bildschirmausrichtung
                "input_purpose": [],  # Zweck der Eingabe
                "responsive_design": []
            },
            "distinguishable": {
                "color_contrast": [],
                "text_resize": [],
                "images_of_text": [],
                "reflow": [],  # Umbruch bei Zoom
                "non_text_contrast": [],  # Kontrast für UI-Elemente
                "text_spacing": [],  # Textabstände
                "hover_focus_content": []  # Inhalte bei Hover/Fokus
            }
        }

        for url, page_data in crawler_data.get("data", {}).items():
            # Erweiterte Bildanalyse
            for image in page_data.get("structure", {}).get("images", []):
                self._analyze_image(image, url, results)

            # Erweiterte Multimedia-Analyse
            multimedia = page_data.get("structure", {}).get("multimedia", {})
            self._analyze_multimedia(multimedia, url, results)

            # Erweiterte Strukturanalyse
            structure = page_data.get("structure", {})
            self._analyze_structure(structure, url, results)

            # Responsive Design Prüfung
            styling = page_data.get("styling", {})
            self._analyze_responsive_design(styling, url, results)

        return results

    def _analyze_operable(self, crawler_data: Dict[str, Any], accessibility_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        2. Bedienbar - Benutzeroberflächen und Navigation müssen bedienbar sein
        """
        results = {
            "keyboard_accessible": {
                "keyboard_traps": [],
                "focus_order": [],
                "single_char_shortcuts": [],  # Einzelzeichen-Tastenkombinationen
                "keyboard_triggers": []  # Tastaturauslöser
            },
            "timing": {
                "adjustable_timing": [],
                "pause_stop_hide": [],
                "timeout_warnings": [],  # Warnungen vor Zeitablauf
                "re_authenticating": []  # Neu-Authentifizierung
            },
            "seizures_physical": {  # Anfälle und physische Reaktionen
                "flash_threshold": [],
                "animation_from_interactions": [],
                "motion_actuation": []
            },
            "navigable": {
                "skip_links": [],
                "page_titles": [],
                "focus_order": [],
                "link_purpose": [],
                "multiple_ways": [],  # Mehrere Navigationswege
                "headings_labels": [],  # Überschriften und Beschriftungen
                "focus_visible": []  # Sichtbarer Fokus
            },
            "input_modalities": {
                "pointer_gestures": [],
                "pointer_cancellation": [],
                "label_in_name": [],
                "motion_actuation": []
            }
        }

        for url, page_data in crawler_data.get("data", {}).items():
            # Erweiterte Tastaturzugänglichkeit
            self._analyze_keyboard_accessibility(page_data, url, results)

            # Erweiterte Zeitsteuerung
            self._analyze_timing(page_data, url, results)

            # Erweiterte Navigation
            self._analyze_navigation(page_data, url, results)

            # Erweiterte Eingabemodalitäten
            self._analyze_input_modalities(page_data, url, results)

        return results

    def _analyze_understandable(self, crawler_data: Dict[str, Any], accessibility_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        3. Verständlich - Informationen und Bedienung müssen verständlich sein
        """
        results = {
            "readable": {
                "language_detection": [],
                "language_parts": [],  # Sprache von Teilen
                "unusual_words": [],
                "abbreviations": [],
                "reading_level": [],  # Leseniveau
                "pronunciation": []  # Aussprache
            },
            "predictable": {
                "on_focus": [],
                "on_input": [],
                "consistent_navigation": [],
                "consistent_identification": [],
                "change_on_request": []  # Änderungen auf Anfrage
            },
            "input_assistance": {
                "error_identification": [],
                "labels_instructions": [],
                "error_suggestion": [],
                "error_prevention": [],
                "help_available": [],  # Verfügbare Hilfe
                "error_prevention_all": []  # Fehlervermeidung (rechtlich)
            }
        }

        for url, page_data in crawler_data.get("data", {}).items():
            # Erweiterte Sprachanalyse
            self._analyze_language(page_data, url, results)

            # Erweiterte Vorhersehbarkeitsanalyse
            self._analyze_predictability(page_data, url, results)

            # Erweiterte Eingabehilfen
            self._analyze_input_assistance(page_data, url, results)

        return results

    def _analyze_robust(self, crawler_data: Dict[str, Any], accessibility_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        4. Robust - Inhalte müssen robust genug sein für verschiedene User Agents
        """
        results = {
            "compatible": {
                "parsing": [],  # Code-Validierung
                "name_role_value": [],  # Name, Rolle, Wert
                "status_messages": []  # Statusmeldungen
            },
            "html_validation": {
                "doctype": [],
                "encoding": [],
                "valid_tags": [],
                "valid_attributes": []
            },
            "aria_implementation": {
                "landmarks": [],
                "roles": [],
                "properties": [],
                "states": [],
                "relationships": []
            }
        }

        for url, page_data in crawler_data.get("data", {}).items():
            # HTML-Validierung
            self._analyze_html_validation(page_data, url, results)

            # ARIA-Implementierung
            self._analyze_aria(page_data, url, results)

            # Kompatibilitätsprüfung
            self._analyze_compatibility(page_data, url, results)

        return results

    def _categorize_by_conformance_level(self, categorized_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kategorisiert die Ergebnisse nach den Konformitätsstufen A, AA und AAA
        """
        return {
            "level_a": self._filter_level_a_criteria(categorized_results),
            "level_aa": self._filter_level_aa_criteria(categorized_results),
            "level_aaa": self._filter_level_aaa_criteria(categorized_results)
        }

    # Hilfsmethoden für die detaillierte Analyse
    def _analyze_image(self, image: Dict[str, Any], url: str, results: Dict[str, Any]):
        """Erweiterte Bildanalyse"""
        if not isinstance(image, dict):
            self.logger.warning(f"_analyze_image - unerwarteter Bildtyp: {type(image)} für Bild: {image}")
            return

        if not image.get("alt"):
            results["text_alternatives"]["images_without_alt"].append({
                "url": url,
                "image": image
            })
        
        # Prüfe auf dekorative Bilder
        if image.get("role") == "presentation" or image.get("alt") == "":
            results["text_alternatives"]["decorative_images"].append({
                "url": url,
                "image": image
            })

        # Prüfe auf komplexe Bilder
        # Stelle sicher, dass width und height als Integer behandelt werden
        try:
            width = int(image.get("width", 0)) if image.get("width") else 0
            height = int(image.get("height", 0)) if image.get("height") else 0
            is_large_image = width * height > 100000
        except (ValueError, TypeError):
            self.logger.warning(f"_analyze_image - ungültige Bildgröße: width={image.get('width')}, height={image.get('height')}")
            is_large_image = False
            
        if image.get("complex") or is_large_image:
            results["text_alternatives"]["complex_images"].append({
                "url": url,
                "image": image
            })

    def _analyze_multimedia(self, multimedia: Dict[str, Any], url: str, results: Dict[str, Any]):
        """Erweiterte Multimedia-Analyse"""
        for video in multimedia.get("video", []):
            if isinstance(video, dict):
                if not video.get("captions"):
                    results["time_based_media"]["videos_without_captions"].append({
                        "url": url,
                        "video": video
                    })
                if not video.get("description"):
                    results["time_based_media"]["video_descriptions"].append({
                        "url": url,
                        "video": video
                    })

        for audio in multimedia.get("audio", []):
            if isinstance(audio, dict):
                if not audio.get("transcript"):
                    results["time_based_media"]["audio_without_transcripts"].append({
                        "url": url,
                        "audio": audio
                    })

    def _analyze_structure(self, structure: Dict[str, Any], url: str, results: Dict[str, Any]):
        """Erweiterte Strukturanalyse"""
        results["adaptable"]["content_structure"].append({
            "url": url,
            "headings": structure.get("headings", []),
            "landmarks": structure.get("landmarks", []),
            "lists": structure.get("lists", []),
            "tables": structure.get("tables", [])
        })

    def _analyze_responsive_design(self, styling: Dict[str, Any], url: str, results: Dict[str, Any]):
        """Analyse des responsiven Designs"""
        if styling.get("viewport"):
            results["adaptable"]["responsive_design"].append({
                "url": url,
                "viewport": styling["viewport"],
                "media_queries": styling.get("media_queries", []),
                "flexible_images": styling.get("responsive_images", 0)
            })

    def _analyze_keyboard_accessibility(self, page_data: Dict[str, Any], url: str, results: Dict[str, Any]):
        """Analyse der Tastaturzugänglichkeit"""
        self.logger.debug(f"_analyze_keyboard_accessibility - page_data TYP: {type(page_data)}")
        interactive_elements_data = page_data.get("structure", {}).get("interactive_elements", [])
        self.logger.debug(f"_analyze_keyboard_accessibility - interactive_elements_data TYP: {type(interactive_elements_data)}")
        self.logger.debug(f"_analyze_keyboard_accessibility - interactive_elements_data Inhalt: {json.dumps(interactive_elements_data, indent=2, ensure_ascii=False)}")

        # Prüfe auf Tastaturfallen
        # Stellen sicher, dass wir über die richtigen Listen von Elementen iterieren
        all_interactive_elements = []
        if isinstance(interactive_elements_data, dict):
            if isinstance(interactive_elements_data.get("buttons"), list):
                all_interactive_elements.extend(interactive_elements_data.get("buttons", []))
            if isinstance(interactive_elements_data.get("inputs"), list):
                all_interactive_elements.extend(interactive_elements_data.get("inputs", []))
            # Fügen Sie hier weitere Typen hinzu, falls nötig (custom_controls, dialogs, tooltips)
            if isinstance(interactive_elements_data.get("custom_controls"), list):
                all_interactive_elements.extend(interactive_elements_data.get("custom_controls", []))
            if isinstance(interactive_elements_data.get("dialogs"), list):
                all_interactive_elements.extend(interactive_elements_data.get("dialogs", []))
            if isinstance(interactive_elements_data.get("tooltips"), list): # Tooltips sind unwahrscheinlich für tabindex, aber zur Vollständigkeit
                all_interactive_elements.extend(interactive_elements_data.get("tooltips", []))
        elif isinstance(interactive_elements_data, list): # Fallback, falls es doch eine flache Liste ist
            all_interactive_elements = interactive_elements_data

        for element in all_interactive_elements:
            self.logger.debug(f"_analyze_keyboard_accessibility - aktuelles element TYP: {type(element)}")
            self.logger.debug(f"_analyze_keyboard_accessibility - aktuelles element Inhalt: {json.dumps(element, indent=2, ensure_ascii=False)}")
            if isinstance(element, dict):
                if element.get("tabindex") == "-1" or element.get("disabled"):
                    results["keyboard_accessible"]["keyboard_traps"].append({
                        "url": url,
                        "element": element
                    })
            else:
                self.logger.warning(f"_analyze_keyboard_accessibility - unerwarteter Elementtyp: {type(element)} für Element: {element}")

        # Prüfe Fokusreihenfolge
        # Ähnliche Logik für focusable_elements anwenden, wenn nötig
        focusable_elements_raw = page_data.get("structure", {}).get("interactive_elements", [])
        actual_focusable_elements = []
        if isinstance(focusable_elements_raw, dict):
            if isinstance(focusable_elements_raw.get("buttons"), list):
                actual_focusable_elements.extend(focusable_elements_raw.get("buttons", []))
            if isinstance(focusable_elements_raw.get("inputs"), list):
                actual_focusable_elements.extend(focusable_elements_raw.get("inputs", []))
            # Fügen Sie hier weitere Typen hinzu, falls nötig
        elif isinstance(focusable_elements_raw, list):
            actual_focusable_elements = focusable_elements_raw
        
        # Filtert Elemente heraus, die keine Dictionaries sind oder keinen tabindex haben
        valid_focusable_elements = [el for el in actual_focusable_elements if isinstance(el, dict) and el.get("tabindex") is not None]
        
        focusable_elements = sorted(
            valid_focusable_elements,
            key=lambda x: int(x.get("tabindex")) if str(x.get("tabindex")).lstrip('-').isdigit() else 0 # Stellt sicher, dass tabindex eine Zahl ist
        )
        results["keyboard_accessible"]["focus_order"].append({
            "url": url,
            "elements": focusable_elements
        })

    def _analyze_timing(self, page_data: Dict[str, Any], url: str, results: Dict[str, Any]):
        """Analyse der Zeitsteuerung"""
        # Prüfe auf Zeitlimits
        for script in page_data.get("structure", {}).get("scripts", []):
            if "setTimeout" in script.get("content", "") or "setInterval" in script.get("content", ""):
                results["timing"]["adjustable_timing"].append({
                    "url": url,
                    "script": script
                })

        # Prüfe auf automatische Aktualisierungen
        meta_refresh = page_data.get("structure", {}).get("meta_refresh")
        if meta_refresh:
            results["timing"]["pause_stop_hide"].append({
                "url": url,
                "refresh": meta_refresh
            })

    def _analyze_navigation(self, page_data: Dict[str, Any], url: str, results: Dict[str, Any]):
        """Analyse der Navigation"""
        # Prüfe Seitentitel
        title = page_data.get("title", {}).get("page_title")
        if not title:
            results["navigable"]["page_titles"].append({
                "url": url,
                "title": None
            })

        # Prüfe Links
        for link in page_data.get("structure", {}).get("links", []):
            if isinstance(link, dict):
                if not link.get("text") and not link.get("aria_label"):
                    results["navigable"]["link_purpose"].append({
                        "url": url,
                        "link": link
                    })

        # Prüfe Navigationswege
        navigation_methods = []
        if page_data.get("structure", {}).get("navigation"):
            navigation_methods.append("main_nav")
        if page_data.get("structure", {}).get("search"):
            navigation_methods.append("search")
        if page_data.get("structure", {}).get("sitemap"):
            navigation_methods.append("sitemap")

        results["navigable"]["multiple_ways"].append({
            "url": url,
            "available_methods": navigation_methods
        })

    def _analyze_input_modalities(self, page_data: Dict[str, Any], url: str, results: Dict[str, Any]):
        """Analyse der Eingabemodalitäten"""
        # Prüfe Zeigergesten
        for element in page_data.get("structure", {}).get("interactive_elements", []):
            if isinstance(element, dict) and element.get("event_handlers", {}).get("gesture"):
                results["input_modalities"]["pointer_gestures"].append({
                    "url": url,
                    "element": element
                })

        # Prüfe Bezeichnungen in Namen
        for element in page_data.get("structure", {}).get("interactive_elements", []):
            if isinstance(element, dict):
                visible_label = element.get("text", "")
                aria_label = element.get("aria_label", "")
                if visible_label and aria_label and visible_label not in aria_label:
                    results["input_modalities"]["label_in_name"].append({
                        "url": url,
                        "element": element,
                        "visible_label": visible_label,
                        "aria_label": aria_label
                    })

    def _analyze_language(self, page_data: Dict[str, Any], url: str, results: Dict[str, Any]):
        """Analyse der Sprache"""
        # Prüfe Hauptsprache
        language = page_data.get("accessibility", {}).get("language", {})
        if not language.get("main_language"):
            results["readable"]["language_detection"].append({
                "url": url,
                "language": None
            })

        # Prüfe Sprachwechsel
        for element in page_data.get("structure", {}).get("text_elements", []):
            if isinstance(element, dict) and element.get("lang") and element.get("lang") != language.get("main_language"):
                results["readable"]["language_parts"].append({
                    "url": url,
                    "element": element
                })

    def _analyze_predictability(self, page_data: Dict[str, Any], url: str, results: Dict[str, Any]):
        """Analyse der Vorhersehbarkeit"""
        # Prüfe Fokusverhalten
        for element in page_data.get("structure", {}).get("interactive_elements", []):
            if isinstance(element, dict) and element.get("event_handlers", {}).get("focus"):
                results["predictable"]["on_focus"].append({
                    "url": url,
                    "element": element
                })

        # Prüfe Eingabeverhalten
        for form in page_data.get("structure", {}).get("forms", []):
            if isinstance(form, dict):
                for field in form.get("fields", []):
                    if isinstance(field, dict) and field.get("event_handlers", {}).get("input"):
                        results["predictable"]["on_input"].append({
                            "url": url,
                            "field": field
                        })

    def _analyze_input_assistance(self, page_data: Dict[str, Any], url: str, results: Dict[str, Any]):
        """Analyse der Eingabehilfen"""
        # Prüfe Formularbeschriftungen
        for form in page_data.get("structure", {}).get("forms", []):
            if isinstance(form, dict):
                for field in form.get("fields", []):
                    if isinstance(field, dict):
                        if not field.get("label") and not field.get("aria_label"):
                            results["input_assistance"]["labels_instructions"].append({
                                "url": url,
                                "field": field
                            })

        # Prüfe Fehlermeldungen
        for form in page_data.get("structure", {}).get("forms", []):
            if isinstance(form, dict):
                if not form.get("error_handling"):
                    results["input_assistance"]["error_identification"].append({
                        "url": url,
                        "form": form
                    })

    def _analyze_html_validation(self, page_data: Dict[str, Any], url: str, results: Dict[str, Any]):
        """Analyse der HTML-Validität"""
        # Prüfe Doctype
        if not page_data.get("structure", {}).get("doctype"):
            results["html_validation"]["doctype"].append({
                "url": url,
                "message": "Kein Doctype gefunden"
            })

        # Prüfe Encoding
        if not page_data.get("structure", {}).get("charset"):
            results["html_validation"]["encoding"].append({
                "url": url,
                "message": "Keine Zeichenkodierung angegeben"
            })

    def _analyze_aria(self, page_data: Dict[str, Any], url: str, results: Dict[str, Any]):
        """Analyse der ARIA-Implementierung"""
        # Prüfe Landmarks
        for landmark in page_data.get("accessibility", {}).get("aria_roles", []):
            if isinstance(landmark, dict) and landmark.get("role") in ["main", "navigation", "banner", "contentinfo"]:
                results["aria_implementation"]["landmarks"].append({
                    "url": url,
                    "landmark": landmark
                })

        # Prüfe ARIA-Rollen
        for element in page_data.get("structure", {}).get("interactive_elements", []):
            if isinstance(element, dict) and element.get("role") and not element.get("aria_label"):
                results["aria_implementation"]["roles"].append({
                    "url": url,
                    "element": element
                })

    def _analyze_compatibility(self, page_data: Dict[str, Any], url: str, results: Dict[str, Any]):
        """Analyse der Kompatibilität"""
        # Prüfe Statusmeldungen
        for message in page_data.get("structure", {}).get("status_messages", []):
            if isinstance(message, dict):
                if not message.get("role") in ["status", "alert", "log"]:
                    results["compatible"]["status_messages"].append({
                        "url": url,
                        "message": message
                    })

    def _filter_level_a_criteria(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Filtert Level A Kriterien"""
        return {
            "text_alternatives": results["perceivable"]["text_alternatives"],
            "keyboard_access": results["operable"]["keyboard_accessible"],
            "timing": results["operable"]["timing"],
            "seizures": results["operable"]["seizures_physical"],
            "navigable": results["operable"]["navigable"],
            "readable": results["understandable"]["readable"],
            "predictable": results["understandable"]["predictable"],
            "compatible": results["robust"]["compatible"]
        }

    def _filter_level_aa_criteria(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Filtert Level AA Kriterien"""
        return {
            "captions": results["perceivable"]["time_based_media"],
            "contrast": results["perceivable"]["distinguishable"],
            "resize": results["perceivable"]["distinguishable"],
            "multiple_ways": results["operable"]["navigable"],
            "language_parts": results["understandable"]["readable"],
            "error_suggestion": results["understandable"]["input_assistance"]
        }

    def _filter_level_aaa_criteria(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Filtert Level AAA Kriterien"""
        return {
            "sign_language": results["perceivable"]["time_based_media"],
            "extended_audio": results["perceivable"]["time_based_media"],
            "contrast_enhanced": results["perceivable"]["distinguishable"],
            "low_background": results["perceivable"]["distinguishable"],
            "sign_language": results["perceivable"]["time_based_media"],
            "location": results["operable"]["navigable"],
            "unusual_words": results["understandable"]["readable"],
            "abbreviations": results["understandable"]["readable"],
            "reading_level": results["understandable"]["readable"],
            "pronunciation": results["understandable"]["readable"]
        }

    # Weitere Hilfsmethoden für die anderen Analysen...
    # [Hier würden die weiteren Implementierungen der Hilfsmethoden folgen] 