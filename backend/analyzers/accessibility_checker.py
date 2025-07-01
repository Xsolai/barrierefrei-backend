from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
from typing import List, Dict, Any, Tuple
import logging
import time
import re
import json
import math
import colorsys
from urllib.parse import urljoin
from contextlib import contextmanager

class AccessibilityChecker:
    def __init__(self):
        self.setup_logging()
        self.driver = None

    def setup_logging(self):
        logging.basicConfig(
            level=logging.DEBUG,  # Änderung zu DEBUG für detailliertere Logs
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    @contextmanager
    def get_webdriver(self):
        """Sicheres WebDriver-Management mit Context Manager"""
        driver = None
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            self.logger.debug("Initialisiere Chrome WebDriver")
            try:
                driver_path = ChromeDriverManager().install()
                self.logger.info(f"Ursprünglicher Pfad von ChromeDriverManager: {driver_path}")
                # Korrekturversuch für den Pfad
                if driver_path.endswith("THIRD_PARTY_NOTICES.chromedriver"):
                    corrected_driver_path = driver_path.replace("THIRD_PARTY_NOTICES.chromedriver", "chromedriver")
                    self.logger.info(f"Korrigierter Pfad für ChromeDriver: {corrected_driver_path}")
                    service = Service(executable_path=corrected_driver_path)
                else:
                    service = Service(executable_path=driver_path)
            except Exception as e:
                self.logger.error(f"Fehler beim automatischen Download/Pfadkorrektur des ChromeDriver: {str(e)}")
                raise

            driver = webdriver.Chrome(service=service, options=chrome_options)
            self.logger.debug("Chrome WebDriver erfolgreich initialisiert")
            
            yield driver
        except Exception as e:
            self.logger.error(f"Fehler beim WebDriver-Setup: {str(e)}")
            raise
        finally:
            if driver:
                self.logger.debug("Beende Chrome WebDriver")
                driver.quit()

    def analyze_website(self, url: str, depth: int = 1) -> Dict[str, Any]:
        self.logger.info(f"Starte Analyse für URL: {url}")
        
        try:
            with self.get_webdriver() as driver:
                self.logger.debug(f"Versuche URL zu laden: {url}")
                driver.get(url)
                
                # Warte auf das Laden der Seite
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                self.logger.debug("Seite erfolgreich geladen")
                
                results = {
                    "url": url,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "violations": [],
                    "warnings": [],
                    "passed": []
                }
                
                # Führe alle Checks in einem try-except Block aus
                checks = [
                    self._check_images_alt,
                    self._check_keyboard_navigation,
                    self._check_skip_links,
                    self._check_heading_structure,
                    self._check_color_contrast,
                    self._check_form_labels,
                    self._check_language_declaration,
                    self._check_responsive_design,
                    self._check_aria_roles,
                    self._check_page_title,
                    self._check_landmarks,
                    self._check_link_names,
                    self._check_form_validation,
                    self._check_focus_visible,
                    self._check_text_spacing,
                    self._check_tables
                ]
                
                for check in checks:
                    try:
                        check(results, driver)
                        self.logger.debug(f"Check {check.__name__} erfolgreich durchgeführt")
                    except Exception as e:
                        self.logger.error(f"Fehler bei {check.__name__}: {str(e)}")
                        results["warnings"].append({
                            "type": "check_error",
                            "severity": "warning",
                            "message": f"Fehler bei der Durchführung von {check.__name__}",
                            "error": str(e)
                        })
                
                return results
                
        except Exception as e:
            self.logger.error(f"Kritischer Fehler bei der Analyse: {str(e)}")
            return {
                "error": str(e),
                "type": "critical",
                "url": url,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

    def _sanitize_element(self, element):
        """Konvertiert ein Selenium WebElement in serialisierbare Daten"""
        if element is None:
            return None
        
        try:
            return {
                'tag_name': element.tag_name,
                'text': element.text,
                'attributes': {
                    'class': element.get_attribute('class'),
                    'id': element.get_attribute('id'),
                    'href': element.get_attribute('href'),
                    'src': element.get_attribute('src'),
                    'alt': element.get_attribute('alt'),
                    'aria-label': element.get_attribute('aria-label'),
                    'role': element.get_attribute('role')
                }
            }
        except:
            return str(element)

    def _check_images_alt(self, results: Dict[str, Any], driver: webdriver.Chrome):
        """Prüft Bilder auf Alt-Texte"""
        images = driver.find_elements(By.TAG_NAME, "img")
        for img in images:
            try:
                alt = img.get_attribute("alt")
                src = img.get_attribute("src")
                if not alt:
                    results["violations"].append({
                        "type": "missing_alt",
                        "element": "img",
                        "severity": "error",
                        "message": "Bild ohne Alt-Text gefunden",
                        "element_info": self._sanitize_element(img)
                    })
            except Exception as e:
                self.logger.warning(f"Fehler bei der Bildanalyse: {str(e)}")

    def _check_keyboard_navigation(self, results: Dict[str, Any], driver: webdriver.Chrome):
        """Prüft Tastaturbedienbarkeit"""
        interactive_elements = driver.find_elements(By.CSS_SELECTOR, 
            "a, button, input, select, textarea, [role='button'], [role='link']")
        
        for element in interactive_elements:
            tabindex = element.get_attribute("tabindex")
            if tabindex and int(tabindex) < 0:
                results["violations"].append({
                    "type": "keyboard_navigation",
                    "element": element.tag_name,
                    "severity": "error",
                    "message": "Element ist nicht per Tastatur erreichbar",
                    "element_info": self._sanitize_element(element)
                })

    def _check_skip_links(self, results: Dict[str, Any], driver: webdriver.Chrome):
        """Prüft auf Skip-Links"""
        skip_links = driver.find_elements(By.CSS_SELECTOR, 
            "a[href^='#']:not([href='#'])")
        
        if not skip_links:
            results["warnings"].append({
                "type": "skip_links",
                "severity": "warning",
                "message": "Keine Skip-Links zur Hauptnavigation gefunden"
            })

    def _check_heading_structure(self, results: Dict[str, Any], driver: webdriver.Chrome):
        """Prüft Überschriftenhierarchie"""
        headings = []
        for i in range(1, 7):
            headings.extend(driver.find_elements(By.TAG_NAME, f"h{i}"))
        
        if not headings:
            results["violations"].append({
                "type": "headings",
                "severity": "error",
                "message": "Keine Überschriften gefunden"
            })
        
        # Prüfe Überschriftenhierarchie
        last_level = 0
        for heading in headings:
            current_level = int(heading.tag_name[1])
            if current_level > last_level + 1:
                results["violations"].append({
                    "type": "heading_hierarchy",
                    "severity": "error",
                    "message": f"Überschriftenebene übersprungen (von H{last_level} zu H{current_level})",
                    "html": heading.get_attribute("outerHTML")
                })
            last_level = current_level

    def _check_color_contrast(self, results: Dict[str, Any], driver: webdriver.Chrome):
        """Prüft Farbkontraste zwischen Text und Hintergrund"""
        # Finde alle Text-Elemente
        text_elements = driver.find_elements(By.CSS_SELECTOR, 
            "p, h1, h2, h3, h4, h5, h6, li, td, a, span, div:not(:empty)")
        
        contrast_issues = []
        checked_elements = 0
        
        for elem in text_elements[:30]:  # Begrenzen auf 30 Elemente für Performance
            try:
                # Überspringe leere oder sehr kurze Texte
                if not elem.text or len(elem.text.strip()) < 3:
                    continue
                    
                checked_elements += 1
                
                # Hole die berechneten Farben
                style_values = driver.execute_script("""
                    var style = window.getComputedStyle(arguments[0]);
                    var bgColor = style.backgroundColor;
                    var textColor = style.color;
                    var fontSize = style.fontSize;
                    var fontWeight = style.fontWeight;
                    
                    return {
                        backgroundColor: bgColor,
                        color: textColor,
                        fontSize: fontSize,
                        fontWeight: fontWeight
                    };
                """, elem)
                
                bg_color = style_values["backgroundColor"]
                text_color = style_values["color"]
                font_size = self._extract_px_value(style_values["fontSize"])
                font_weight = style_values["fontWeight"]
                
                # Konvertiere rgba zu rgb
                bg_rgb = self._parse_color(bg_color)
                text_rgb = self._parse_color(text_color)
                
                # Wenn eine der Farben transparent ist, überspringe
                if not bg_rgb or not text_rgb:
                    continue
                    
                # Berechne Kontrastverhältnis
                contrast_ratio = self._calculate_contrast_ratio(bg_rgb, text_rgb)
                
                # Bestimme Schwellenwert basierend auf Textgröße und -gewicht
                is_large_text = font_size >= 18 or (font_size >= 14 and font_weight in ["bold", "700", "800", "900"])
                
                required_ratio = 4.5
                if is_large_text:
                    required_ratio = 3.0
                
                if contrast_ratio < required_ratio:
                    contrast_issues.append({
                        "element": self._sanitize_element(elem),
                        "contrast_ratio": round(contrast_ratio, 2),
                        "required_ratio": required_ratio,
                        "text_color": text_color,
                        "bg_color": bg_color,
                        "is_large_text": is_large_text,
                        "text_sample": elem.text[:50]
                    })
            except Exception as e:
                self.logger.debug(f"Fehler bei der Kontrastanalyse: {str(e)}")
                continue
        
        if contrast_issues:
            results["violations"].append({
                "type": "color_contrast",
                "severity": "error",
                "message": f"{len(contrast_issues)} von {checked_elements} geprüften Elementen haben unzureichenden Farbkontrast",
                "issues": contrast_issues[:10]  # Begrenzen auf 10 Beispiele
            })
        else:
            results["passed"].append({
                "type": "color_contrast",
                "message": f"Alle {checked_elements} geprüften Elemente haben ausreichenden Farbkontrast"
            })

    def _parse_color(self, color_str: str) -> Tuple[int, int, int]:
        """Konvertiert einen CSS-Farbwert in RGB"""
        if not color_str or color_str == "transparent" or color_str == "rgba(0, 0, 0, 0)":
            return None
            
        try:
            # rgb(r, g, b) oder rgba(r, g, b, a)
            rgb_match = re.search(r'rgba?\((\d+),\s*(\d+),\s*(\d+)', color_str)
            if rgb_match:
                r, g, b = map(int, rgb_match.groups())
                return (r, g, b)
                
            # #rrggbb oder #rgb
            hex_match = re.search(r'#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})', color_str, re.I)
            if hex_match:
                r, g, b = map(lambda x: int(x, 16), hex_match.groups())
                return (r, g, b)
                
            # #rgb
            short_hex_match = re.search(r'#([0-9a-f])([0-9a-f])([0-9a-f])', color_str, re.I)
            if short_hex_match:
                r, g, b = map(lambda x: int(x + x, 16), short_hex_match.groups())
                return (r, g, b)
        except:
            pass
            
        return None

    def _calculate_contrast_ratio(self, rgb1: Tuple[int, int, int], rgb2: Tuple[int, int, int]) -> float:
        """Berechnet das Kontrastverhältnis zwischen zwei RGB-Farben"""
        # Berechne relative Leuchtkraft
        l1 = self._relative_luminance(rgb1)
        l2 = self._relative_luminance(rgb2)
        
        # Verwende die hellere Farbe als L1
        if l1 < l2:
            l1, l2 = l2, l1
            
        # Berechne Kontrastverhältnis
        return (l1 + 0.05) / (l2 + 0.05)

    def _relative_luminance(self, rgb: Tuple[int, int, int]) -> float:
        """Berechnet die relative Leuchtkraft einer RGB-Farbe"""
        r, g, b = rgb
        
        # Normalisiere RGB-Werte
        r = r / 255
        g = g / 255
        b = b / 255
        
        # Gamma-Korrektur
        r = self._gamma_correction(r)
        g = self._gamma_correction(g)
        b = self._gamma_correction(b)
        
        # Berechne gewichtete Summe
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    def _gamma_correction(self, value: float) -> float:
        """Wendet Gamma-Korrektur auf einen Farbwert an"""
        if value <= 0.03928:
            return value / 12.92
        else:
            return math.pow((value + 0.055) / 1.055, 2.4)

    def _check_form_labels(self, results: Dict[str, Any], driver: webdriver.Chrome):
        """Prüft Formularfelder auf Labels"""
        inputs = driver.find_elements(By.TAG_NAME, "input")
        for input_field in inputs:
            input_id = input_field.get_attribute("id")
            if input_id:
                label = driver.find_elements(By.CSS_SELECTOR, f"label[for='{input_id}']")
                if not label:
                    results["violations"].append({
                        "type": "form_label",
                        "severity": "error",
                        "message": "Formularfeld ohne zugeordnetes Label gefunden",
                        "html": input_field.get_attribute("outerHTML")
                    })

    def _check_language_declaration(self, results: Dict[str, Any], driver: webdriver.Chrome):
        """Prüft Sprachdeklaration"""
        html = driver.find_element(By.TAG_NAME, "html")
        lang = html.get_attribute("lang")
        if not lang:
            results["violations"].append({
                "type": "language",
                "severity": "error",
                "message": "Keine Sprachdeklaration im HTML-Tag gefunden"
            })

    def _check_responsive_design(self, results: Dict[str, Any], driver: webdriver.Chrome):
        """Prüft grundlegende Responsive Design Eigenschaften"""
        viewport = driver.find_element(By.CSS_SELECTOR, "meta[name='viewport']")
        if not viewport:
            results["violations"].append({
                "type": "responsive",
                "severity": "error",
                "message": "Kein Viewport-Meta-Tag gefunden"
            }) 

    def _check_aria_roles(self, results: Dict[str, Any], driver: webdriver.Chrome):
        """Prüft die korrekte Verwendung von ARIA-Rollen"""
        elements_with_roles = driver.find_elements(By.CSS_SELECTOR, "[role]")
        
        valid_roles = {
            'alert', 'alertdialog', 'application', 'article', 'banner', 'button',
            'cell', 'checkbox', 'columnheader', 'combobox', 'complementary',
            'contentinfo', 'definition', 'dialog', 'directory', 'document',
            'feed', 'figure', 'form', 'grid', 'gridcell', 'group', 'heading',
            'img', 'link', 'list', 'listbox', 'listitem', 'log', 'main',
            'marquee', 'math', 'menu', 'menubar', 'menuitem', 'menuitemcheckbox',
            'menuitemradio', 'navigation', 'none', 'note', 'option', 'presentation',
            'progressbar', 'radio', 'radiogroup', 'region', 'row', 'rowgroup',
            'rowheader', 'scrollbar', 'search', 'searchbox', 'separator',
            'slider', 'spinbutton', 'status', 'switch', 'tab', 'table',
            'tablist', 'tabpanel', 'term', 'textbox', 'timer', 'toolbar',
            'tooltip', 'tree', 'treegrid', 'treeitem'
        }
        
        for element in elements_with_roles:
            role = element.get_attribute("role")
            if role not in valid_roles:
                results["violations"].append({
                    "type": "invalid_aria_role",
                    "severity": "error",
                    "message": f"Ungültige ARIA-Rolle: {role}",
                    "element_info": self._sanitize_element(element)
                })
            
            # Prüfe Anforderungen für bestimmte Rollen
            if role == "checkbox" and not element.get_attribute("aria-checked"):
                results["violations"].append({
                    "type": "missing_aria_attribute",
                    "severity": "error",
                    "message": "Checkbox-Rolle ohne aria-checked Attribut",
                    "element_info": self._sanitize_element(element)
                })
                
            if role in ["combobox", "listbox", "textbox"] and not element.get_attribute("aria-expanded"):
                results["warnings"].append({
                    "type": "missing_aria_attribute",
                    "severity": "warning",
                    "message": f"{role}-Rolle ohne aria-expanded Attribut",
                    "element_info": self._sanitize_element(element)
                })

    def _check_page_title(self, results: Dict[str, Any], driver: webdriver.Chrome):
        """Prüft den Seitentitel auf Vorhandensein und Aussagekraft"""
        title = driver.title
        
        if not title:
            results["violations"].append({
                "type": "missing_title",
                "severity": "error",
                "message": "Die Seite hat keinen Titel"
            })
        elif len(title) < 5:
            results["warnings"].append({
                "type": "short_title",
                "severity": "warning",
                "message": f"Der Seitentitel ist sehr kurz: '{title}'"
            })
        elif "untitled" in title.lower() or "new page" in title.lower():
            results["violations"].append({
                "type": "default_title",
                "severity": "error",
                "message": f"Die Seite verwendet einen Standard-Titel: '{title}'"
            })
        else:
            results["passed"].append({
                "type": "page_title",
                "message": f"Die Seite hat einen aussagekräftigen Titel: '{title}'"
            })

    def _check_landmarks(self, results: Dict[str, Any], driver: webdriver.Chrome):
        """Prüft die Verwendung von ARIA-Landmarks"""
        landmarks = {
            "banner": driver.find_elements(By.CSS_SELECTOR, "header, [role='banner']"),
            "navigation": driver.find_elements(By.CSS_SELECTOR, "nav, [role='navigation']"),
            "main": driver.find_elements(By.CSS_SELECTOR, "main, [role='main']"),
            "complementary": driver.find_elements(By.CSS_SELECTOR, "aside, [role='complementary']"),
            "contentinfo": driver.find_elements(By.CSS_SELECTOR, "footer, [role='contentinfo']"),
            "search": driver.find_elements(By.CSS_SELECTOR, "[role='search']")
        }
        
        # Prüfe, ob die wichtigsten Landmarks vorhanden sind
        if not landmarks["main"]:
            results["violations"].append({
                "type": "missing_landmark",
                "severity": "error",
                "message": "Kein Hauptinhalt-Landmark (main) gefunden"
            })
            
        if not landmarks["navigation"]:
            results["warnings"].append({
                "type": "missing_landmark",
                "severity": "warning",
                "message": "Kein Navigations-Landmark (nav) gefunden"
            })
            
        # Prüfe auf mehrfache Hauptinhalts-Landmarks
        if len(landmarks["main"]) > 1:
            results["warnings"].append({
                "type": "multiple_landmarks",
                "severity": "warning",
                "message": f"Mehrere Hauptinhalts-Landmarks gefunden: {len(landmarks['main'])}"
            })
            
        # Zähle die Gesamtzahl der Landmarks
        total_landmarks = sum(len(landmark_list) for landmark_list in landmarks.values())
        
        if total_landmarks == 0:
            results["violations"].append({
                "type": "no_landmarks",
                "severity": "error",
                "message": "Keine Landmarks gefunden"
            })
        else:
            results["passed"].append({
                "type": "landmarks",
                "message": f"Insgesamt {total_landmarks} Landmarks gefunden"
            })

    def _check_link_names(self, results: Dict[str, Any], driver: webdriver.Chrome):
        """Prüft Links auf aussagekräftige Namen"""
        links = driver.find_elements(By.TAG_NAME, "a")
        
        for link in links:
            link_text = link.text.strip()
            aria_label = link.get_attribute("aria-label")
            title = link.get_attribute("title")
            
            accessible_name = link_text or aria_label or title
            
            # Prüfe auf leere Links
            if not accessible_name:
                # Prüfe, ob der Link ein Bild mit Alt-Text enthält
                img = link.find_elements(By.TAG_NAME, "img")
                if img and img[0].get_attribute("alt"):
                    continue  # Das Bild hat einen Alt-Text, also hat der Link einen Namen
                
                results["violations"].append({
                    "type": "empty_link",
                    "severity": "error",
                    "message": "Link ohne zugänglichen Namen gefunden",
                    "element_info": self._sanitize_element(link)
                })
                continue
                
            # Prüfe auf nicht aussagekräftige Link-Texte
            non_descriptive = ["klicken sie hier", "hier klicken", "mehr", "weiter", "click here", "more", "read more", "link"]
            if accessible_name.lower() in non_descriptive or len(accessible_name) < 4:
                results["warnings"].append({
                    "type": "non_descriptive_link",
                    "severity": "warning",
                    "message": f"Nicht aussagekräftiger Link-Text: '{accessible_name}'",
                    "element_info": self._sanitize_element(link)
                })

    def _check_form_validation(self, results: Dict[str, Any], driver: webdriver.Chrome):
        """Prüft Formulare auf Validierungsmöglichkeiten"""
        forms = driver.find_elements(By.TAG_NAME, "form")
        
        for form in forms:
            has_required_fields = bool(form.find_elements(By.CSS_SELECTOR, "[required]"))
            has_validation = form.get_attribute("novalidate") is None
            
            # Sammle Informationen über Fehlermeldungen
            error_messages = form.find_elements(By.CSS_SELECTOR, "[role='alert'], .error, .invalid, [aria-invalid='true']")
            
            # Prüfe Formularfelder
            fields = form.find_elements(By.CSS_SELECTOR, "input, select, textarea")
            fields_with_validation = []
            
            for field in fields:
                field_validation = {
                    "id": field.get_attribute("id"),
                    "type": field.get_attribute("type"),
                    "required": field.get_attribute("required") is not None,
                    "pattern": field.get_attribute("pattern"),
                    "min": field.get_attribute("min"),
                    "max": field.get_attribute("max"),
                    "minlength": field.get_attribute("minlength"),
                    "maxlength": field.get_attribute("maxlength"),
                    "aria_required": field.get_attribute("aria-required"),
                    "aria_invalid": field.get_attribute("aria-invalid"),
                    "aria_errormessage": field.get_attribute("aria-errormessage")
                }
                
                # Zähle nur Felder mit Validierungsattributen
                if any(v for k, v in field_validation.items() if k not in ["id", "type"]):
                    fields_with_validation.append(field_validation)
            
            # Bewerte die Formularvalidierung
            if has_required_fields and not has_validation and not fields_with_validation:
                results["warnings"].append({
                    "type": "form_validation",
                    "severity": "warning",
                    "message": "Formular mit Pflichtfeldern ohne Validierung",
                    "element_info": self._sanitize_element(form)
                })
                
            if fields_with_validation and not error_messages:
                results["warnings"].append({
                    "type": "missing_error_messages",
                    "severity": "warning",
                    "message": "Formular mit Validierung ohne sichtbare Fehlermeldungen",
                    "element_info": self._sanitize_element(form)
                })
            
            # Wenn sowohl Validierung als auch Fehlermeldungen vorhanden sind
            if fields_with_validation and error_messages:
                results["passed"].append({
                    "type": "form_validation",
                    "message": f"Formular mit {len(fields_with_validation)} validierten Feldern und {len(error_messages)} Fehlermeldungen"
                })

    def _check_focus_visible(self, results: Dict[str, Any], driver: webdriver.Chrome):
        """Prüft die Sichtbarkeit des Fokus bei interaktiven Elementen"""
        # Diese Prüfung ist komplex und erfordert CSS-Analyse oder Screenshots
        # Hier eine vereinfachte Version, die nach outline:none sucht
        
        # Extrahiere alle Stylesheets
        stylesheets = driver.execute_script("""
            var styles = '';
            for (var i = 0; i < document.styleSheets.length; i++) {
                try {
                    var rules = document.styleSheets[i].cssRules || document.styleSheets[i].rules;
                    for (var j = 0; j < rules.length; j++) {
                        styles += rules[j].cssText;
                    }
                } catch (e) {
                    // Ignoriere CORS-Fehler
                }
            }
            return styles;
        """)
        
        # Suche nach Focus-Styles, die den Fokus entfernen
        focus_removers = [
            r':focus\s*{\s*outline\s*:\s*none',
            r':focus\s*{\s*outline\s*:\s*0',
            r'\.no-outline:focus',
            r'\.no-focus-outline'
        ]
        
        for pattern in focus_removers:
            if re.search(pattern, stylesheets):
                results["violations"].append({
                    "type": "focus_not_visible",
                    "severity": "error",
                    "message": f"CSS entfernt den sichtbaren Fokus (Muster: {pattern})",
                    "style_info": pattern
                })
                break
                
        # Suche nach Elementen mit inline-styles, die den Fokus entfernen
        focus_removing_elements = driver.find_elements(By.CSS_SELECTOR, 
            "[style*='outline: none'], [style*='outline:none'], [style*='outline: 0'], [style*='outline:0']")
        
        if focus_removing_elements:
            results["violations"].append({
                "type": "focus_not_visible_inline",
                "severity": "error",
                "message": f"{len(focus_removing_elements)} Elemente mit inline-styles, die den Fokus entfernen",
                "elements": [self._sanitize_element(elem) for elem in focus_removing_elements[:5]]  # Begrenzen auf 5 Beispiele
            })

    def _check_text_spacing(self, results: Dict[str, Any], driver: webdriver.Chrome):
        """Prüft Textabstände auf Barrierefreiheit"""
        # Minimale Werte für Textabstände nach WCAG 2.1
        min_line_height = 1.5    # 1.5 mal die Schriftgröße
        min_spacing = 0.12       # 0.12 mal die Schriftgröße
        min_paragraph = 2        # 2 mal die Schriftgröße
        
        # Extrahiere Text-Elemente und ihre Styles
        text_elements = driver.find_elements(By.CSS_SELECTOR, 
            "p, h1, h2, h3, h4, h5, h6, li, td, div:not(:empty)")
        
        issues = []
        
        for elem in text_elements[:20]:  # Begrenzen auf 20 Elemente für Performance
            try:
                computed_style = driver.execute_script("""
                    var style = window.getComputedStyle(arguments[0]);
                    return {
                        lineHeight: style.lineHeight,
                        letterSpacing: style.letterSpacing,
                        wordSpacing: style.wordSpacing,
                        fontSize: style.fontSize
                    };
                """, elem)
                
                # Extrahiere Zahlenwerte (nehme an, dass sie in px sind)
                font_size = self._extract_px_value(computed_style["fontSize"])
                line_height = self._extract_px_value(computed_style["lineHeight"])
                letter_spacing = self._extract_px_value(computed_style["letterSpacing"])
                word_spacing = self._extract_px_value(computed_style["wordSpacing"])
                
                if font_size > 0:
                    # Berechne Verhältnisse zur Schriftgröße
                    line_height_ratio = line_height / font_size if line_height else 0
                    letter_spacing_ratio = letter_spacing / font_size if letter_spacing else 0
                    word_spacing_ratio = word_spacing / font_size if word_spacing else 0
                    
                    # Prüfe auf zu geringe Werte
                    if line_height_ratio > 0 and line_height_ratio < min_line_height:
                        issues.append({
                            "type": "line_height",
                            "element": self._sanitize_element(elem),
                            "value": line_height_ratio,
                            "min_recommended": min_line_height
                        })
                        
                    if letter_spacing_ratio > 0 and letter_spacing_ratio < min_spacing:
                        issues.append({
                            "type": "letter_spacing",
                            "element": self._sanitize_element(elem),
                            "value": letter_spacing_ratio,
                            "min_recommended": min_spacing
                        })
                        
                    if word_spacing_ratio > 0 and word_spacing_ratio < min_spacing:
                        issues.append({
                            "type": "word_spacing",
                            "element": self._sanitize_element(elem),
                            "value": word_spacing_ratio,
                            "min_recommended": min_spacing
                        })
            except Exception as e:
                self.logger.debug(f"Fehler bei der Textabstandsanalyse: {str(e)}")
                continue
        
        if issues:
            results["warnings"].append({
                "type": "text_spacing",
                "severity": "warning",
                "message": f"{len(issues)} Elemente mit unzureichenden Textabständen gefunden",
                "issues": issues[:10]  # Begrenzen auf 10 Beispiele
            })
        else:
            results["passed"].append({
                "type": "text_spacing",
                "message": "Keine Probleme mit Textabständen gefunden"
            })

    def _extract_px_value(self, css_value: str) -> float:
        """Extrahiert den Zahlenwert aus einem CSS-Wert (z.B. '16px' -> 16)"""
        if not css_value:
            return 0
            
        try:
            # Entferne Einheit und konvertiere zu float
            match = re.search(r'([\d.]+)', css_value)
            if match:
                return float(match.group(1))
        except:
            pass
            
        return 0

    def _check_tables(self, results: Dict[str, Any], driver: webdriver.Chrome):
        """Prüft Tabellen auf Barrierefreiheit"""
        tables = driver.find_elements(By.TAG_NAME, "table")
        
        for table in tables:
            # Prüfe auf caption
            caption = table.find_elements(By.TAG_NAME, "caption")
            has_caption = len(caption) > 0
            
            # Prüfe auf Spaltenüberschriften
            headers = table.find_elements(By.TAG_NAME, "th")
            has_headers = len(headers) > 0
            
            # Prüfe auf scope-Attribute bei th-Elementen
            headers_with_scope = [h for h in headers if h.get_attribute("scope")]
            has_proper_scope = len(headers_with_scope) == len(headers) and len(headers) > 0
            
            # Prüfe auf komplexe Tabellen (mehrere tbody, rowspan/colspan)
            tbody_elements = table.find_elements(By.TAG_NAME, "tbody")
            cells_with_span = table.find_elements(By.CSS_SELECTOR, "[rowspan], [colspan]")
            is_complex_table = len(tbody_elements) > 1 or len(cells_with_span) > 0
            
            # Prüfe auf aria-Attribute für komplexe Tabellen
            if is_complex_table:
                cells_with_headers = table.find_elements(By.CSS_SELECTOR, "[headers]")
                has_proper_aria = len(cells_with_headers) > 0
                
                if not has_proper_aria:
                    results["violations"].append({
                        "type": "complex_table_no_aria",
                        "severity": "error",
                        "message": "Komplexe Tabelle ohne ARIA-Attribute für Zellzuordnung",
                        "element_info": self._sanitize_element(table)
                    })
            
            # Bewerte die Tabelle
            if not has_caption:
                results["warnings"].append({
                    "type": "table_no_caption",
                    "severity": "warning",
                    "message": "Tabelle ohne Caption gefunden",
                    "element_info": self._sanitize_element(table)
                })
                
            if not has_headers:
                results["violations"].append({
                    "type": "table_no_headers",
                    "severity": "error",
                    "message": "Tabelle ohne Spaltenüberschriften (th) gefunden",
                    "element_info": self._sanitize_element(table)
                })
                
            if has_headers and not has_proper_scope:
                results["warnings"].append({
                    "type": "table_no_scope",
                    "severity": "warning",
                    "message": "Tabelle mit Überschriften ohne scope-Attribute",
                    "element_info": self._sanitize_element(table)
                })
                
            # Wenn alles korrekt ist
            if has_caption and has_headers and has_proper_scope:
                results["passed"].append({
                    "type": "table_structure",
                    "message": "Tabelle mit korrekter Struktur gefunden"
                }) 