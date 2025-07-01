from typing import Dict, List, Any
import logging
import re
import traceback

class CriteriaMapper:
    def __init__(self):
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def _ensure_dict(self, obj: Any) -> bool:
        """Stellt sicher, dass ein Objekt ein Dictionary ist"""
        if not isinstance(obj, dict):
            self.logger.warning(f"Unerwarteter Typ: {type(obj)} für Objekt: {str(obj)[:30]}...")
            return False
        return True

    def map_data_to_criteria(self, crawler_data: Dict[str, Any], accessibility_results: Dict[str, Any]) -> Dict[str, Any]:
        """Ordnet die extrahierten Daten den WCAG-Prüfkriterien zu"""
        try:
            crawler_data_copy = crawler_data.copy()
            accessibility_results_copy = accessibility_results.copy() # Auch accessibility_results kopieren
            
            mapped_data = {
                "1_wahrnehmbar": self._map_perceivable_criteria(crawler_data_copy, accessibility_results_copy),
                "2_bedienbar": self._map_operable_criteria(crawler_data_copy, accessibility_results_copy),
                "3_verständlich": self._map_understandable_criteria(crawler_data_copy, accessibility_results_copy),
                "4_robust": self._map_robust_criteria(crawler_data_copy, accessibility_results_copy),
                "summary": self._generate_summary(crawler_data_copy, accessibility_results_copy),
                "scores": self._calculate_scores(crawler_data_copy, accessibility_results_copy)
            }
            
            return mapped_data
        except Exception as e:
            self.logger.error(f"Fehler bei der Zuordnung: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                "error": str(e),
                "type": "mapping_error"
            }

    def _map_perceivable_criteria(self, crawler_data: Dict[str, Any], accessibility_results: Dict[str, Any]) -> Dict[str, Any]:
        perceivable_data = {
            "1.1_text_alternatives": {
                "1.1.1_nicht_text_inhalte": {
                    "images": self._collect_image_data(crawler_data),
                    "aria_labels_general": self._collect_aria_labels(crawler_data), # Umbenannt für Klarheit
                    "form_element_labels": self._collect_form_labels(crawler_data), # Umbenannt für Klarheit
                    "complex_images_description": self._collect_complex_images(crawler_data), # Umbenannt
                    "captcha_alternatives": self._collect_captcha_data(crawler_data) # Umbenannt
                }
            },
            "1.2_zeitbasierte_medien": {
                "1.2.1_audio_transkripte": self._collect_audio_content(crawler_data),
                "1.2.2_video_untertitel": self._collect_video_content(crawler_data),
                "1.2.3_audiodeskription": self._collect_multimedia_alternatives(crawler_data)
            },
            "1.3_anpassbare_darstellung": {
                "1.3.1_html_strukturelemente": self._collect_semantic_html(crawler_data),
                "1.3.2_ueberschriften_hierarchie": self._collect_heading_structure(crawler_data),
                "1.3.3_konsistente_layouts": self._collect_layout_consistency(crawler_data),
                "1.3.4_inhalts_reihenfolge": self._collect_content_order(crawler_data),
                "1.3.5_formular_zuordnungen": self._collect_form_labels(crawler_data)
            },
            "1.4_unterscheidbar": {
                 "1.4.1_farben_allein": self._collect_color_reliance_data(accessibility_results),
                 "1.4.2_ausreichende_kontraste": self._collect_contrast_data(accessibility_results),
                 "1.4.3_anpassbare_textgroesse": self._collect_text_scaling_data(accessibility_results),
                 "1.4.4_textanpassungen_moeglich": self._collect_text_customization_data(accessibility_results),
                 "1.4.5_grafik_kontraste": self._collect_graphic_contrast_data(accessibility_results),
                 "1.4.6_fokus_hinweise": self._collect_focus_indicators(crawler_data)
            }
        }
        return perceivable_data

    def _map_operable_criteria(self, crawler_data: Dict[str, Any], accessibility_results: Dict[str, Any]) -> Dict[str, Any]:
        operable_data = {
            "2.1_tastaturbedienbarkeit": {
                "2.1.1_tastatur": self._collect_keyboard_operability_data(accessibility_results),
                "2.1.2_kein_tastaturfang": self._collect_keyboard_trap_data(accessibility_results)
            },
            "2.2_genuegend_zeit": {
                "2.2.1_anpassbare_zeitlimits": self._collect_time_limits_data(crawler_data),
                "2.2.2_pausierbare_inhalte": self._collect_moving_content_data(crawler_data)
            },
            "2.3_anfaelle_vermeiden": {
                "2.3.1_kein_flackern_blinken": self._collect_flashing_content_data(crawler_data)
            },
            "2.4_navigierbar": {
                "2.4.1_blöcke_umgehen": {
                    "landmarks": self._collect_landmarks(crawler_data),
                    "skip_links": self._collect_skip_links(crawler_data)
                },
                "2.4.2_seitentitel": {
                    "page_titles": self._collect_page_titles(crawler_data)
                },
                "2.4.3_mehrere_navigationswege": self._collect_multiple_navigation_ways(crawler_data),
                "2.4.4_aussagekraeftige_linktexte": self._collect_link_texts(crawler_data),
                "2.4.5_korrekte_ueberschriften": self._collect_heading_usage(crawler_data),
                "2.4.6_fokus_reihenfolge": self._collect_focus_order_data(crawler_data),
                "2.4.7_fokus_sichtbar": self._collect_focus_visible_data(accessibility_results)
            }
        }
        return operable_data

    def _map_understandable_criteria(self, crawler_data: Dict[str, Any], accessibility_results: Dict[str, Any]) -> Dict[str, Any]:
        understandable_data = {
            "3.1_lesbar": {
                "3.1.1_sprache_seite": {
                    "language_declaration": self._collect_language_declaration(crawler_data)
                },
                "3.1.2_sprachwechsel": self._collect_language_changes(crawler_data)
            },
            "3.2_vorhersehbarkeit": {
                "3.2.1_konsistente_navigation": self._collect_navigation_consistency(crawler_data),
                "3.2.2_konsistente_bezeichnungen": self._collect_consistent_naming(crawler_data)
            },
            "3.3_eingabehilfe": {
                "3.3.1_fehlerhinweise": self._collect_error_identification(crawler_data),
                "3.3.2_beschriftungen_anweisungen": self._collect_form_labels(crawler_data),
                "3.3.3_fehlererkennung": self._collect_error_description(crawler_data),
                "3.3.4_hilfestellungen": self._collect_help_suggestions(crawler_data)
            }
        }
        return understandable_data

    def _map_robust_criteria(self, crawler_data: Dict[str, Any], accessibility_results: Dict[str, Any]) -> Dict[str, Any]:
        robust_data = {
            "4.1_kompatibel": {
                "4.1.1_syntaxanalyse": { # Parsing
                    "html_validation": self._collect_html_validation(crawler_data, accessibility_results)
                },
                "4.1.2_name_rolle_wert": {
                     "aria_usage": self._collect_aria_labels(crawler_data) # Wiederverwendung für allgemeine ARIA Nutzung
                }
            }
        }
        return robust_data

    def _collect_focus_order(self, crawler_data: Dict[str, Any]) -> Dict[str, Any]:
        focus_order_data = {"tab_order": [], "keyboard_navigation": [], "focus_visible_css": []}
        for url, page_data in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_data): continue
            accessibility = page_data.get("accessibility", {})
            if not self._ensure_dict(accessibility): accessibility = {}
            tab_indices = accessibility.get("tab_index", [])
            for tab_item in tab_indices:
                if not self._ensure_dict(tab_item): continue
                item_copy = tab_item.copy(); item_copy["page_url"] = url
                focus_order_data["tab_order"].append(item_copy)
            styling = page_data.get("styling", {}); css_analysis = styling.get("css_analysis", {})
            for style in css_analysis.get("inline_styles", []):
                if isinstance(style, dict) and any(fk in str(style) for fk in [":focus","outline:","box-shadow:"]):
                    focus_order_data["focus_visible_css"].append({"page_url": url, "style": style})
            keyboard_nav = accessibility.get("keyboard_navigation", {})
            if keyboard_nav: focus_order_data["keyboard_navigation"].append({"page_url": url, "data": keyboard_nav})
        return focus_order_data
        
    def _collect_focus_order_data(self, crawler_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._collect_focus_order(crawler_data)

    def _collect_skip_links(self, crawler_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        skip_links_data = []
        for url, page_data in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_data): continue
            accessibility = page_data.get("accessibility", {}); skip_links = accessibility.get("skip_links", [])
            for link in skip_links:
                if not self._ensure_dict(link): continue
                link_copy = link.copy(); link_copy["page_url"] = url
                skip_links_data.append(link_copy)
            structure = page_data.get("structure", {}); links = structure.get("links", [])
            for link in links:
                if not isinstance(link, dict): continue
                href = link.get("href", ""); text = link.get("text", "")
                if (href and href.startswith("#") and 
                    any(kw in str(text).lower() for kw in ["skip", "überspringen", "zum inhalt", "to content", "main"])):
                    skip_links_data.append({"page_url": url, "href": href, "text": text, "detected_type": "content_skip_link"})
        return skip_links_data

    def _collect_page_titles(self, crawler_data: Dict[str, Any]) -> Dict[str, Any]:
        titles_data = {"with_title": [], "without_title": [], "short_title": [], "duplicate_title": []}
        all_titles = {}
        for url, page_data in crawler_data.get("data", {}).items():
            if not isinstance(page_data, dict): continue
            structure = page_data.get("structure", {}); 
            if not isinstance(structure, dict): continue
            title_info_raw = structure.get("title", {})
            if not self._ensure_dict(title_info_raw): title_info_raw = {}
            page_title = title_info_raw.get("page_title"); h1_title = title_info_raw.get("h1_title")
            title_info = {"page_url": url, "page_title": page_title, "h1_title": h1_title}
            if page_title:
                if page_title in all_titles: all_titles[page_title].append(url)
                else: all_titles[page_title] = [url]
                if len(str(page_title)) < 10: titles_data["short_title"].append(title_info)
                else: titles_data["with_title"].append(title_info)
            else: titles_data["without_title"].append(title_info)
        for title, urls in all_titles.items():
            if len(urls) > 1:
                for u_item in urls: # Renamed url to u_item to avoid conflict
                    titles_data["duplicate_title"].append({"page_url": u_item, "page_title": title, "shared_with": [u_other for u_other in urls if u_other != u_item]})
        return titles_data

    def _collect_image_data(self, crawler_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        images_summary = {"all_extracted_images": [], "images_with_alt_text": [], "images_without_alt_text": [], "images_flagged_as_decorative": []}
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content): continue
            structure = page_content.get("structure", {})
            if not self._ensure_dict(structure): continue
            page_images = structure.get("images", [])
            if not isinstance(page_images, list): continue
            for img_info in page_images:
                if not self._ensure_dict(img_info): continue
                img_info_copy = img_info.copy(); img_info_copy["page_url"] = page_url
                images_summary["all_extracted_images"].append(img_info_copy)
                alt_text = img_info.get("alt"); is_decorative = img_info.get("decorative", False) or alt_text == ""
                if alt_text and alt_text.strip(): images_summary["images_with_alt_text"].append(img_info_copy)
                else:
                    images_summary["images_without_alt_text"].append(img_info_copy)
                    if is_decorative: images_summary["images_flagged_as_decorative"].append(img_info_copy)
        return images_summary
        
    def _collect_aria_labels(self, crawler_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        aria_data = {"elements_with_aria_label": [], "elements_with_aria_labelledby": [], "elements_with_aria_describedby": []}
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content): continue
            elements = page_content.get("structure", {}).get("all_elements", []) # Fallback to all_elements
            if not isinstance(elements, list): continue
            for elem in elements:
                if not self._ensure_dict(elem): continue
                attrs = elem.get("attributes", {})
                if not isinstance(attrs, dict): continue
                elem_details = {"tag_name": elem.get("tag_name"), "text_content": str(elem.get("text_content", ""))[:100], "html_snippet": str(elem.get("html", ""))[:200], "page_url": page_url}
                has_aria = False
                if attrs.get("aria-label"):
                    elem_details["aria_label"] = attrs["aria-label"]
                    aria_data["elements_with_aria_label"].append(elem_details.copy()) 
                    has_aria = True
                if attrs.get("aria-labelledby"):
                    elem_details["aria_labelledby"] = attrs["aria_labelledby"]
                    aria_data["elements_with_aria_labelledby"].append(elem_details.copy() if not has_aria else {**elem_details, "aria_labelledby": attrs["aria_labelledby"]}) # Avoid full duplication if already added
                    has_aria = True # ensure it's not added twice if it has label and labelledby
                if attrs.get("aria-describedby"):
                    elem_details["aria_describedby"] = attrs["aria_describedby"]
                    aria_data["elements_with_aria_describedby"].append(elem_details.copy() if not has_aria else {**elem_details, "aria_describedby": attrs["aria_describedby"]})
        return aria_data

    def _collect_form_labels(self, crawler_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        form_label_data = {"labeled_fields": [], "unlabeled_fields": [], "buttons_info": [], "other_form_elements": []}
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content): continue
            forms = page_content.get("structure", {}).get("forms", [])
            if not isinstance(forms, list): continue
            for form_idx, form_details in enumerate(forms):
                if not self._ensure_dict(form_details): continue
                for field_type_key in ["inputs", "textareas", "selects"]:
                    for field in form_details.get(field_type_key, []):
                        if not self._ensure_dict(field): continue
                        field_copy = field.copy(); field_copy["page_url"] = page_url; field_copy["form_index"] = form_idx; field_copy["element_type"] = field_type_key[:-1]
                        # Check for explicit label, aria-label, or aria-labelledby
                        has_label = field.get("label_text") or field.get("attributes",{}).get("aria-label") or field.get("attributes",{}).get("aria-labelledby")
                        if has_label:
                            form_label_data["labeled_fields"].append(field_copy)
                    else:
                            form_label_data["unlabeled_fields"].append(field_copy)
                for button in form_details.get("buttons", []):
                    if not self._ensure_dict(button): continue
                    button_copy = button.copy(); button_copy["page_url"] = page_url; button_copy["form_index"] = form_idx
                    form_label_data["buttons_info"].append(button_copy)
        return form_label_data
        
    def _collect_complex_images(self, crawler_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        complex_images = []
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content): continue
            page_images = page_content.get("structure", {}).get("images", [])
            if not isinstance(page_images, list): continue
            for img_info in page_images:
                if not self._ensure_dict(img_info): continue
                attrs = img_info.get("attributes", {})
                if not isinstance(attrs, dict): continue
                has_longdesc = attrs.get("longdesc")
                # figure_context might not exist or might not have has_figcaption
                figure_context = img_info.get("figure_context", {})
                in_figure_with_caption = figure_context.get("has_figcaption") if isinstance(figure_context, dict) else False
                if has_longdesc or in_figure_with_caption:
                    img_copy = img_info.copy(); img_copy["page_url"] = page_url
                    reasons = []
                    if has_longdesc: reasons.append("has_longdesc")
                    if in_figure_with_caption: reasons.append("in_figure_with_figcaption")
                    img_copy["reason_complex"] = ", ".join(reasons)
                    complex_images.append(img_copy)
        return complex_images

    def _collect_captcha_data(self, crawler_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        captchas = []
        captcha_keywords = ["captcha", "recaptcha", "hcaptcha", "verification", "sicherheitsprüfung", "security check", "verify you are human"]
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content): continue
            # Durchsuche Textinhalte und typische Attribute nach CAPTCHA-Hinweisen
            text_content_raw = page_content.get("raw_text_content", "").lower() # Annahme: Crawler liefert gesamten Text
            if any(keyword in text_content_raw for keyword in captcha_keywords):
                 captchas.append({"page_url": page_url, "found_in_text": True, "text_snippet": text_content_raw[:200]})
                 continue # Um Doppelungen zu vermeiden, wenn auch in Elementen gefunden

            elements = page_content.get("structure", {}).get("all_elements", [])
            if not isinstance(elements, list): continue
            for elem in elements:
                if not self._ensure_dict(elem): continue
                elem_text = str(elem.get("text_content", "")).lower()
                elem_attrs_str = str(elem.get("attributes", {})).lower()
                # Suche nach typischen Attributen oder Klassen
                if any(keyword in elem_text for keyword in captcha_keywords) or \
                   any(f'{keyword}' in elem_attrs_str for keyword in captcha_keywords) or \
                   ("class" in elem.get("attributes", {}) and any(keyword in c.lower() for c in elem["attributes"]["class"] for keyword in captcha_keywords if isinstance(elem["attributes"]["class"], list))) or \
                   ("id" in elem.get("attributes", {}) and any(keyword in elem["attributes"]["id"].lower() for keyword in captcha_keywords if isinstance(elem["attributes"]["id"], str))):
                    captchas.append({"page_url": page_url, "element_tag": elem.get("tag_name"), "text_snippet": elem_text[:100], "attributes_snippet": elem_attrs_str[:100], "found_in_text": False})
        return captchas
        
    def _collect_landmarks(self, crawler_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        landmarks_data = []
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content): continue
            page_landmarks = page_content.get("structure", {}).get("landmarks", []) # Direkte Annahme aus Crawler-Daten
            if not isinstance(page_landmarks, list): continue
            for lm_info in page_landmarks:
                if not self._ensure_dict(lm_info): continue
                lm_copy = lm_info.copy()
                lm_copy["page_url"] = page_url
                landmarks_data.append(lm_copy)
        return landmarks_data
        
    def _collect_language_declaration(self, crawler_data: Dict[str, Any]) -> Dict[str, Any]:
        lang_data = {"pages_language_declaration": [], "text_language_changes": []}
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content): continue
            html_attrs = page_content.get("structure", {}).get("html_attributes", {})
            main_lang = html_attrs.get("lang") if isinstance(html_attrs, dict) else None
            lang_data["pages_language_declaration"].append({"page_url": page_url, "declared_lang": main_lang if main_lang else "Not declared"})
            
            elements_with_lang = page_content.get("structure", {}).get("elements_with_lang_attribute", []) # Annahme: Crawler liefert diese Liste
            if not isinstance(elements_with_lang, list): continue
            for elem in elements_with_lang:
                if not self._ensure_dict(elem): continue
                elem_lang = elem.get("attributes", {}).get("lang")
                if elem_lang and elem_lang.strip() and elem_lang.lower() != (main_lang.lower() if main_lang else ""):
                    lang_data["text_language_changes"].append({
                        "page_url": page_url, 
                        "tag_name": elem.get("tag_name"), 
                        "lang_attribute": elem_lang, 
                        "text_snippet": str(elem.get("text_content", ""))[:100]
                    })
        return lang_data

    def _collect_html_validation(self, crawler_data: Dict[str, Any], accessibility_results: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        validation_issues = {"doctype_issues": [], "encoding_issues": [], "parsing_errors_from_checker": []}
        # Annahme 1: Doctype und Encoding Infos kommen vom Crawler pro Seite
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content): continue
            structure = page_content.get("structure", {})
            if not self._ensure_dict(structure): continue
            if not structure.get("doctype_present"): # Annahme: boolean flag vom Crawler
                validation_issues["doctype_issues"].append({"page_url": page_url, "issue": "Doctype missing or not detected"})
            if not structure.get("charset_declared"): # Annahme: boolean flag vom Crawler
                validation_issues["encoding_issues"].append({"page_url": page_url, "issue": "Character encoding not declared"})

        # Annahme 2: Parsing-Fehler kommen vom Accessibility Checker
        for viol in accessibility_results.get("violations", []):
            # Typische IDs für Parsing-Probleme (Beispiele, an Axe-Core o.ä. anpassen)
            if viol.get("id") in ["html-lang-valid", "aria-roles", "duplicate-id-active", "duplicate-id-aria", "valid-lang"]:
                for node in viol.get("nodes", []):
                    if not self._ensure_dict(node): continue
                    # Versuche, die URL aus den Target-Informationen des Nodes zu extrahieren oder zuzuordnen
                    # Dies ist eine Heuristik und muss ggf. an die Struktur von accessibility_results angepasst werden.
                    target_url = "UnknownPage"
                    if node.get("target") and isinstance(node.get("target"), list) and node.get("target"): 
                        # Annahme: target ist eine Liste von Selektoren, die URL ist nicht direkt hier
                        # Wir müssten die Violations pro Seite gruppieren, was der Checker evtl. nicht macht.
                        # Fürs Erste nehmen wir die Haupt-URL, wenn keine spezifischere Info da ist.
                        target_url = accessibility_results.get("url", crawler_data.get("base_url", "UnknownPage"))
                    
                    validation_issues["parsing_errors_from_checker"].append({
                        "page_url": target_url, # Bestmögliche Zuordnung
                        "error_id": viol.get("id"), 
                        "message": viol.get("help", ""), 
                        "html_snippet": node.get("html", ""),
                        "impact": viol.get("impact")
                    })
        return validation_issues
        
    def _generate_summary(self, crawler_data: Dict[str, Any], accessibility_results: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "Summary generation not yet implemented."}
        
    def _calculate_scores(self, crawler_data: Dict[str, Any], accessibility_results: Dict[str, Any]) -> Dict[str, float]:
        return {"perceivable": 0.0, "operable": 0.0, "understandable": 0.0, "robust": 0.0, "overall": 0.0 }

    # Hilfsmethoden (Beispiele)
    def _collect_color_reliance_data(self, accessibility_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        color_issues = []
        for viol in accessibility_results.get("violations", []):
            if viol.get("id") == "use-of-color": # Axe-Core ID für alleinige Farbnutzung
                color_issues.append(viol)
        return color_issues

    def _collect_contrast_data(self, accessibility_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        contrast_issues = []
        for viol in accessibility_results.get("violations", []):
            if viol.get("id") == "color-contrast":
                contrast_issues.extend(viol.get("nodes", [])) 
        return contrast_issues
    
    def _collect_keyboard_operability_data(self, accessibility_results: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        keyboard_data = {"violations": [], "warnings": []}
        for viol in accessibility_results.get("violations", []):
            if viol.get("id") in ["keyboard", "focus-order", "no-keyboard-trap", "scrollable-region-focusable", "button-name", "link-name"]:
                keyboard_data["violations"].append(viol)
        for warn in accessibility_results.get("warnings", []):
            if warn.get("id") in ["tabindex"] : # Tabindex > 0 ist oft eine Warnung
                keyboard_data["warnings"].append(warn)
        return keyboard_data

    def _collect_focus_visible_data(self, accessibility_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        focus_issues = []
        for viol in accessibility_results.get("violations", []):
             if viol.get("id") in ["focus-visible", "focus-not-visible-inline", "css-orientation-lock", "ensure-focus-order"] : # Axe-IDs
                focus_issues.append(viol)
        return focus_issues

    # Neue Sammelmethoden für erweiterte WCAG-Abdeckung
    
    # 1.2 Zeitbasierte Medien
    def _collect_audio_content(self, crawler_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        audio_elements = []
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content): continue
            elements = page_content.get("structure", {}).get("all_elements", [])
            if not isinstance(elements, list): continue
            for elem in elements:
                if not self._ensure_dict(elem): continue
                if elem.get("tag_name") == "audio":
                    elem_copy = elem.copy()
                    elem_copy["page_url"] = page_url
                    audio_elements.append(elem_copy)
        return audio_elements

    def _collect_video_content(self, crawler_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        video_elements = []
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content): continue
            elements = page_content.get("structure", {}).get("all_elements", [])
            if not isinstance(elements, list): continue
            for elem in elements:
                if not self._ensure_dict(elem): continue
                if elem.get("tag_name") in ["video", "iframe"]:
                    elem_copy = elem.copy()
                    elem_copy["page_url"] = page_url
                    # Prüfe auf Video-Plattformen
                    src = elem.get("attributes", {}).get("src", "")
                    if any(platform in str(src).lower() for platform in ["youtube", "vimeo", "wistia"]):
                        elem_copy["platform_detected"] = True
                    video_elements.append(elem_copy)
        return video_elements

    def _collect_multimedia_alternatives(self, crawler_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        multimedia_alternatives = []
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content): continue
            elements = page_content.get("structure", {}).get("all_elements", [])
            if not isinstance(elements, list): continue
            for elem in elements:
                if not self._ensure_dict(elem): continue
                if elem.get("tag_name") in ["track", "caption"]:
                    elem_copy = elem.copy()
                    elem_copy["page_url"] = page_url
                    multimedia_alternatives.append(elem_copy)
        return multimedia_alternatives

    # 1.3 Anpassbare Darstellung
    def _collect_semantic_html(self, crawler_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        semantic_data = {"semantic_elements": [], "non_semantic_usage": []}
        semantic_tags = ["header", "nav", "main", "section", "article", "aside", "footer"]
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content): continue
            elements = page_content.get("structure", {}).get("all_elements", [])
            if not isinstance(elements, list): continue
            for elem in elements:
                if not self._ensure_dict(elem): continue
                tag_name = elem.get("tag_name")
                if tag_name in semantic_tags:
                    elem_copy = elem.copy()
                    elem_copy["page_url"] = page_url
                    semantic_data["semantic_elements"].append(elem_copy)
                elif tag_name == "div" and elem.get("attributes", {}).get("role"):
                    elem_copy = elem.copy()
                    elem_copy["page_url"] = page_url
                    semantic_data["non_semantic_usage"].append(elem_copy)
        return semantic_data

    def _collect_heading_structure(self, crawler_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        heading_data = {"headings": [], "structure_violations": []}
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content): continue
            headings = page_content.get("structure", {}).get("headings", [])
            if isinstance(headings, list):
                for heading in headings:
                    if isinstance(heading, dict):
                        heading_copy = heading.copy()
                        heading_copy["page_url"] = page_url
                        heading_data["headings"].append(heading_copy)
        return heading_data

    def _collect_layout_consistency(self, crawler_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        layout_data = []
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content): continue
            navigation = page_content.get("structure", {}).get("navigation", {})
            if navigation:
                nav_copy = navigation.copy() if isinstance(navigation, dict) else {}
                nav_copy["page_url"] = page_url
                layout_data.append(nav_copy)
        return layout_data

    def _collect_content_order(self, crawler_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        order_data = []
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content): continue
            structure = page_content.get("structure", {})
            if structure:
                order_info = {
                    "page_url": page_url,
                    "has_main": bool(structure.get("main_content")),
                    "heading_count": len(structure.get("headings", [])),
                    "landmark_count": len(structure.get("landmarks", []))
                }
                order_data.append(order_info)
        return order_data

    # 1.4 Erweiterte Unterscheidbarkeit
    def _collect_text_scaling_data(self, accessibility_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        scaling_issues = []
        for viol in accessibility_results.get("violations", []):
            if viol.get("id") in ["meta-viewport", "zoom-disable"]:
                scaling_issues.append(viol)
        return scaling_issues

    def _collect_text_customization_data(self, accessibility_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        customization_issues = []
        for viol in accessibility_results.get("violations", []):
            if viol.get("id") in ["css-text-spacing", "content-reflow"]:
                customization_issues.append(viol)
        return customization_issues

    def _collect_graphic_contrast_data(self, accessibility_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        graphic_contrast_issues = []
        for viol in accessibility_results.get("violations", []):
            if viol.get("id") in ["non-text-contrast", "graphic-contrast"]:
                graphic_contrast_issues.append(viol)
        return graphic_contrast_issues

    def _collect_focus_indicators(self, crawler_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        focus_indicators = []
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content): continue
            styling = page_content.get("styling", {})
            css_analysis = styling.get("css_analysis", {}) if isinstance(styling, dict) else {}
            for style in css_analysis.get("inline_styles", []):
                if isinstance(style, dict) and ":focus" in str(style):
                    focus_indicators.append({"page_url": page_url, "style": style})
        return focus_indicators

    # 2.2 Genügend Zeit
    def _collect_time_limits_data(self, crawler_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        time_limits = []
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content): continue
            elements = page_content.get("structure", {}).get("all_elements", [])
            if not isinstance(elements, list): continue
            for elem in elements:
                if not self._ensure_dict(elem): continue
                # Suche nach Meta-Refresh oder JavaScript-Weiterleitungen
                if elem.get("tag_name") == "meta":
                    attrs = elem.get("attributes", {})
                    if attrs.get("http-equiv") == "refresh":
                        elem_copy = elem.copy()
                        elem_copy["page_url"] = page_url
                        time_limits.append(elem_copy)
        return time_limits

    def _collect_moving_content_data(self, crawler_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        moving_content = []
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content): continue
            elements = page_content.get("structure", {}).get("all_elements", [])
            if not isinstance(elements, list): continue
            for elem in elements:
                if not self._ensure_dict(elem): continue
                # Suche nach animierten Elementen
                attrs = elem.get("attributes", {})
                if any(anim_attr in str(attrs).lower() for anim_attr in ["autoplay", "animation", "marquee"]):
                    elem_copy = elem.copy()
                    elem_copy["page_url"] = page_url
                    moving_content.append(elem_copy)
        return moving_content

    # 2.3 Anfälle vermeiden
    def _collect_flashing_content_data(self, crawler_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        flashing_content = []
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content): continue
            elements = page_content.get("structure", {}).get("all_elements", [])
            if not isinstance(elements, list): continue
            for elem in elements:
                if not self._ensure_dict(elem): continue
                # Suche nach blinkenden/flackernden Elementen
                if elem.get("tag_name") in ["blink", "marquee"] or "flash" in str(elem.get("attributes", {})).lower():
                    elem_copy = elem.copy()
                    elem_copy["page_url"] = page_url
                    flashing_content.append(elem_copy)
        return flashing_content

    # 2.4 Erweiterte Navigation
    def _collect_multiple_navigation_ways(self, crawler_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        navigation_ways = {"navigation_menus": [], "search_functions": [], "sitemaps": []}
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content): continue
            navigation = page_content.get("structure", {}).get("navigation", {})
            if navigation:
                nav_copy = navigation.copy() if isinstance(navigation, dict) else {}
                nav_copy["page_url"] = page_url
                navigation_ways["navigation_menus"].append(nav_copy)
            
            # Suche nach Suchfunktionen
            forms = page_content.get("structure", {}).get("forms", [])
            for form in forms:
                if isinstance(form, dict) and any(search_term in str(form).lower() for search_term in ["search", "suche"]):
                    form_copy = form.copy()
                    form_copy["page_url"] = page_url
                    navigation_ways["search_functions"].append(form_copy)
        return navigation_ways

    def _collect_link_texts(self, crawler_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        link_data = {"descriptive_links": [], "non_descriptive_links": []}
        non_descriptive_patterns = ["click here", "more", "read more", "hier klicken", "mehr", "weiterlesen"]
        
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content): continue
            links = page_content.get("structure", {}).get("links", [])
            if not isinstance(links, list): continue
            for link in links:
                if not self._ensure_dict(link): continue
                link_copy = link.copy()
                link_copy["page_url"] = page_url
                text = str(link.get("text", "")).lower().strip()
                if any(pattern in text for pattern in non_descriptive_patterns) or len(text) < 4:
                    link_data["non_descriptive_links"].append(link_copy)
                else:
                    link_data["descriptive_links"].append(link_copy)
        return link_data

    def _collect_heading_usage(self, crawler_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        heading_usage = {"proper_hierarchy": [], "hierarchy_violations": []}
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content): continue
            headings = page_content.get("structure", {}).get("headings", [])
            if isinstance(headings, list):
                prev_level = 0
                for heading in headings:
                    if isinstance(heading, dict):
                        heading_copy = heading.copy()
                        heading_copy["page_url"] = page_url
                        level = heading.get("level", 0)
                        if level > prev_level + 1:
                            heading_usage["hierarchy_violations"].append(heading_copy)
                        else:
                            heading_usage["proper_hierarchy"].append(heading_copy)
                        prev_level = level
        return heading_usage

    # 2.1 Erweiterte Tastaturbedienung
    def _collect_keyboard_trap_data(self, accessibility_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        keyboard_trap_issues = []
        for viol in accessibility_results.get("violations", []):
            if viol.get("id") in ["keyboard-trap", "no-keyboard-trap"]:
                keyboard_trap_issues.append(viol)
        return keyboard_trap_issues

    # 3.1 Erweiterte Lesbarkeit
    def _collect_language_changes(self, crawler_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        language_changes = []
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content): continue
            elements_with_lang = page_content.get("structure", {}).get("elements_with_lang_attribute", [])
            if isinstance(elements_with_lang, list):
                for elem in elements_with_lang:
                    if isinstance(elem, dict):
                        elem_copy = elem.copy()
                        elem_copy["page_url"] = page_url
                        language_changes.append(elem_copy)
        return language_changes

    # 3.2 Vorhersehbarkeit
    def _collect_navigation_consistency(self, crawler_data: Dict[str, Any]) -> Dict[str, Any]:
        navigation_consistency = {"consistent_navs": [], "inconsistent_navs": []}
        nav_structures = {}
        
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content): continue
            navigation = page_content.get("structure", {}).get("navigation", {})
            if navigation:
                nav_hash = str(sorted(navigation.items())) if isinstance(navigation, dict) else str(navigation)
                if nav_hash in nav_structures:
                    nav_structures[nav_hash].append(page_url)
                else:
                    nav_structures[nav_hash] = [page_url]
        
        for nav_structure, pages in nav_structures.items():
            entry = {"structure": nav_structure, "pages": pages}
            if len(pages) > 1:
                navigation_consistency["consistent_navs"].append(entry)
            else:
                navigation_consistency["inconsistent_navs"].append(entry)
        
        return navigation_consistency

    def _collect_consistent_naming(self, crawler_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        naming_consistency = {"consistent_elements": [], "inconsistent_elements": []}
        element_names = {}
        
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content): continue
            buttons = page_content.get("structure", {}).get("buttons", [])
            if isinstance(buttons, list):
                for button in buttons:
                    if isinstance(button, dict):
                        text = button.get("text", "").strip()
                        if text:
                            if text in element_names:
                                element_names[text].append({"page_url": page_url, "element": button})
                            else:
                                element_names[text] = [{"page_url": page_url, "element": button}]
        
        for text, occurrences in element_names.items():
            entry = {"text": text, "occurrences": occurrences}
            if len(occurrences) > 1:
                naming_consistency["consistent_elements"].append(entry)
            else:
                naming_consistency["inconsistent_elements"].append(entry)
                
        return naming_consistency

    # 3.3 Erweiterte Eingabehilfe
    def _collect_error_identification(self, crawler_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        error_identification = []
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content): continue
            forms = page_content.get("structure", {}).get("forms", [])
            if isinstance(forms, list):
                for form in forms:
                    if isinstance(form, dict):
                        # Suche nach Validierungsattributen
                        for field_type in ["inputs", "textareas", "selects"]:
                            for field in form.get(field_type, []):
                                if isinstance(field, dict):
                                    attrs = field.get("attributes", {})
                                    if any(validation_attr in attrs for validation_attr in ["required", "pattern", "min", "max"]):
                                        field_copy = field.copy()
                                        field_copy["page_url"] = page_url
                                        error_identification.append(field_copy)
        return error_identification

    def _collect_error_description(self, crawler_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        error_descriptions = []
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content): continue
            elements = page_content.get("structure", {}).get("all_elements", [])
            if isinstance(elements, list):
                for elem in elements:
                    if isinstance(elem, dict):
                        # Suche nach Fehlermeldungs-Elementen
                        attrs = elem.get("attributes", {})
                        classes = attrs.get("class", [])
                        if isinstance(classes, list) and any("error" in str(cls).lower() for cls in classes):
                            elem_copy = elem.copy()
                            elem_copy["page_url"] = page_url
                            error_descriptions.append(elem_copy)
        return error_descriptions

    def _collect_help_suggestions(self, crawler_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        help_suggestions = []
        for page_url, page_content in crawler_data.get("data", {}).items():
            if not self._ensure_dict(page_content): continue
            elements = page_content.get("structure", {}).get("all_elements", [])
            if isinstance(elements, list):
                for elem in elements:
                    if isinstance(elem, dict):
                        # Suche nach Hilfe-Elementen
                        attrs = elem.get("attributes", {})
                        if "aria-describedby" in attrs or any(help_text in str(elem.get("text_content", "")).lower() for help_text in ["help", "hilfe", "tooltip", "hint"]):
                            elem_copy = elem.copy()
                            elem_copy["page_url"] = page_url
                            help_suggestions.append(elem_copy)
        return help_suggestions