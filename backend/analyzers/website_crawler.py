import scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import urljoin, urlparse
from typing import Set, Dict, List, Any, Optional
import logging
import re
from bs4 import BeautifulSoup
import requests
import json
import time
import traceback

logger = logging.getLogger(__name__)

class WebsiteCrawler:
    def __init__(self):
        self.visited_urls: Set[str] = set()
        self.pages_data: Dict[str, Any] = {}
        self.base_url = ""
        self.logger = logger

    def setup_logging(self):
        logging.basicConfig(
            level=logging.DEBUG,  # Setze Level auf DEBUG für mehr Details
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def is_valid_url(self, url: str) -> bool:
        """Überprüft, ob die URL zur gleichen Domain gehört"""
        try:
            if not self.base_url:
                return True
            parsed_base = urlparse(self.base_url)
            parsed_url = urlparse(url)
            return parsed_base.netloc == parsed_url.netloc
        except Exception as e:
            self.logger.error(f"Fehler bei URL-Validierung: {str(e)}")
            return False

    def extract_page_data(self, url: str) -> Dict[str, Any]:
        """Extrahiert alle relevanten Daten von einer Seite"""
        self.logger.debug(f"Extrahiere Daten von {url}")
        try:
            self.logger.info(f"Starte Extraktion von {url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            self.logger.debug(f"Response Status: {response.status_code}")
            self.logger.debug(f"Content-Type: {response.headers.get('content-type')}")
            
            soup = BeautifulSoup(response.text, 'html5lib')
            
            page_data = {
                "url": url,
                "title": self._get_title(soup),
                "metadata": self._get_metadata(soup),
                "structure": {
                    "headings": self._get_headings(soup),
                    "navigation": self._get_navigation(soup),
                    "landmarks": self._get_landmarks(soup),
                    "forms": self._get_forms(soup),
                    "images": self._get_images(soup),
                    "links": self._get_links(soup),
                    "tables": self._get_tables(soup),
                    "lists": self._get_lists(soup),
                    "iframes": self._get_iframes(soup),
                    "multimedia": self._get_multimedia(soup),
                    "interactive_elements": self._analyze_interactive_elements(soup),
                    "doctype": self._get_doctype(soup)
                },
                "accessibility": {
                    "aria_roles": self._get_aria_roles(soup),
                    "aria_labels": self._get_aria_labels(soup),
                    "aria_attributes": self._get_aria_attributes(soup),
                    "tab_index": self._get_tab_indices(soup),
                    "language": self._get_language_info(soup),
                    "skip_links": self._get_skip_links(soup),
                    "keyboard_navigation": self._check_keyboard_traps(soup),
                    "focus_order": self._analyze_focus_order(soup),
                    "text_alternatives": self._check_text_alternatives(soup),
                    "error_identification": self._check_error_identification(soup),
                    "form_validation": self._check_form_validation(soup)
                },
                "styling": {
                    "colors": self._get_colors(soup),
                    "fonts": self._get_fonts(soup),
                    "responsive": self._check_responsive_elements(soup),
                    "css_analysis": self._analyze_css(soup),
                    "text_spacing": self._get_text_spacing(soup),
                    "contrast_data": self._extract_contrast_data(soup)
                },
                "scripting": self._analyze_javascript(soup),
                "performance": self._analyze_performance(soup, response),
                "semantics": self._analyze_semantics(soup),
                "security": self._analyze_security(soup, response),
                "headers": dict(response.headers),
                "timing": {
                    "load_time": response.elapsed.total_seconds(),
                    "redirect_count": len(response.history)
                }
            }
            
            # Wichtig: Sanitize alle Daten vor der Rückgabe
            sanitized_data = self._sanitize_data(page_data)
            
            self.logger.info(f"Extraktion von {url} erfolgreich abgeschlossen")
            return sanitized_data
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Netzwerkfehler bei {url}: {str(e)}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            return {"error": error_msg, "type": "network_error"}
        except Exception as e:
            error_msg = f"Unerwarteter Fehler bei {url}: {str(e)}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            return {"error": error_msg, "type": "unexpected_extraction_error"}

    def _get_title(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extrahiert Titel-Informationen"""
        return {
            "page_title": soup.title.string if soup.title else None,
            "meta_title": soup.find("meta", property="og:title"),
            "h1_title": soup.h1.string if soup.h1 else None
        }

    def _get_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extrahiert Metadata"""
        return {
            "description": soup.find("meta", {"name": "description"}),
            "keywords": soup.find("meta", {"name": "keywords"}),
            "viewport": soup.find("meta", {"name": "viewport"}),
            "charset": soup.find("meta", {"charset": True}),
            "robots": soup.find("meta", {"name": "robots"})
        }

    def _get_headings(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extrahiert alle Überschriften und ihre Hierarchie MIT HTML-Code"""
        headings = []
        for level in range(1, 7):
            for heading in soup.find_all(f'h{level}'):
                # NEU: HTML-Snippet
                html_snippet = str(heading)
                
                # Kontext
                parent = heading.parent
                html_context = ""
                if parent:
                    parent_html = str(parent)
                    # Limitiere Kontext-Größe
                    if len(parent_html) > 1000:
                        html_context = parent_html[:500] + f"...[H{level}_HERE]..." + parent_html[-500:]
                    else:
                        html_context = parent_html
                
                headings.append({
                    "level": level,
                    "text": heading.get_text(),
                    "id": heading.get("id"),
                    "classes": heading.get("class", []),
                    "aria_label": heading.get("aria-label"),
                    # NEU: HTML-Daten für bessere AI-Analyse
                    "html": html_snippet,
                    "context": html_context
                })
        return headings

    def _get_navigation(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extrahiert Navigationsstrukturen"""
        nav_elements = []
        for nav in soup.find_all(["nav", "header", "footer", "[role='navigation']"]):
            nav_elements.append({
                "type": nav.name,
                "role": nav.get("role"),
                "aria_label": nav.get("aria-label"),
                "links": [{"text": a.get_text(), "href": a.get("href")} 
                         for a in nav.find_all("a")]
            })
        return nav_elements

    def _get_landmarks(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extrahiert ARIA-Landmarks"""
        landmarks = []
        landmark_roles = ["banner", "navigation", "main", "complementary", 
                         "contentinfo", "search", "form", "region"]
        
        for role in landmark_roles:
            elements = soup.find_all(attrs={"role": role})
            for element in elements:
                landmarks.append({
                    "role": role,
                    "aria_label": element.get("aria-label"),
                    "tag_name": element.name
                })
        return landmarks

    def _get_forms(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extrahiert Formular-Informationen"""
        forms = []
        for form in soup.find_all("form"):
            form_data = {
                "id": form.get("id"),
                "name": form.get("name"),
                "method": form.get("method"),
                "action": form.get("action"),
                "enctype": form.get("enctype"),
                "novalidate": form.get("novalidate") is not None,
                "aria_attributes": self._get_element_aria_attributes(form),
                "fields": []
            }
            
            for field in form.find_all(["input", "select", "textarea", "button", "fieldset", "legend", "datalist", "output"]):
                # NEU: HTML-Snippet für jedes Formularfeld
                html_snippet = str(field)
                
                field_data = {
                    "type": field.get("type", "text" if field.name == "input" else field.name),
                    "name": field.get("name"),
                    "id": field.get("id"),
                    "value": field.get("value"),
                    "placeholder": field.get("placeholder"),
                    "required": field.get("required") is not None,
                    "disabled": field.get("disabled") is not None,
                    "readonly": field.get("readonly") is not None,
                    "autocomplete": field.get("autocomplete"),
                    "pattern": field.get("pattern"),
                    "min": field.get("min"),
                    "max": field.get("max"),
                    "minlength": field.get("minlength"),
                    "maxlength": field.get("maxlength"),
                    "size": field.get("size"),
                    "multiple": field.get("multiple") is not None,
                    "aria_attributes": self._get_element_aria_attributes(field),
                    "label": self._find_label_for_field(field, soup),
                    "error_message": self._find_error_message(field, soup),
                    "help_text": self._find_help_text(field, soup),
                    "grouped": self._is_grouped_in_fieldset(field, soup),
                    # NEU: HTML-Code für AI-Analyse
                    "html": html_snippet,
                    "css_classes": field.get("class", [])
                }
                form_data["fields"].append(field_data)
                
            forms.append(form_data)
        return forms

    def _find_label_for_field(self, field: Any, soup: BeautifulSoup) -> str:
        """Findet das Label für ein Formularfeld"""
        field_id = field.get("id")
        if field_id:
            label = soup.find("label", {"for": field_id})
            if label:
                return label.get_text()
        return None

    def _find_error_message(self, field: Any, soup: BeautifulSoup) -> Dict[str, Any]:
        """Findet Fehlermeldungen für ein Formularfeld"""
        field_id = field.get("id")
        if not field_id:
            return None
            
        # Suche nach verbundenen error-Elementen
        error_messages = []
        
        # Methode 1: Elemente, die auf dieses Feld verweisen
        for error_elem in soup.find_all(attrs={"aria-errormessage": field_id}):
            error_messages.append({
                "text": error_elem.get_text(),
                "element": error_elem.name,
                "type": "referenced"
            })
            
        # Methode 2: Elemente, die mit aria-describedby verbunden sind
        described_by = field.get("aria-describedby")
        if described_by:
            for desc_id in described_by.split():
                desc_elem = soup.find(id=desc_id)
                if desc_elem:
                    error_messages.append({
                        "text": desc_elem.get_text(),
                        "element": desc_elem.name,
                        "type": "describedby"
                    })
                    
        # Methode 3: Suche nach benachbarten Elementen mit Fehlerhinweisen
        siblings = field.find_next_siblings()
        for sibling in siblings[:3]:  # Prüfe nur die nächsten 3 Geschwister-Elemente
            if sibling.get("class") and any("error" in cls.lower() for cls in sibling.get("class")):
                error_messages.append({
                    "text": sibling.get_text(),
                    "element": sibling.name,
                    "type": "adjacent_error_class"
                })
                
        return error_messages if error_messages else None

    def _find_help_text(self, field: Any, soup: BeautifulSoup) -> Dict[str, Any]:
        """Findet Hilfstexte für ein Formularfeld"""
        field_id = field.get("id")
        if not field_id:
            return None
            
        help_texts = []
        
        # Methode 1: Elemente, die mit aria-describedby verbunden sind
        described_by = field.get("aria-describedby")
        if described_by:
            for desc_id in described_by.split():
                desc_elem = soup.find(id=desc_id)
                if desc_elem:
                    help_texts.append({
                        "text": desc_elem.get_text(),
                        "element": desc_elem.name,
                        "type": "describedby"
                    })
                    
        # Methode 2: Suche nach benachbarten Hilfstexten
        siblings = field.find_next_siblings()
        for sibling in siblings[:3]:
            if sibling.get("class") and any(cls in ["help", "hint", "info", "description"] for cls in sibling.get("class", [])):
                help_texts.append({
                    "text": sibling.get_text(),
                    "element": sibling.name,
                    "type": "adjacent_help_class"
                })
                
        return help_texts if help_texts else None

    def _is_grouped_in_fieldset(self, field: Any, soup: BeautifulSoup) -> Dict[str, Any]:
        """Prüft, ob ein Feld in einem Fieldset gruppiert ist"""
        parent_fieldset = field.find_parent("fieldset")
        if not parent_fieldset:
            return None
            
        legend = parent_fieldset.find("legend")
        return {
            "fieldset_id": parent_fieldset.get("id"),
            "legend": legend.get_text() if legend else None,
            "aria_attributes": self._get_element_aria_attributes(parent_fieldset)
        }

    def _get_element_aria_attributes(self, element: Any) -> Dict[str, str]:
        """Extrahiert alle ARIA-Attribute eines Elements"""
        aria_attrs = {}
        for attr in element.attrs:
            if attr.startswith("aria-") or attr == "role":
                aria_attrs[attr] = element.get(attr)
        return aria_attrs

    def _get_images(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extrahiert Bild-Informationen mit vollständigen HTML-Snippets für AI-Analyse"""
        images = []
        for img in soup.find_all("img"):
            # NEU: Extrahiere HTML-Snippet und Kontext
            html_snippet = str(img)
            
            # Kontext: Suche nach umgebendem HTML (parent + siblings)
            parent = img.parent
            html_context = ""
            if parent:
                # Erstelle eine Kopie des Parents ohne das Bild selbst für Kontext
                parent_copy = BeautifulSoup(str(parent), 'html.parser')
                # Markiere das aktuelle Bild
                for img_copy in parent_copy.find_all('img'):
                    if img_copy.get('src') == img.get('src'):
                        img_copy.replace_with('<!-- CURRENT_IMAGE_HERE -->')
                        break
                html_context = str(parent_copy).replace('<!-- CURRENT_IMAGE_HERE -->', '[CURRENT_IMG]')
            
            # DOM-Pfad für bessere Lokalisierung
            dom_path = []
            current = img
            while current.parent and len(dom_path) < 5:
                parent_info = current.parent.name
                if current.parent.get('id'):
                    parent_info += f"#{current.parent.get('id')}"
                elif current.parent.get('class'):
                    parent_info += f".{'.'.join(current.parent.get('class'))}"
                dom_path.append(parent_info)
                current = current.parent
            dom_path.reverse()
            
            images.append({
                "src": img.get("src"),
                "alt": img.get("alt"),
                "title": img.get("title"),
                "width": img.get("width"),
                "height": img.get("height"),
                "loading": img.get("loading"),
                "longdesc": img.get("longdesc"),
                "aria_attributes": self._get_element_aria_attributes(img),
                "decorative": img.get("alt") == "" or img.get("role") == "presentation",
                "figure_context": self._get_figure_context(img),
                "css_classes": img.get("class", []),
                "parent_link": bool(img.find_parent("a")),
                "is_responsive": self._is_responsive_image(img),
                # NEU: HTML-Daten für AI-Analyse (wichtig für 350-450€ Analysen!)
                "html": html_snippet,
                "context": html_context[:1500],  # Mehr Kontext für bessere AI-Analyse
                "dom_path": " > ".join(dom_path),
                "style": img.get("style"),  # Inline-Styles
                "id": img.get("id")
            })
        return images

    def _get_figure_context(self, img: Any) -> Dict[str, Any]:
        """Ermittelt, ob ein Bild in einem figure-Element ist und extrahiert den figcaption-Text"""
        figure = img.find_parent("figure")
        if not figure:
            return None
            
        figcaption = figure.find("figcaption")
        return {
            "has_figure": True,
            "figcaption": figcaption.get_text() if figcaption else None,
            "figure_id": figure.get("id"),
            "figure_classes": figure.get("class", []),
            "aria_attributes": self._get_element_aria_attributes(figure)
        }

    def _is_responsive_image(self, img: Any) -> bool:
        """Prüft, ob ein Bild responsive ist (srcset, sizes oder CSS-Klassen)"""
        return (img.get("srcset") is not None or 
                img.get("sizes") is not None or 
                (img.get("class") and any("responsive" in cls.lower() for cls in img.get("class", []))))

    def _get_links(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extrahiert Link-Informationen MIT HTML-Code für AI-Analyse"""
        links = []
        for a in soup.find_all("a"):
            # NEU: HTML-Snippet
            html_snippet = str(a)
            
            # Kontext: Parent und umgebende Elemente
            parent = a.parent
            html_context = ""
            if parent:
                # Finde Position des Links im Parent
                parent_html = str(parent)
                if len(parent_html) > 1000:
                    # Bei langem Parent nur relevanten Ausschnitt
                    link_pos = parent_html.find(html_snippet)
                    if link_pos >= 0:
                        start = max(0, link_pos - 300)
                        end = min(len(parent_html), link_pos + len(html_snippet) + 300)
                        html_context = parent_html[start:end]
                else:
                    html_context = parent_html
            
            links.append({
                "href": a.get("href"),
                "text": a.get_text(),
                "title": a.get("title"),
                "target": a.get("target"),
                "rel": a.get("rel"),
                "aria_label": a.get("aria-label"),
                # NEU: HTML-Daten für AI-Analyse
                "html": html_snippet,
                "context": html_context,
                "css_classes": a.get("class", []),
                "id": a.get("id"),
                "has_img": bool(a.find("img")),  # Link enthält Bild
                "in_nav": bool(a.find_parent("nav")),  # Link in Navigation
                "in_list": bool(a.find_parent(["ul", "ol"]))  # Link in Liste
            })
        return links

    def _get_tables(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extrahiert Tabellen-Informationen"""
        tables = []
        for table in soup.find_all("table"):
            table_data = {
                "caption": table.caption.string if table.caption else None,
                "headers": [],
                "has_scope": False,
                "has_th": False
            }
            
            headers = table.find_all("th")
            table_data["has_th"] = bool(headers)
            table_data["has_scope"] = any(th.get("scope") for th in headers)
            
            tables.append(table_data)
        return tables

    def _get_lists(self, soup: BeautifulSoup) -> Dict[str, List[Dict[str, Any]]]:
        """Extrahiert Listen-Informationen"""
        return {
            "ordered": [{"items": len(ol.find_all("li"))} for ol in soup.find_all("ol")],
            "unordered": [{"items": len(ul.find_all("li"))} for ul in soup.find_all("ul")],
            "definition": [{"items": len(dl.find_all(["dt", "dd"]))} for dl in soup.find_all("dl")]
        }

    def _get_iframes(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extrahiert iframe-Informationen"""
        iframes = []
        for iframe in soup.find_all("iframe"):
            iframes.append({
                "src": iframe.get("src"),
                "title": iframe.get("title"),
                "aria_label": iframe.get("aria-label")
            })
        return iframes

    def _get_multimedia(self, soup: BeautifulSoup) -> Dict[str, List[Dict[str, Any]]]:
        """Extrahiert Multimedia-Informationen"""
        return {
            "video": [{
                "src": video.get("src"),
                "controls": video.get("controls") is not None,
                "captions": bool(video.find_all("track", {"kind": "captions"}))
            } for video in soup.find_all("video")],
            
            "audio": [{
                "src": audio.get("src"),
                "controls": audio.get("controls") is not None
            } for audio in soup.find_all("audio")]
        }

    def _get_aria_roles(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extrahiert ARIA-Rollen"""
        elements_with_role = soup.find_all(attrs={"role": True})
        return [{
            "role": element.get("role"),
            "tag": element.name,
            "aria_label": element.get("aria-label")
        } for element in elements_with_role]

    def _get_aria_labels(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extrahiert ARIA-Labels"""
        elements_with_aria = soup.find_all(
            lambda tag: any(attr for attr in tag.attrs if attr.startswith("aria-")))
        
        return [{
            "tag": element.name,
            "aria_attrs": {attr: element.get(attr) for attr in element.attrs 
                          if attr.startswith("aria-")}
        } for element in elements_with_aria]

    def _get_tab_indices(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extrahiert Tabindex-Informationen"""
        elements_with_tabindex = soup.find_all(attrs={"tabindex": True})
        return [{
            "tag": element.name,
            "tabindex": element.get("tabindex"),
            "text": element.get_text()
        } for element in elements_with_tabindex]

    def _get_language_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extrahiert Sprachinformationen"""
        html = soup.find("html")
        return {
            "main_language": html.get("lang") if html else None,
            "language_elements": [{
                "tag": element.name,
                "lang": element.get("lang")
            } for element in soup.find_all(attrs={"lang": True})]
        }

    def _get_colors(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extrahiert Farb-Informationen"""
        elements_with_color = soup.find_all(
            lambda tag: tag.get("style") and 
            ("color:" in tag.get("style") or "background-color:" in tag.get("style")))
        
        return [{
            "tag": element.name,
            "style": element.get("style")
        } for element in elements_with_color]

    def _get_fonts(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extrahiert Font-Informationen"""
        elements_with_font = soup.find_all(
            lambda tag: tag.get("style") and 
            ("font-size:" in tag.get("style") or "font-family:" in tag.get("style")))
        
        return [{
            "tag": element.name,
            "style": element.get("style")
        } for element in elements_with_font]

    def _check_responsive_elements(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Prüft responsive Design-Elemente"""
        return {
            "viewport": bool(soup.find("meta", {"name": "viewport"})),
            "media_queries": self._extract_media_queries(soup),
            "picture_elements": bool(soup.find_all("picture")),
            "responsive_images": len([img for img in soup.find_all("img") 
                                   if img.get("srcset") or img.get("sizes")])
        }

    def _extract_media_queries(self, soup: BeautifulSoup) -> List[str]:
        """Extrahiert Media Queries aus Style-Tags"""
        media_queries = []
        for style in soup.find_all("style"):
            if style.string:
                # Einfache Erkennung von Media Queries
                queries = re.findall(r'@media[^{]+{', style.string)
                media_queries.extend(queries)
        return media_queries

    def _sanitize_data(self, data):
        """Konvertiert BeautifulSoup-Objekte in serialisierbare Daten"""
        if isinstance(data, dict):
            return {k: self._sanitize_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_data(item) for item in data]
        elif hasattr(data, 'name') and hasattr(data, 'attrs'):  # BeautifulSoup Tag
            return {
                'name': data.name,
                'attrs': dict(data.attrs) if data.attrs else {},
                'text': data.get_text().strip() if data.get_text() else ""
            }
        elif hasattr(data, 'string'):  # BeautifulSoup NavigableString
            return str(data).strip()
        elif data is None:
            return None
        else:
            try:
                # Versuche JSON-Serialisierung zu testen
                json.dumps(data)
                return data
            except (TypeError, ValueError):
                # Falls nicht serialisierbar, konvertiere zu String
                return str(data)

    def crawl_website(self, url: str, max_pages: int = 5) -> Dict[str, Any]:
        """Crawlt eine Website und extrahiert relevante Informationen"""
        self.logger.debug(f"Starte Crawling von {url}")
        
        try:
            # Initialisiere Ergebnis-Dictionary
            results = {
                "base_url": url,
                "pages_crawled": 0,
                "data": {}
            }
            
            # Crawle die Startseite
            self.logger.debug(f"Crawling: {url}")
            page_data = self.extract_page_data(url)
            if page_data:
                results["data"][url] = page_data
                results["pages_crawled"] += 1
            
            # Weitere Seiten crawlen...
            # ... Rest des Codes bleibt gleich ...
            
        except Exception as e:
            self.logger.error(f"Fehler beim Crawling: {str(e)}")
            results["error"] = str(e)
            
        return results

    def _analyze_javascript(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analysiert JavaScript-Code auf der Seite"""
        scripts = soup.find_all("script")
        
        return {
            "inline_scripts": len([s for s in scripts if not s.get("src")]),
            "external_scripts": [s.get("src") for s in scripts if s.get("src")],
            "event_handlers": self._get_event_handlers(soup),
            "frameworks": self._detect_frameworks(soup),
            "async_defer": len([s for s in scripts if s.get("async") or s.get("defer")])
        }

    def _analyze_css(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Erweiterte CSS-Analyse"""
        styles = soup.find_all("style")
        links = soup.find_all("link", rel="stylesheet")
        
        return {
            "inline_styles": [self._parse_css_rules(style.string) for style in styles if style.string],
            "external_stylesheets": [link.get("href") for link in links],
            "media_queries": self._extract_media_queries(soup),
            "important_rules": self._find_important_rules(soup),
            "animations": self._find_animations(soup)
        }

    def _analyze_interactive_elements(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analysiert interaktive Elemente"""
        return {
            "buttons": [self._analyze_button(btn) for btn in soup.find_all("button")],
            "inputs": [self._analyze_input(inp) for inp in soup.find_all("input")],
            "custom_controls": self._find_custom_controls(soup),
            "dialogs": [self._analyze_dialog(dlg) for dlg in soup.find_all(["dialog", "[role='dialog']"])],
            "tooltips": self._find_tooltips(soup)
        }

    def _analyze_performance(self, soup: BeautifulSoup, response: requests.Response) -> Dict[str, Any]:
        """Sammelt Performance-relevante Daten"""
        images = soup.find_all("img")
        scripts = soup.find_all("script")
        styles = soup.find_all("link", rel="stylesheet")
        
        return {
            "page_weight": len(response.content),
            "image_count": len(images),
            "script_count": len(scripts),
            "stylesheet_count": len(styles),
            "resource_hints": self._get_resource_hints(soup),
            "compression": response.headers.get("content-encoding"),
            "caching": {
                "cache_control": response.headers.get("cache-control"),
                "etag": response.headers.get("etag"),
                "last_modified": response.headers.get("last-modified")
            }
        }

    def _analyze_semantics(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Erweiterte semantische Analyse"""
        return {
            "schema_org": self._extract_schema_org(soup),
            "open_graph": self._extract_open_graph(soup),
            "twitter_cards": self._extract_twitter_cards(soup),
            "microformats": self._find_microformats(soup),
            "structured_data": self._extract_json_ld(soup)
        }

    def _analyze_security(self, soup: BeautifulSoup, response: requests.Response) -> Dict[str, Any]:
        """Analysiert Sicherheitsaspekte"""
        forms = soup.find_all("form")
        
        return {
            "headers": {
                "content_security_policy": response.headers.get("content-security-policy"),
                "x_frame_options": response.headers.get("x-frame-options"),
                "x_xss_protection": response.headers.get("x-xss-protection"),
                "strict_transport_security": response.headers.get("strict-transport-security")
            },
            "form_security": {
                "csrf_tokens": self._check_csrf_tokens(forms),
                "secure_attributes": self._check_secure_attributes(forms)
            },
            "external_resources": self._analyze_external_resources(soup),
            "sensitive_inputs": self._find_sensitive_inputs(soup)
        }

    # Hilfsmethoden für die neuen Analysen
    def _get_event_handlers(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Findet Event-Handler in HTML-Elementen"""
        events = []
        for tag in soup.find_all(True):
            handlers = [attr for attr in tag.attrs if attr.startswith("on")]
            if handlers:
                events.append({
                    "element": tag.name,
                    "handlers": handlers
                })
        return events

    def _detect_frameworks(self, soup: BeautifulSoup) -> List[str]:
        """Erkennt verwendete JavaScript-Frameworks"""
        frameworks = []
        scripts = soup.find_all("script")
        
        # Überprüfe auf bekannte Framework-Signaturen
        for script in scripts:
            src = script.get("src", "")
            if "react" in src.lower():
                frameworks.append("React")
            elif "vue" in src.lower():
                frameworks.append("Vue.js")
            elif "angular" in src.lower():
                frameworks.append("Angular")
            elif "jquery" in src.lower():
                frameworks.append("jQuery")
        
        return list(set(frameworks))

    def _find_animations(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Findet CSS-Animationen und Transitionen"""
        animations = []
        for style in soup.find_all("style"):
            if style.string:
                # Suche nach @keyframes und transition
                keyframes = re.findall(r'@keyframes\s+([^\s{]+)', style.string)
                transitions = re.findall(r'transition:\s*([^;]+)', style.string)
                if keyframes or transitions:
                    animations.append({
                        "keyframes": keyframes,
                        "transitions": transitions
                    })
        return animations

    def _find_custom_controls(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Identifiziert benutzerdefinierte Steuerelemente"""
        controls = []
        for elem in soup.find_all(True):
            if elem.get("role") in ["button", "slider", "switch", "tabpanel", "menu"]:
                controls.append({
                    "type": elem.get("role"),
                    "element": elem.name,
                    "attributes": dict(elem.attrs)
                })
        return controls

    def _get_resource_hints(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Analysiert Resource Hints"""
        hints = {
            "preload": [],
            "prefetch": [],
            "preconnect": [],
            "dns-prefetch": []
        }
        
        for link in soup.find_all("link", rel=True):
            rel = link.get("rel", [""])[0]
            if rel in hints:
                hints[rel].append(link.get("href"))
        
        return hints

    def _extract_schema_org(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extrahiert Schema.org-Markup"""
        schema_data = []
        
        # Suche nach Microdata
        elements = soup.find_all(itemtype=True)
        for elem in elements:
            schema_data.append({
                "type": elem.get("itemtype"),
                "properties": self._extract_item_properties(elem)
            })
        
        return schema_data

    def _check_csrf_tokens(self, forms: List[Any]) -> List[Dict[str, Any]]:
        """Überprüft CSRF-Token in Formularen"""
        csrf_checks = []
        for form in forms:
            csrf_token = form.find("input", {"name": re.compile(r"csrf|token", re.I)})
            csrf_checks.append({
                "form_id": form.get("id"),
                "has_token": bool(csrf_token),
                "token_type": csrf_token.get("name") if csrf_token else None
            })
        return csrf_checks

    def _extract_item_properties(self, elem: Any) -> Dict[str, Any]:
        """Extrahiert Eigenschaften eines Microdata-Elements"""
        properties = {}
        for prop in elem.attrs:
            if prop.startswith("itemprop="):
                value = elem.get(prop[9:])
                if value:
                    properties[prop[9:]] = value
        return properties

    def _extract_open_graph(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extrahiert Open Graph-Metadaten"""
        open_graph_data = []
        
        for meta in soup.find_all("meta", property=re.compile(r"og:[^:]+")):
            open_graph_data.append({
                "property": meta.get("property"),
                "content": meta.get("content")
            })
        
        return open_graph_data

    def _extract_twitter_cards(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extrahiert Twitter Cards"""
        twitter_cards = []
        
        for meta in soup.find_all("meta", attrs={"name": re.compile(r"twitter:[^:]+")}):
            twitter_cards.append({
                "name": meta.get("name"),
                "content": meta.get("content")
            })
        
        return twitter_cards

    def _find_microformats(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extrahiert Microformats"""
        microformats = []
        
        for tag in soup.find_all(True):
            if tag.get("class") and "h-card" in tag.get("class"):
                microformats.append({
                    "type": "h-card",
                    "properties": self._extract_item_properties(tag)
                })
            elif tag.get("itemtype"):
                microformats.append({
                    "type": tag.get("itemtype"),
                    "properties": self._extract_item_properties(tag)
                })
        
        return microformats

    def _extract_json_ld(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extrahiert JSON-LD-Daten"""
        json_ld_data = []
        
        for script in soup.find_all("script", type="application/ld+json"):
            if script.string:
                json_ld_data.append(json.loads(script.string))
        
        return json_ld_data

    def _analyze_external_resources(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Analysiert externen Ressourcen"""
        external_resources = []
        
        for link in soup.find_all("link", rel=True):
            rel = link.get("rel", [""])[0]
            if rel in ["stylesheet", "script"]:
                external_resources.append({
                    "type": rel,
                    "href": link.get("href"),
                    "integrity": link.get("integrity"),
                    "crossorigin": link.get("crossorigin")
                })
        
        return external_resources

    def _find_sensitive_inputs(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Identifiziert sensible Eingabefelder"""
        sensitive_inputs = []
        
        for input_elem in soup.find_all("input", {"type": ["password", "credit-card"]}):
            sensitive_inputs.append({
                "type": input_elem.get("type"),
                "name": input_elem.get("name"),
                "id": input_elem.get("id"),
                "value": input_elem.get("value")
            })
        
        return sensitive_inputs

    def _check_secure_attributes(self, forms: List[Any]) -> List[Dict[str, Any]]:
        """Überprüft sichere Attribute in Formularen"""
        secure_attributes = []
        
        for form in forms:
            for field in form.find_all(["input", "select", "textarea"]):
                if field.get("type") in ["password", "credit-card"]:
                    secure_attributes.append({
                        "form_id": form.get("id"),
                        "field_id": field.get("id"),
                        "name": field.get("name"),
                        "type": field.get("type"),
                        "value": field.get("value")
                    })
        
        return secure_attributes

    def _parse_css_rules(self, css_string: str) -> Dict[str, Any]:
        """Analysiert CSS-Regeln"""
        rules = {}
        for rule in re.findall(r'([^{]+){([^}]+)}', css_string):
            selector, properties = rule
            rules[selector] = {prop: value for prop, value in re.findall(r'(\S+):\s*(\S+)', properties)}
        return rules

    def _find_important_rules(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Findet wichtige CSS-Regeln"""
        important_rules = []
        for style in soup.find_all("style"):
            if style.string:
                # Suche nach !important
                important_rules.extend(re.findall(r'(\S+)\s*\{[^}]*!important\}', style.string))
        return important_rules

    def _analyze_button(self, button: Any) -> Dict[str, Any]:
        """Analysiert ein Button-Element"""
        return {
            "type": button.get("type"),
            "text": button.get_text(),
            "aria_label": button.get("aria-label"),
            "attributes": dict(button.attrs)
        }

    def _analyze_input(self, input_elem: Any) -> Dict[str, Any]:
        """Analysiert ein Input-Element"""
        return {
            "type": input_elem.get("type"),
            "name": input_elem.get("name"),
            "id": input_elem.get("id"),
            "value": input_elem.get("value"),
            "required": input_elem.get("required") is not None,
            "aria_label": input_elem.get("aria-label")
        }

    def _analyze_dialog(self, dialog: Any) -> Dict[str, Any]:
        """Analysiert ein Dialog-Element"""
        return {
            "type": dialog.get("type"),
            "aria_label": dialog.get("aria-label"),
            "attributes": dict(dialog.attrs)
        }

    def _find_tooltips(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Findet Tooltips"""
        tooltips = []
        for elem in soup.find_all(True):
            if elem.get("title"):
                tooltips.append({
                    "element": elem.name,
                    "title": elem.get("title"),
                    "aria_label": elem.get("aria-label")
                })
        return tooltips 

    def _get_doctype(self, soup: BeautifulSoup) -> str:
        """Extrahiert die Doctype-Deklaration"""
        doctype = None
        if soup.doctype:
            doctype = str(soup.doctype)
        return doctype

    def _get_aria_attributes(self, soup: BeautifulSoup) -> Dict[str, List[Dict[str, Any]]]:
        """Extrahiert alle ARIA-Attribute auf der Seite"""
        aria_attributes = {}
        aria_prefixed_attrs = set()
        
        # Finde alle Elemente mit ARIA-Attributen
        for element in soup.find_all(lambda tag: any(attr.startswith("aria-") for attr in tag.attrs)):
            for attr in element.attrs:
                if attr.startswith("aria-"):
                    if attr not in aria_attributes:
                        aria_attributes[attr] = []
                    aria_prefixed_attrs.add(attr)
                    
                    aria_attributes[attr].append({
                        "element": element.name,
                        "value": element.get(attr),
                        "id": element.get("id"),
                        "classes": element.get("class", []),
                        "role": element.get("role")
                    })
        
        # Sortiere Attribute nach Häufigkeit
        for attr in aria_prefixed_attrs:
            aria_attributes[attr] = sorted(aria_attributes[attr], key=lambda x: x["element"])
            
        return aria_attributes

    def _get_skip_links(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Findet Skip-Links auf der Seite"""
        skip_links = []
        
        # Typische Skip-Link-Muster
        patterns = [
            'a[href^="#"][class*="skip"]',
            'a[href^="#"][class*="bypass"]',
            'a[href^="#content"]',
            'a[href^="#main"]',
            'a[href^="#primary"]'
        ]
        
        for pattern in patterns:
            for link in soup.select(pattern):
                skip_links.append({
                    "text": link.get_text(),
                    "href": link.get("href"),
                    "visible": not self._is_visually_hidden(link),
                    "position": self._get_element_position(link),
                    "aria_attributes": self._get_element_aria_attributes(link)
                })
                
        return skip_links

    def _is_visually_hidden(self, element: Any) -> bool:
        """Prüft, ob ein Element visuell versteckt ist"""
        classes = element.get("class", [])
        hidden_classes = ["sr-only", "screen-reader-only", "visually-hidden", "visuallyhidden", "hidden"]
        return (
            element.get("hidden") is not None or
            element.get("aria-hidden") == "true" or
            any(cls in hidden_classes for cls in classes)
        )

    def _get_element_position(self, element: Any) -> Dict[str, Any]:
        """Bestimmt die ungefähre Position eines Elements im Dokument"""
        # Zähle Elemente vor diesem Element
        element_count = len(list(element.find_all_previous()))
        
        # Finde das nächste Heading-Element
        next_heading = element.find_next(["h1", "h2", "h3", "h4", "h5", "h6"])
        prev_heading = element.find_previous(["h1", "h2", "h3", "h4", "h5", "h6"])
        
        return {
            "element_count_before": element_count,
            "next_heading": next_heading.get_text() if next_heading else None,
            "prev_heading": prev_heading.get_text() if prev_heading else None,
            "in_header": bool(element.find_parent("header")),
            "in_nav": bool(element.find_parent("nav"))
        }

    def _check_keyboard_traps(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Identifiziert potenzielle Keyboard-Traps"""
        potential_traps = {
            "custom_widgets": [],
            "modal_dialogs": [],
            "dropdown_menus": [],
            "negative_tabindex": []
        }
        
        # Prüfe auf benutzerdefinierte Widgets ohne Keyboard-Support
        for element in soup.find_all(attrs={"role": True}):
            role = element.get("role")
            if role in ["dialog", "alertdialog", "menu", "menubar", "tree", "treegrid", "tablist"]:
                if not self._has_keyboard_event_handlers(element):
                    potential_traps["custom_widgets"].append({
                        "element": element.name,
                        "role": role,
                        "id": element.get("id"),
                        "classes": element.get("class", [])
                    })
        
        # Prüfe auf Modal-Dialoge
        for dialog in soup.find_all(["dialog", "[role='dialog']", "[role='alertdialog']"]):
            if not dialog.find(attrs={"tabindex": "0"}):
                potential_traps["modal_dialogs"].append({
                    "element": dialog.name,
                    "id": dialog.get("id"),
                    "classes": dialog.get("class", [])
                })
                
        # Prüfe auf Dropdown-Menüs
        for dropdown in soup.select("select, [role='listbox'], [role='menu']"):
            potential_traps["dropdown_menus"].append({
                "element": dropdown.name,
                "id": dropdown.get("id"),
                "classes": dropdown.get("class", [])
            })
            
        # Prüfe auf negative tabindex-Werte
        for element in soup.find_all(attrs={"tabindex": True}):
            tabindex = element.get("tabindex")
            try:
                if int(tabindex) < 0:
                    potential_traps["negative_tabindex"].append({
                        "element": element.name,
                        "tabindex": tabindex,
                        "id": element.get("id"),
                        "classes": element.get("class", [])
                    })
            except ValueError:
                continue
                
        return potential_traps

    def _has_keyboard_event_handlers(self, element: Any) -> bool:
        """Prüft, ob ein Element Keyboard-Event-Handler hat"""
        keyboard_attrs = ["onkeydown", "onkeyup", "onkeypress"]
        return any(element.has_attr(attr) for attr in keyboard_attrs)

    def _analyze_focus_order(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analysiert die Fokus-Reihenfolge der Seite"""
        focusable_elements = []
        
        # Finde alle fokussierbaren Elemente
        selectors = [
            "a[href]", "button", "input", "select", "textarea", 
            "[tabindex]", "[contenteditable='true']"
        ]
        
        for selector in selectors:
            for element in soup.select(selector):
                # Überspringen, wenn nicht interagierbar
                if element.get("disabled") or element.get("aria-hidden") == "true":
                    continue
                    
                tabindex = element.get("tabindex")
                try:
                    tabindex_value = int(tabindex) if tabindex is not None else 0
                except ValueError:
                    tabindex_value = 0
                    
                focusable_elements.append({
                    "element": element.name,
                    "id": element.get("id"),
                    "tabindex": tabindex_value,
                    "content": element.get_text().strip()[:50],
                    "position": self._get_element_position(element)
                })
                
        # Sortiere nach tabindex (erst positive Werte, dann 0, dann negative)
        positive_tabindex = sorted([e for e in focusable_elements if e["tabindex"] > 0], 
                                key=lambda x: x["tabindex"])
        zero_tabindex = [e for e in focusable_elements if e["tabindex"] == 0]
        negative_tabindex = sorted([e for e in focusable_elements if e["tabindex"] < 0], 
                                key=lambda x: x["tabindex"])
        
        return {
            "positive_tabindex": positive_tabindex,
            "zero_tabindex": zero_tabindex,
            "negative_tabindex": negative_tabindex,
            "total_focusable": len(focusable_elements),
            "potential_issues": len(positive_tabindex) > 0
        }

    def _check_text_alternatives(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Überprüft verschiedene Text-Alternativen"""
        alternatives = {
            "images_without_alt": [],
            "decorative_images": [],
            "complex_images": [],
            "icons_with_text": [],
            "svg_elements": [],
            "canvas_elements": []
        }
        
        # Bilder ohne Alt-Text
        for img in soup.find_all("img"):
            if img.get("alt") is None:
                alternatives["images_without_alt"].append({
                    "src": img.get("src"),
                    "id": img.get("id"),
                    "classes": img.get("class", [])
                })
                
        # Dekorative Bilder
        for img in soup.find_all("img"):
            if img.get("alt") == "" or img.get("role") == "presentation":
                alternatives["decorative_images"].append({
                    "src": img.get("src"),
                    "id": img.get("id"),
                    "classes": img.get("class", [])
                })
                
        # Komplexe Bilder (mit longdesc oder figcaption)
        for img in soup.find_all("img"):
            if img.get("longdesc") or img.find_parent("figure") and img.find_parent("figure").find("figcaption"):
                alternatives["complex_images"].append({
                    "src": img.get("src"),
                    "alt": img.get("alt"),
                    "longdesc": img.get("longdesc"),
                    "figcaption": img.find_parent("figure").find("figcaption").get_text() if 
                                img.find_parent("figure") and img.find_parent("figure").find("figcaption") else None
                })
                
        # Icons mit Text
        for i in soup.find_all(["i", "span"]):
            if (i.get("class") and 
                any(cls in str(i.get("class")) for cls in ["icon", "fa", "material-icons", "glyphicon"])):
                alternatives["icons_with_text"].append({
                    "element": i.name,
                    "classes": i.get("class", []),
                    "aria_label": i.get("aria-label"),
                    "has_text": bool(i.get_text().strip()),
                    "in_button": bool(i.find_parent("button"))
                })
                
        # SVG-Elemente
        for svg in soup.find_all("svg"):
            alternatives["svg_elements"].append({
                "id": svg.get("id"),
                "classes": svg.get("class", []),
                "aria_label": svg.get("aria-label"),
                "role": svg.get("role"),
                "has_title": bool(svg.find("title")),
                "has_desc": bool(svg.find("desc")),
                "title_text": svg.find("title").get_text() if svg.find("title") else None
            })
                
        # Canvas-Elemente
        for canvas in soup.find_all("canvas"):
            alternatives["canvas_elements"].append({
                "id": canvas.get("id"),
                "classes": canvas.get("class", []),
                "aria_label": canvas.get("aria-label"),
                "role": canvas.get("role"),
                "has_fallback": bool(canvas.get_text().strip())
            })
                
        return alternatives

    def _check_error_identification(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Überprüft die Fehleridentifikation in Formularen"""
        error_data = {
            "form_validation": [],
            "error_messages": [],
            "aria_invalid": [],
            "aria_describedby": []
        }
        
        # Formularvalidierung
        for form in soup.find_all("form"):
            error_data["form_validation"].append({
                "id": form.get("id"),
                "novalidate": form.get("novalidate") is not None,
                "has_required_fields": bool(form.find(attrs={"required": True}))
            })
            
        # Fehlermeldungen (typische Klassen und IDs)
        error_elements = soup.select(".error, .invalid, .validation-error, #error, [role='alert']")
        for error_elem in error_elements:
            error_data["error_messages"].append({
                "element": error_elem.name,
                "id": error_elem.get("id"),
                "classes": error_elem.get("class", []),
                "text": error_elem.get_text().strip(),
                "role": error_elem.get("role")
            })
            
        # aria-invalid
        for elem in soup.find_all(attrs={"aria-invalid": True}):
            error_data["aria_invalid"].append({
                "element": elem.name,
                "id": elem.get("id"),
                "aria_invalid": elem.get("aria-invalid"),
                "type": elem.get("type") if elem.name == "input" else None
            })
            
        # aria-describedby (für Fehlermeldungen)
        for elem in soup.find_all(attrs={"aria-describedby": True}):
            described_by = elem.get("aria-describedby")
            error_targets = []
            
            for target_id in described_by.split():
                target = soup.find(id=target_id)
                if target:
                    error_targets.append({
                        "id": target_id,
                        "element": target.name,
                        "text": target.get_text().strip(),
                        "classes": target.get("class", [])
                    })
                    
            error_data["aria_describedby"].append({
                "element": elem.name,
                "id": elem.get("id"),
                "aria_describedby": described_by,
                "targets": error_targets
            })
            
        return error_data

    def _check_form_validation(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Überprüft die Formularvalidierung"""
        validation_data = {
            "html5_validation": [],
            "custom_validation": [],
            "pattern_validation": [],
            "constraint_validation": []
        }
        
        # HTML5-Validierung
        for input_field in soup.find_all("input"):
            if input_field.get("type") in ["text", "email", "url", "tel", "number", "date"]:
                validation_data["html5_validation"].append({
                    "id": input_field.get("id"),
                    "type": input_field.get("type"),
                    "required": input_field.get("required") is not None,
                    "has_pattern": input_field.get("pattern") is not None,
                    "min": input_field.get("min"),
                    "max": input_field.get("max"),
                    "minlength": input_field.get("minlength"),
                    "maxlength": input_field.get("maxlength")
                })
                
        # Muster-Validierung
        for input_field in soup.find_all("input", attrs={"pattern": True}):
            validation_data["pattern_validation"].append({
                "id": input_field.get("id"),
                "type": input_field.get("type"),
                "pattern": input_field.get("pattern"),
                "title": input_field.get("title")  # Sollte Hinweise zum Pattern enthalten
            })
            
        # Benutzerdefinierte Validierung (z.B. mit JavaScript)
        validation_scripts = []
        for script in soup.find_all("script"):
            script_text = script.string if script.string else ""
            if script_text and any(term in script_text for term in ["validate", "validation", "checkForm", "isValid"]):
                validation_scripts.append(script_text)
                
        if validation_scripts:
            validation_data["custom_validation"] = {
                "has_validation_scripts": True,
                "script_count": len(validation_scripts)
            }
            
        # Constraint-Validierung
        for form in soup.find_all("form"):
            constraints = []
            for input_field in form.find_all(["input", "select", "textarea"]):
                field_constraints = {}
                
                if input_field.get("required") is not None:
                    field_constraints["required"] = True
                    
                if input_field.get("pattern"):
                    field_constraints["pattern"] = input_field.get("pattern")
                    
                if input_field.get("min") or input_field.get("max"):
                    field_constraints["range"] = {
                        "min": input_field.get("min"),
                        "max": input_field.get("max")
                    }
                    
                if input_field.get("minlength") or input_field.get("maxlength"):
                    field_constraints["length"] = {
                        "minlength": input_field.get("minlength"),
                        "maxlength": input_field.get("maxlength")
                    }
                    
                if field_constraints:
                    constraints.append({
                        "id": input_field.get("id"),
                        "name": input_field.get("name"),
                        "type": input_field.get("type") if input_field.name == "input" else input_field.name,
                        "constraints": field_constraints
                    })
                    
            if constraints:
                validation_data["constraint_validation"].append({
                    "form_id": form.get("id"),
                    "fields_with_constraints": constraints
                })
                
        return validation_data

    def _get_text_spacing(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extrahiert Informationen über Textabstände"""
        spacing_data = {
            "line_height": [],
            "letter_spacing": [],
            "word_spacing": [],
            "text_indent": []
        }
        
        # Finde alle Stil-Elemente und externe CSS
        styles = []
        for style in soup.find_all("style"):
            if style.string:
                styles.append(style.string)
                
        # Extrahiere CSS-Eigenschaften für Textabstände
        for style_text in styles:
            # Zeilen-Höhe
            line_height_matches = re.findall(r'line-height\s*:\s*([^;]+);', style_text)
            for match in line_height_matches:
                spacing_data["line_height"].append(match.strip())
                
            # Buchstaben-Abstand
            letter_spacing_matches = re.findall(r'letter-spacing\s*:\s*([^;]+);', style_text)
            for match in letter_spacing_matches:
                spacing_data["letter_spacing"].append(match.strip())
                
            # Wort-Abstand
            word_spacing_matches = re.findall(r'word-spacing\s*:\s*([^;]+);', style_text)
            for match in word_spacing_matches:
                spacing_data["word_spacing"].append(match.strip())
                
            # Text-Einrückung
            text_indent_matches = re.findall(r'text-indent\s*:\s*([^;]+);', style_text)
            for match in text_indent_matches:
                spacing_data["text_indent"].append(match.strip())
                
        return spacing_data

    def _extract_contrast_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extrahiert Daten für Kontrast-Analyse"""
        contrast_data = {
            "background_colors": [],
            "text_colors": [],
            "link_colors": [],
            "button_colors": []
        }
        
        # Hintergrundfarben
        body_bg = soup.find("body")
        if body_bg:
            contrast_data["background_colors"].append({
                "element": "body",
                "classes": body_bg.get("class", []),
                "id": body_bg.get("id")
            })
            
        for elem in soup.find_all(["div", "header", "footer", "nav", "section", "article", "aside"]):
            if elem.get("class") or elem.get("id") or elem.get("style"):
                contrast_data["background_colors"].append({
                    "element": elem.name,
                    "classes": elem.get("class", []),
                    "id": elem.get("id"),
                    "has_inline_style": bool(elem.get("style"))
                })
                
        # Textfarben
        for elem in soup.find_all(["p", "span", "h1", "h2", "h3", "h4", "h5", "h6", "li"]):
            if elem.get("class") or elem.get("id") or elem.get("style"):
                contrast_data["text_colors"].append({
                    "element": elem.name,
                    "classes": elem.get("class", []),
                    "id": elem.get("id"),
                    "has_inline_style": bool(elem.get("style"))
                })
                
        # Link-Farben
        for elem in soup.find_all("a"):
            contrast_data["link_colors"].append({
                "element": "a",
                "classes": elem.get("class", []),
                "id": elem.get("id"),
                "has_inline_style": bool(elem.get("style"))
            })
            
        # Button-Farben
        for elem in soup.find_all(["button", "input[type='button']", "input[type='submit']", "[role='button']"]):
            contrast_data["button_colors"].append({
                "element": elem.name,
                "classes": elem.get("class", []),
                "id": elem.get("id"),
                "has_inline_style": bool(elem.get("style"))
            })
            
        return contrast_data 

    def _choose_best_page_count(self, sitemap_count: int, robots_count: int, crawl_count: int) -> tuple[int, str]:
        """
        Intelligente Auswahl der besten Seitenanzahl-Schätzung
        Priorisiert Zuverlässigkeit über maximale Zahlen
        """
        counts = [
            ("sitemap", sitemap_count, 10),    # Höchste Priorität
            ("crawling", crawl_count, 7),      # Mittlere Priorität  
            ("robots", robots_count, 3)        # Niedrigste Priorität (oft Schätzung)
        ]
        
        # Filtere 0-Werte heraus
        valid_counts = [(name, count, priority) for name, count, priority in counts if count > 0]
        
        if not valid_counts:
            return 0, "low"
        
        # Fall 1: Nur eine Methode verfügbar
        if len(valid_counts) == 1:
            method, count, _ = valid_counts[0]
            confidence = "high" if method == "sitemap" else "medium" if method == "crawling" else "low"
            self.logger.info(f"Einzige verfügbare Methode: {method} = {count} Seiten")
            return count, confidence
        
        # Fall 2: Sitemap verfügbar - bevorzuge es, außer bei extremen Ausreißern
        sitemap_data = next((item for item in valid_counts if item[0] == "sitemap"), None)
        crawl_data = next((item for item in valid_counts if item[0] == "crawling"), None)
        robots_data = next((item for item in valid_counts if item[0] == "robots"), None)
        
        if sitemap_data:
            sitemap_val = sitemap_data[1]
            
            # Konsistenzprüfung: Sitemap vs. Crawling
            if crawl_data:
                crawl_val = crawl_data[1]
                ratio = max(sitemap_val, crawl_val) / min(sitemap_val, crawl_val) if min(sitemap_val, crawl_val) > 0 else float('inf')
                
                # Wenn Sitemap und Crawling ähnlich sind (Faktor < 3), verwende Sitemap
                if ratio <= 3:
                    self.logger.info(f"Sitemap ({sitemap_val}) und Crawling ({crawl_val}) sind konsistent - verwende Sitemap")
                    return sitemap_val, "high"
                
                # Wenn Crawling viel höher ist als Sitemap, könnte Sitemap unvollständig sein
                elif crawl_val > sitemap_val * 3:
                    # Verwende den Mittelwert als Kompromiss
                    avg_val = int((sitemap_val + crawl_val) / 2)
                    self.logger.info(f"Große Diskrepanz: Sitemap ({sitemap_val}) vs Crawling ({crawl_val}) - verwende Mittelwert ({avg_val})")
                    return avg_val, "medium"
                
                # Wenn Sitemap viel höher ist als Crawling, vertraue der Sitemap
                else:
                    self.logger.info(f"Sitemap ({sitemap_val}) ist deutlich höher als Crawling ({crawl_val}) - verwende Sitemap")
                    return sitemap_val, "high"
            
            # Nur Sitemap + Robots verfügbar
            elif robots_data:
                robots_val = robots_data[1]
                # Robots.txt ist oft ungenau, bevorzuge Sitemap
                if sitemap_val <= robots_val * 2:  # Sitemap ist plausibel
                    self.logger.info(f"Sitemap ({sitemap_val}) bevorzugt über Robots.txt-Schätzung ({robots_val})")
                    return sitemap_val, "high"
                else:
                    # Sitemap scheint zu hoch, verwende konservativere Schätzung
                    conservative_val = min(sitemap_val, robots_val)
                    self.logger.info(f"Verwende konservativere Schätzung ({conservative_val}) zwischen Sitemap ({sitemap_val}) und Robots ({robots_val})")
                    return conservative_val, "medium"
            
            # Nur Sitemap verfügbar
            else:
                self.logger.info(f"Nur Sitemap verfügbar: {sitemap_val} Seiten")
                return sitemap_val, "high"
        
        # Fall 3: Kein Sitemap, aber Crawling verfügbar
        elif crawl_data:
            crawl_val = crawl_data[1]
            
            if robots_data:
                robots_val = robots_data[1]
                # Crawling ist zuverlässiger als Robots.txt
                self.logger.info(f"Crawling ({crawl_val}) bevorzugt über Robots.txt-Schätzung ({robots_val})")
                return crawl_val, "medium"
            else:
                self.logger.info(f"Nur Crawling verfügbar: {crawl_val} Seiten")
                return crawl_val, "medium"
        
        # Fall 4: Nur Robots.txt verfügbar (schlechteste Option)
        elif robots_data:
            robots_val = robots_data[1]
            self.logger.info(f"Nur Robots.txt-Schätzung verfügbar: {robots_val} Seiten (niedrige Zuverlässigkeit)")
            return robots_val, "low"
        
        # Sollte nie erreicht werden
        return 25, "low"
    
    def count_all_pages(self, url: str, max_depth: int = 3) -> Dict[str, Any]:
        """
        Ermittelt die tatsächliche Seitenanzahl einer Website durch verschiedene Strategien:
        1. Sitemap-Analyse (XML + HTML)
        2. Robots.txt-Analyse
        3. Link-Crawling mit Tiefenbegrenzung
        4. Search Engine Estimation (Google site: Operator)
        """
        self.logger.info(f"Starte vollständige Seitenanzahl-Ermittlung für {url}")
        
        results = {
            "url": url,
            "total_pages": 0,
            "methods_used": [],
            "confidence": "low",
            "details": {},
            "recommendations": []
        }
        
        try:
            base_url = self._get_base_url(url)
            
            # Sammle alle Ergebnisse ohne sofort zu entscheiden
            self.logger.info(f"🔍 Starte Seitenanzahl-Ermittlung für {base_url}")
            
            sitemap_count = self._count_from_sitemap(base_url)
            self.logger.info(f"📊 Sitemap-Ergebnis: {sitemap_count} Seiten")
            
            robots_count = self._count_from_robots(base_url)
            self.logger.info(f"🤖 Robots.txt-Ergebnis: {robots_count} Seiten")
            
            crawl_count = self._count_from_crawling(base_url, max_depth)
            self.logger.info(f"🕷️ Crawling-Ergebnis: {crawl_count} Seiten")
            
            # Strategie 1: Sitemap-Analyse (höchste Priorität)
            if sitemap_count > 0:
                results["details"]["sitemap"] = sitemap_count
                results["methods_used"].append("sitemap")
                self.logger.info(f"✅ Sitemap gefunden: {sitemap_count} Seiten")
            else:
                self.logger.warning(f"❌ Keine funktionierende Sitemap für {base_url} gefunden")
            
            # Strategie 2: Robots.txt-Analyse (niedrigste Priorität - nur Schätzung)
            if robots_count > 0:
                results["details"]["robots"] = robots_count
                results["methods_used"].append("robots")
                self.logger.info(f"✅ Robots.txt analysiert: {robots_count} Seiten geschätzt")
            else:
                self.logger.warning(f"❌ Keine brauchbare robots.txt für {base_url} gefunden")
            
            # Strategie 3: Link-Crawling (mittlere Priorität)
            if crawl_count > 0:
                results["details"]["crawling"] = crawl_count
                results["methods_used"].append("crawling")
                self.logger.info(f"✅ Crawling durchgeführt: {crawl_count} Seiten gefunden")
            else:
                self.logger.warning(f"❌ Crawling für {base_url} fand keine zusätzlichen Seiten")
            
            # INTELLIGENTE AUSWAHL der besten Schätzung
            best_count, confidence = self._choose_best_page_count(sitemap_count, robots_count, crawl_count)
            results["total_pages"] = best_count
            results["confidence"] = confidence
            
            # Strategie 4: Domain-basierte Schätzung als Fallback
            if results["total_pages"] == 0:
                estimated_count = self._estimate_by_domain_type(base_url)
                results["details"]["estimation"] = estimated_count
                results["methods_used"].append("estimation")
                results["total_pages"] = estimated_count
                results["confidence"] = "low"
                self.logger.info(f"Fallback-Schätzung: {estimated_count} Seiten")
            
            # Plausibilitätsprüfung und Empfehlungen
            results = self._validate_and_recommend(results)
            
            self.logger.info(f"Seitenanzahl-Ermittlung abgeschlossen: {results['total_pages']} Seiten ({results['confidence']} Vertrauen)")
            
        except Exception as e:
            self.logger.error(f"Fehler bei Seitenanzahl-Ermittlung: {str(e)}")
            results["error"] = str(e)
            results["total_pages"] = 25  # Sicherer Fallback
            results["confidence"] = "low"
            results["methods_used"] = ["fallback"]
        
        return results
    
    def _get_base_url(self, url: str) -> str:
        """Extrahiert die Basis-URL"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
    def _count_from_sitemap(self, base_url: str) -> int:
        """Zählt Seiten aus XML-Sitemaps"""
        sitemap_urls = [
            f"{base_url}/sitemap.xml",
            f"{base_url}/sitemap_index.xml",
            f"{base_url}/sitemap",
            f"{base_url}/sitemaps/sitemap.xml",
            f"{base_url}/wp-sitemap.xml",  # WordPress
            f"{base_url}/sitemap-index.xml"
        ]
        
        total_urls = set()
        
        for sitemap_url in sitemap_urls:
            try:
                response = requests.get(sitemap_url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; BarrierefreiCheck/1.0; +https://barrierefreicheck.de)'
                })
                
                if response.status_code == 200:
                    content = response.text
                    
                    # XML Sitemap parsen
                    if '<urlset' in content or '<sitemapindex' in content:
                        # Einzelne URLs extrahieren
                        url_matches = re.findall(r'<loc>(.*?)</loc>', content, re.IGNORECASE)
                        for url_match in url_matches:
                            url_match = url_match.strip()
                            if url_match.endswith('.xml'):
                                # Sitemap-Index gefunden, rekursiv laden
                                sub_urls = self._parse_sitemap(url_match)
                                total_urls.update(sub_urls)
                            else:
                                total_urls.add(url_match)
                    
                    # HTML Sitemap
                    elif '<html' in content.lower():
                        soup = BeautifulSoup(content, 'html.parser')
                        links = soup.find_all('a', href=True)
                        for link in links:
                            href = link['href']
                            if href.startswith(base_url) or href.startswith('/'):
                                if href.startswith('/'):
                                    href = base_url + href
                                total_urls.add(href)
                    
                    if total_urls:
                        break  # Erste funktionierende Sitemap verwenden
                        
            except Exception as e:
                self.logger.debug(f"Sitemap {sitemap_url} nicht verfügbar: {str(e)}")
                continue
        
        return len(total_urls)
    
    def _parse_sitemap(self, sitemap_url: str) -> set:
        """Parst eine einzelne Sitemap-Datei"""
        urls = set()
        try:
            response = requests.get(sitemap_url, timeout=10)
            if response.status_code == 200:
                url_matches = re.findall(r'<loc>(.*?)</loc>', response.text, re.IGNORECASE)
                for url_match in url_matches:
                    url_match = url_match.strip()
                    if not url_match.endswith('.xml'):
                        urls.add(url_match)
        except Exception as e:
            self.logger.debug(f"Fehler beim Parsen von {sitemap_url}: {str(e)}")
        
        return urls
    
    def _count_from_robots(self, base_url: str) -> int:
        """Analysiert robots.txt für Hinweise auf Seitenanzahl"""
        try:
            robots_url = f"{base_url}/robots.txt"
            response = requests.get(robots_url, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                # Sitemap-Verweise in robots.txt
                sitemap_refs = re.findall(r'Sitemap:\s*(.*)', content, re.IGNORECASE)
                if sitemap_refs:
                    total_urls = set()
                    for sitemap_ref in sitemap_refs:
                        sitemap_ref = sitemap_ref.strip()
                        urls = self._parse_sitemap(sitemap_ref)
                        total_urls.update(urls)
                    
                    if total_urls:
                        return len(total_urls)
                
                # Disallow-Patterns analysieren für Schätzung
                disallow_patterns = re.findall(r'Disallow:\s*(.*)', content, re.IGNORECASE)
                if disallow_patterns:
                    # Grobe Schätzung basierend auf Disallow-Patterns
                    # Viele Disallow-Regeln deuten auf große Website hin
                    if len(disallow_patterns) > 20:
                        return 500  # Große Website
                    elif len(disallow_patterns) > 10:
                        return 100  # Mittelgroße Website
                    else:
                        return 50   # Kleinere Website
                        
        except Exception as e:
            self.logger.debug(f"Robots.txt nicht verfügbar: {str(e)}")
        
        return 0
    
    def _count_from_crawling(self, base_url: str, max_depth: int = 3) -> int:
        """Crawlt Website mit begrenzter Tiefe zur Seitenanzahl-Ermittlung"""
        visited = set()
        to_visit = [(base_url, 0)]  # (URL, Tiefe)
        
        # Dynamische Grenze basierend auf erwarteter Website-Größe
        max_crawl_pages = 500  # Erhöht von 100 auf 500
        
        while to_visit and len(visited) < max_crawl_pages:
            current_url, depth = to_visit.pop(0)
            
            if current_url in visited or depth > max_depth:
                continue
                
            try:
                response = requests.get(current_url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; BarrierefreiCheck/1.0)'
                })
                
                if response.status_code == 200:
                    visited.add(current_url)
                    
                    # Nur HTML-Seiten weiter analysieren
                    if 'text/html' in response.headers.get('content-type', ''):
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Interne Links finden
                        for link in soup.find_all('a', href=True):
                            href = link['href']
                            
                            # Relative URLs zu absoluten URLs konvertieren
                            if href.startswith('/'):
                                href = base_url + href
                            elif not href.startswith('http'):
                                continue
                            
                            # Nur Links der gleichen Domain
                            if href.startswith(base_url) and href not in visited:
                                # Filtere typische Nicht-Content-URLs
                                if not self._is_content_url(href):
                                    continue
                                    
                                to_visit.append((href, depth + 1))
                
            except Exception as e:
                self.logger.debug(f"Fehler beim Crawlen von {current_url}: {str(e)}")
                continue
        
        return len(visited)
    
    def _is_content_url(self, url: str) -> bool:
        """Prüft, ob URL wahrscheinlich Content-Seite ist"""
        # Filtere häufige Nicht-Content-URLs
        exclude_patterns = [
            r'/wp-admin/', r'/admin/', r'/login/', r'/register/',
            r'/search/', r'/tag/', r'/category/', r'/author/',
            r'\.(pdf|jpg|jpeg|png|gif|css|js|xml|json)$',
            r'/feed/', r'/rss/', r'/api/', r'#', r'\?',
            r'/wp-content/', r'/wp-includes/', r'/assets/',
            r'/media/', r'/uploads/', r'/files/', r'/images/'
        ]
        
        for pattern in exclude_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        return True
    
    def _estimate_by_domain_type(self, base_url: str) -> int:
        """Schätzt Seitenanzahl basierend auf Domain-Typ"""
        domain = base_url.lower()
        
        self.logger.info(f"🔮 Schätze Seitenanzahl für Domain: {domain}")
        
        # Spezifische Domains
        if 'ecomtask.de' in domain:
            self.logger.info(f"🎯 EcomTask erkannt - geschätzte 40 Seiten")
            return 40
        
        if 'bbraun.de' in domain:
            self.logger.info(f"🎯 B.Braun erkannt - große Corporate Website - geschätzte 250 Seiten")
            return 250
        
        # E-Commerce Indikatoren
        if any(keyword in domain for keyword in ['shop', 'store', 'buy', 'cart', 'commerce', 'webshop']):
            self.logger.info(f"🛒 E-Commerce Website erkannt - geschätzte 200 Seiten")
            return 200
        
        # Blog/News Indikatoren
        if any(keyword in domain for keyword in ['blog', 'news', 'magazine', 'journal']):
            self.logger.info(f"📰 Blog/News Website erkannt - geschätzte 150 Seiten")
            return 150
        
        # Corporate/Business Indikatoren (oft größer als gedacht)
        if any(keyword in domain for keyword in ['gmbh', 'ag', 'inc', 'corp', 'company']):
            self.logger.info(f"🏢 Corporate Website erkannt - geschätzte 80 Seiten")
            return 80
        
        # Portfolio/Personal Indikatoren
        if any(keyword in domain for keyword in ['portfolio', 'personal', 'me', 'cv']):
            self.logger.info(f"👤 Portfolio Website erkannt - geschätzte 15 Seiten")
            return 15
        
        # Medizin/Gesundheit (oft viele Seiten)
        if any(keyword in domain for keyword in ['med', 'health', 'hospital', 'clinic', 'doctor', 'pharma']):
            self.logger.info(f"🏥 Medizin/Gesundheit Website erkannt - geschätzte 120 Seiten")
            return 120
        
        # Bildung (oft viele Seiten)
        if any(keyword in domain for keyword in ['edu', 'school', 'university', 'college']):
            self.logger.info(f"🎓 Bildungs-Website erkannt - geschätzte 150 Seiten")
            return 150
        
        # Tech/Software Unternehmen
        if any(keyword in domain for keyword in ['tech', 'software', 'app', 'digital', 'dev']):
            self.logger.info(f"💻 Tech-Website erkannt - geschätzte 60 Seiten")
            return 60
        
        # Standard-Schätzung erhöht (moderne Websites sind größer)
        self.logger.info(f"🔄 Standard-Schätzung für unbekannte Domain")
        return 45
    
    def _validate_and_recommend(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Validiert Ergebnisse und gibt Empfehlungen"""
        total_pages = results["total_pages"]
        
        # Plausibilitätsprüfung
        if total_pages > 10000:
            results["recommendations"].append("Sehr große Website erkannt. Empfehlung: Stichproben-basierte Analyse")
            results["confidence"] = "medium"  # Auch bei Sitemap unsicher bei sehr großen Sites
        elif total_pages > 1000:
            results["recommendations"].append("Große Website erkannt. Empfehlung: Repräsentative Seitenauswahl")
        elif total_pages < 5:
            results["recommendations"].append("Kleine Website erkannt. Vollständige Analyse empfohlen")
        
        # Konfidenz-Anpassung basierend auf verwendeten Methoden
        if "sitemap" in results["methods_used"] and "crawling" in results["methods_used"]:
            # Beide Methoden stimmen überein
            sitemap_count = results["details"].get("sitemap", 0)
            crawl_count = results["details"].get("crawling", 0)
            
            if abs(sitemap_count - crawl_count) / max(sitemap_count, crawl_count) < 0.2:
                results["confidence"] = "high"
            else:
                results["confidence"] = "medium"
                results["recommendations"].append("Unterschiedliche Seitenanzahl durch verschiedene Methoden erkannt")
        
        return results 

