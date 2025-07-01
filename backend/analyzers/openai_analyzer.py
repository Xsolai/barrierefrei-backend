#!/usr/bin/env python3
"""
OpenAI WCAG Analyzer - Analysiert Webseiten mit GPT-4 auf WCAG-Konformität
"""

import logging
import json
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
import openai
from openai import OpenAI
import os
import re

# Import config
try:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import (
        OPENAI_API_KEY, 
        OPENAI_MODEL, 
        OPENAI_MAX_TOKENS, 
        OPENAI_TEMPERATURE,
        OPENAI_MAX_CONTEXT_TOKENS
    )
except ImportError:
    # Fallback wenn config.py nicht gefunden wird
    OPENAI_API_KEY = None
    OPENAI_MODEL = "gpt-4-turbo-preview"
    OPENAI_MAX_TOKENS = 5000
    OPENAI_TEMPERATURE = 0.0
    OPENAI_MAX_CONTEXT_TOKENS = 1000000

# Zentrales WCAG Scoring- und Compliance-Schema - DRASTISCH VERSCHÄRFT!
WCAG_SCORING_RULES = {
    "score_ranges": {
        "85-100": "Ausgezeichnet (extrem selten - nur bei nahezu perfekter Umsetzung)",
        "70-84": "Gut (solide Umsetzung mit wichtigen Verbesserungen nötig)",
        "55-69": "Befriedigend (grundlegende Umsetzung, erhebliche Verbesserungen nötig)",
        "40-54": "Ausreichend (teilweise Umsetzung, viele Probleme vorhanden)",
        "25-39": "Mangelhaft (große Probleme, nur Grundlagen erkennbar)",
        "0-24": "Ungenügend (kritische Barrieren, komplette Überarbeitung nötig)"
    },
    "compliance_mapping": {
        "AAA (98-100)": "Perfekte Barrierefreiheit - praktisch unerreichbar, nur theoretisch möglich",
        "AA+ (95-97)": "Exzellente Barrierefreiheit - übertrifft AA-Standards deutlich",
        "AA (85-94)": "Sehr gute Barrierefreiheit - erfüllt AA-Standards vollständig",
        "A+ (75-84)": "Gute Barrierefreiheit - übertrifft A-Standards",
        "A (60-74)": "Grundlegende Barrierefreiheit - A-Standards erfüllt",
        "PARTIAL (35-59)": "Teilweise barrierefrei - wichtige Lücken vorhanden",
        "POOR (15-34)": "Schlecht - erhebliche Barrieren vorhanden",
        "CRITICAL (0-14)": "Kritisch - umfassende Überarbeitung zwingend erforderlich"
    },
    "philosophy": "Seien Sie STRENG und REALISTISCH - echte Barrierefreiheit ist schwer zu erreichen. AAA ist praktisch unmöglich, AA erfordert exzellente Umsetzung. Die meisten Websites liegen zwischen 20-60 Punkten. Nur außergewöhnlich gut gemachte Seiten erreichen über 80 Punkte."
}

class OpenAIWCAGAnalyzer:
    """OpenAI-basierter WCAG-Experten-Analyzer"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialisiert den OpenAI Analyzer
        
        Args:
            api_key: OpenAI API Key (optional, wird aus Umgebungsvariable gelesen)
        """
        self.logger = logging.getLogger(__name__)
        
        # API Key laden
        if api_key:
            self.api_key = api_key
        else:
            # Versuche aus verschiedenen Quellen zu laden
            self.api_key = self._load_api_key()
        
        if not self.api_key:
            raise ValueError("OpenAI API Key nicht gefunden. Setze OPENAI_API_KEY Umgebungsvariable.")
        
        # OpenAI Client initialisieren
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # Model-Konfiguration - flexibel über Umgebung oder Default
        self.model = OPENAI_MODEL
        self.max_tokens = OPENAI_MAX_TOKENS
        self.temperature = OPENAI_TEMPERATURE
        
        # Context Window - kann über Umgebung auf 1M gesetzt werden!
        self.max_context_tokens = OPENAI_MAX_CONTEXT_TOKENS
        
        self.logger.info(f"OpenAI WCAG Analyzer initialisiert:")
        self.logger.info(f"  📊 Model: {self.model}")
        self.logger.info(f"  🚀 Max Context: {self.max_context_tokens:,} tokens")
        self.logger.info(f"  📝 Max Response: {self.max_tokens:,} tokens")
        self.logger.info(f"  🌡️ Temperature: {self.temperature}")
    
    def _load_api_key(self) -> Optional[str]:
        """Lädt API Key aus verschiedenen Quellen"""
        # 1. Umgebungsvariable
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            return api_key
        
        # 2. .env.local im Projektroot
        env_file = Path(__file__).parent.parent.parent / '.env.local'
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('OPENAI_API_KEY='):
                        return line.split('=', 1)[1].strip()
        
        # 3. .env im Backend
        env_file = Path(__file__).parent.parent / '.env'
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('OPENAI_API_KEY='):
                        return line.split('=', 1)[1].strip()
        
        return None
    
    def _estimate_tokens(self, text: str) -> int:
        """Schätzt die Anzahl der Token in einem Text (grober Estimate: ~4 Zeichen = 1 Token)"""
        return len(text) // 4

    def _truncate_prompt_if_needed(self, expert_prompt: str, wcag_area: str) -> str:
        """Kürzt den Prompt intelligent, falls er zu lang ist"""
        estimated_tokens = self._estimate_tokens(expert_prompt)
        
        if estimated_tokens <= self.max_context_tokens:
            return expert_prompt
        
        self.logger.warning(f"⚠️ Prompt für {wcag_area} zu lang ({estimated_tokens:,} tokens), kürze auf {self.max_context_tokens:,} tokens")
        
        # Strategie: Behalte Anfang und Ende, kürze Mitte
        lines = expert_prompt.split('\n')
        
        # Finde den Datenbereich
        data_start_idx = None
        for i, line in enumerate(lines):
            if 'WEBSITE_ANALYSIS_DATA' in line or '```json' in line:
                data_start_idx = i
                break
        
        if data_start_idx:
            # Behalte Header und Footer
            header = '\n'.join(lines[:data_start_idx])
            footer = '\n'.join(lines[-50:])  # Letzte 50 Zeilen
            
            # Kürze Daten in der Mitte
            available_tokens = self.max_context_tokens - self._estimate_tokens(header) - self._estimate_tokens(footer) - 100
            
            data_lines = lines[data_start_idx:-50]
            truncated_data = []
            current_tokens = 0
            
            for line in data_lines:
                line_tokens = self._estimate_tokens(line)
                if current_tokens + line_tokens > available_tokens:
                    truncated_data.append("... [Daten gekürzt für Token-Limit] ...")
                    break
                truncated_data.append(line)
                current_tokens += line_tokens
            
            return '\n'.join([header] + truncated_data + [footer])
        
        # Fallback: Kürze einfach auf die letzten X Zeichen
        max_chars = self.max_context_tokens * 3  # Konservative Schätzung
        if len(expert_prompt) > max_chars:
            truncated = expert_prompt[:max_chars] + "\n\n... [Prompt gekürzt für Context-Limit] ..."
            self.logger.info(f"✂️ Prompt hart gekürzt auf {max_chars:,} Zeichen")
            return truncated
        
        return expert_prompt

    def _extract_json_from_markdown(self, markdown_text: str) -> str:
        """Extrahiert und bereinigt JSON aus Markdown-Code-Blöcken"""
        import re
        
        # Entferne Unicode BOM und unsichtbare Zeichen
        markdown_text = markdown_text.strip().lstrip('\ufeff').lstrip('\u200b').lstrip('\u00a0')
        
        # Schritt 1: Versuche JSON aus ```json Code-Blöcken zu extrahieren
        json_pattern = r'```json\s*\n(.*?)\n```'
        matches = re.findall(json_pattern, markdown_text, re.DOTALL | re.IGNORECASE)
        
        if matches:
            raw_json = matches[0].strip()
            return self._clean_json(raw_json)
        
        # Schritt 2: Versuche JSON aus generischen Code-Blöcken
        code_pattern = r'```\s*\n(.*?)\n```'
        matches = re.findall(code_pattern, markdown_text, re.DOTALL)
        
        if matches:
            for match in matches:
                content = match.strip()
                if content.startswith('{') and content.endswith('}'):
                    return self._clean_json(content)
        
        # Schritt 3: Suche nach JSON-ähnlichen Strukturen ohne Code-Blöcke
        json_like_pattern = r'\{[^{}]*"analysis_result"[^{}]*\{.*?\}\s*\}'
        matches = re.findall(json_like_pattern, markdown_text, re.DOTALL)
        
        if matches:
            return self._clean_json(matches[0].strip())
        
        # Schritt 4: Aggressive JSON-Suche - Robustere Bracket-Matching
        # Finde das erste { und das letzte } und extrahiere dazwischen
        start_brace = markdown_text.find('{')
        if start_brace != -1:
            # Zähle geschweifte Klammern, um das korrekte Schließen zu finden
            brace_count = 0
            for i, char in enumerate(markdown_text[start_brace:], start_brace):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        # Gefunden! Extrahiere JSON
                        potential_json = markdown_text[start_brace:i + 1]
                        return self._clean_json(potential_json)
        
        # Fallback: Suche nach einfachem Start/Ende-Muster
        end_brace = markdown_text.rfind('}')
        if start_brace != -1 and end_brace != -1 and end_brace > start_brace:
            potential_json = markdown_text[start_brace:end_brace + 1]
            return self._clean_json(potential_json)
        
        # Letzter Fallback: Gib den gesamten Text zurück
        return markdown_text.strip()
    
    def _clean_json(self, json_str: str) -> str:
        """Bereinigt häufige JSON-Syntax-Fehler"""
        
        # Entferne führende/nachgestellte Whitespaces
        json_str = json_str.strip()
        
        # Entferne trailing commas (häufiger GPT-Fehler)
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        # Entferne Kommentare aus JSON (auch häufiger GPT-Fehler)
        json_str = re.sub(r'//.*?$', '', json_str, flags=re.MULTILINE)
        json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
        
        # Ersetze einfache durch doppelte Anführungszeichen (falls nötig)
        # Aber nur für Property-Namen, nicht für String-Inhalte
        json_str = re.sub(r"'([^']*)'(\s*:)", r'"\1"\2', json_str)
        
        # Entferne überflüssige Whitespaces
        json_str = re.sub(r'\s+', ' ', json_str)
        
        # Stelle sicher, dass { } balanced sind
        open_braces = json_str.count('{')
        close_braces = json_str.count('}')
        
        if open_braces > close_braces:
            json_str += '}' * (open_braces - close_braces)
        
        return json_str

    def _fix_common_json_errors(self, json_str: str) -> str:
        """
        Behebt häufige JSON-Syntax-Fehler
        """
        try:
            import re
            
            # Entferne Unicode BOM und unsichtbare Zeichen am Anfang
            json_str = json_str.strip().lstrip('\ufeff').lstrip('\u200b').lstrip('\u00a0')
            
            # Entferne trailing commas vor closing brackets/braces
            json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
            
            # Doppelte commas entfernen
            json_str = re.sub(r',\s*,', ',', json_str)
            
            # Entferne control characters die JSON parsing stören
            json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)
            
            # Fix: Manchmal beginnt JSON mit Backticks oder anderen Zeichen
            # Finde den ersten echten { und schneide davor ab
            first_brace = json_str.find('{')
            if first_brace > 0:
                json_str = json_str[first_brace:]
            
            # Fix: Manchmal endet JSON mit zusätzlichen Zeichen
            # Finde die letzte echte } und schneide danach ab
            last_brace = json_str.rfind('}')
            if last_brace != -1 and last_brace < len(json_str) - 1:
                json_str = json_str[:last_brace + 1]
            
            # Fix unescaped newlines in strings
            json_str = re.sub(r'(?<!\\)\n', '\\n', json_str)
            
            # Fix unescaped quotes (einfache Heuristik)
            lines = json_str.split('\n')
            fixed_lines = []
            
            for line in lines:
                # Suche nach unescaped quotes in string values (nach :)
                if '": "' in line and line.count('"') > 4:
                    # Einfache Korrektur für häufige Fälle
                    line = re.sub(r'(?<!\\)"(?=[^:,}\]]*[^\\]")', r'\\"', line)
                
                fixed_lines.append(line)
            
            json_str = '\n'.join(fixed_lines)
            
            return json_str
            
        except Exception as e:
            self.logger.warning(f"Fehler bei JSON-Fehler-Korrektur: {e}")
            return json_str

    def _super_aggressive_json_clean(self, json_str: str) -> str:
        """
        Führt eine noch aggressivere Bereinigung durch
        """
        try:
            import re
            
            # Schritt 1: Entferne ALLE unsichtbaren Zeichen am Anfang
            original_length = len(json_str)
            json_str = json_str.strip()
            
            # Entferne alle Unicode-Whitespace-Zeichen am Anfang
            json_str = json_str.lstrip('\ufeff\u200b\u00a0\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u200b\u2028\u2029\u202f\u205f\u3000')
            
            # Schritt 2: Byte-für-Byte Analyse der ersten 10 Zeichen
            if len(json_str) >= 10:
                first_10_bytes = json_str[:10].encode('utf-8')
                self.logger.info(f"🔍 Byte-Analyse: {first_10_bytes.hex()} -> '{json_str[:10]}'")
            
            # Schritt 3: Kritischer Fix für escaped JSON-Anführungszeichen
            if json_str.startswith('{ \"'):
                self.logger.info("🔧 FIXING: Escaped JSON-Anführungszeichen erkannt!")
                json_str = json_str.replace('\\"', '"')
                self.logger.info(f"🔧 Nach Quote-Fix (erste 100 Zeichen): '{json_str[:100]}'")
            
            # Schritt 4: NEUER FIX für "Expecting ',' delimiter"
            # Entferne doppelte Leerzeichen zwischen Werten
            json_str = re.sub(r'(["\]}])\s+(["\[{])', r'\1,\2', json_str)
            
            # Fix für fehlende Kommas vor schließenden Anführungszeichen
            json_str = re.sub(r'(["\w])\s+"([^"]+)":', r'\1, "\2":', json_str)
            
            # Fix für fehlende Kommas zwischen Array-Elementen
            json_str = re.sub(r'}\s*{', r'}, {', json_str)
            
            # Fix für fehlende Kommas zwischen String-Werten
            json_str = re.sub(r'"\s*"(?=[^:]*:)', r'", "', json_str)
            
            # Repariere trailing commas vor schließenden Zeichen
            json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
            
            self.logger.info(f"🔍 JSON-Bereinigung: {original_length} -> {len(json_str)} Zeichen")
            return json_str
            
        except Exception as e:
            self.logger.warning(f"Fehler bei super-aggressiver JSON-Bereinigung: {e}")
            return json_str

    def analyze_with_expert_prompt(self, expert_prompt: str, wcag_area: str) -> Dict[str, Any]:
        """
        Führt eine WCAG-Analyse mit einem Expert-Prompt durch
        
        Args:
            expert_prompt: Vollständiger Expert-Prompt mit Daten
            wcag_area: WCAG-Bereich (z.B. "1_1_textalternativen")
            
        Returns:
            Dict mit Analyse-Ergebnissen
        """
        try:
            self.logger.info(f"Starte OpenAI Analyse für WCAG-Bereich: {wcag_area}")
            
            # Intelligente Prompt-Kürzung falls nötig
            processed_prompt = self._truncate_prompt_if_needed(expert_prompt, wcag_area)
            
            # Dynamischer System Prompt basierend auf WCAG-Bereich
            wcag_descriptions = {
                "1_1_textalternativen": "WCAG 1.1 Textalternativen - NUR Bilder, Alt-Texte und Nicht-Text-Inhalte",
                "1_2_zeitbasierte_medien": "WCAG 1.2 Zeitbasierte Medien - NUR Videos, Audio und zeitbasierte Inhalte", 
                "1_3_anpassbare_darstellung": "WCAG 1.3 Anpassbare Darstellung - NUR HTML-Semantik und Strukturierung",
                "1_4_wahrnehmbare_unterscheidungen": "WCAG 1.4 Wahrnehmbare Unterscheidungen - NUR Farbkontraste und visuelle Unterscheidungen",
                "2_1_tastaturbedienung": "WCAG 2.1 Tastaturbedienung - NUR Tastaturzugänglichkeit und Fokus-Management",
                "2_2_genuegend_zeit": "WCAG 2.2 Genügend Zeit - NUR Zeitlimits, Timer und zeitbasierte Funktionen",
                "2_3_anfaelle_vermeiden": "WCAG 2.3 Anfälle vermeiden - NUR Blitzeffekte, Flackern und schnelle Animationen",
                "2_4_navigation": "WCAG 2.4 Navigierbarkeit - NUR Navigation, Seitenstruktur und Orientierung",
                "3_1_lesbarkeit_sprache": "WCAG 3.1 Lesbarkeit und Sprache - NUR Sprachkennzeichnung und Textverständlichkeit",
                "3_2_vorhersehbarkeit": "WCAG 3.2 Vorhersehbarkeit - NUR konsistente Bedienung und erwartbares Verhalten",
                "3_3_eingabeunterstuetzung": "WCAG 3.3 Eingabeunterstützung - NUR Formulare, Fehlermeldungen und Eingabehilfen",
                "4_1_robustheit_kompatibilitaet": "WCAG 4.1 Robustheit und Kompatibilität - NUR technische Kompatibilität und Code-Qualität"
            }
            
            focus_area = wcag_descriptions.get(wcag_area, f"WCAG-Bereich {wcag_area}")
            
            # Zentrale Scoring-Regeln aus der Konstante laden
            scoring_rules_text = f"""
SCORING-REGELN (zentral definiert):
Score-Bereiche: {', '.join([f'{k}: {v}' for k, v in WCAG_SCORING_RULES['score_ranges'].items()])}

Compliance-Level: {', '.join([f'{k}: {v}' for k, v in WCAG_SCORING_RULES['compliance_mapping'].items()])}

Bewertungs-Philosophie: {WCAG_SCORING_RULES['philosophy']}
"""
            
            system_prompt = f"""Du bist ein spezialisierter WCAG 2.1 Barrierefreiheits-Experte für {focus_area}.

WICHTIGE FOKUSSIERUNG: 
Du analysierst AUSSCHLIESSLICH den Bereich "{focus_area}". 
Ignoriere alle anderen WCAG-Bereiche komplett, auch wenn du Probleme siehst.

{scoring_rules_text}

AUSGABE-FORMAT:
Gib deine Analyse als JSON-Objekt mit dieser Struktur aus:
{{
  "analysis_result": {{
    "summary": {{
      "overall_assessment": "Ausgewogene Bewertung mit positiven und negativen Aspekten",
      "compliance_level": "AAA/AA/A/PARTIAL/NONE",
      "score": <Zahl zwischen 0-100>
    }},
    "criteria_evaluation": [
      {{
        "criterion_id": "X.X.X",
        "name": "Kriteriums-Name",
        "status": "PASSED/FAILED/PARTIAL/WARNING",
        "finding": "Was wurde gefunden",
        "impact": "Auswirkungen auf Nutzer",
        "examples": ["Beispiel 1", "Beispiel 2"],
        "recommendation": "Spezifische Empfehlung",
        "severity": "CRITICAL/MAJOR/MODERATE/MINOR"
      }}
    ],
    "priority_actions": {{
      "immediate": [
        {{
          "title": "Titel der Maßnahme",
          "description": "Detaillierte Beschreibung",
          "effort": "HOCH/MITTEL/NIEDRIG",
          "affected_criteria": ["X.X.X"]
        }}
      ],
      "short_term": [],
      "long_term": []
    }}
  }}
}}"""
            
            # OpenAI API Call mit Retry-Logik für JSON-Parsing
            max_retries = 2
            for attempt in range(max_retries + 1):
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {
                                "role": "system",
                                "content": system_prompt
                            },
                            {
                                "role": "user", 
                                "content": processed_prompt
                            }
                        ],
                        max_tokens=self.max_tokens,
                        temperature=self.temperature,
                        presence_penalty=0.1,
                        frequency_penalty=0.1,
                        response_format={ "type": "json_object" }  # GARANTIERT valides JSON!
                    )
                    
                    raw_content = response.choices[0].message.content
                    
                    # Mit response_format=json_object ist das IMMER valides JSON
                    try:
                        # Direkt parsen - keine Bereinigung nötig!
                        parsed_data = json.loads(raw_content)
                        
                        # Erfolgreiche Validierung - Response verarbeiten
                        analysis_result = {
                            "wcag_area": wcag_area,
                            "timestamp": time.strftime("%Y-%m-%d_%H-%M-%S"),
                            "model_used": self.model,
                            "analysis_content": raw_content,
                            "parsed_json": parsed_data,
                            "token_usage": {
                                "prompt_tokens": response.usage.prompt_tokens,
                                "completion_tokens": response.usage.completion_tokens,
                                "total_tokens": response.usage.total_tokens
                            },
                            "api_call_successful": True,
                            "json_valid": True,
                            "retry_attempt": attempt
                        }
                        
                        self.logger.info(f"✅ OpenAI Analyse erfolgreich für {wcag_area} (Versuch {attempt + 1})")
                        self.logger.info(f"Token-Verbrauch: {response.usage.total_tokens} tokens")
                        
                        return analysis_result
                        
                    except json.JSONDecodeError as json_err:
                        # Mit response_format sollte das NIEMALS passieren!
                        self.logger.error(f"❌ Unerwarteter JSON-Fehler trotz response_format für {wcag_area}: {json_err}")
                        self.logger.error(f"Raw response: {raw_content[:500]}")
                        
                        # Kein Retry bei JSON-Fehlern - das deutet auf ein größeres Problem hin
                        return {
                            "wcag_area": wcag_area,
                            "timestamp": time.strftime("%Y-%m-%d_%H-%M-%S"),
                            "model_used": self.model,
                            "analysis_content": raw_content,
                            "parsed_json": None,
                            "token_usage": {
                                "prompt_tokens": response.usage.prompt_tokens,
                                "completion_tokens": response.usage.completion_tokens,
                                "total_tokens": response.usage.total_tokens
                            },
                            "api_call_successful": True,
                            "json_valid": False,
                            "retry_attempt": attempt,
                            "json_error": str(json_err),
                            "debug_info": {
                                "raw_response_length": len(raw_content),
                                "error_position": f"line {getattr(json_err, 'lineno', 'unknown')} col {getattr(json_err, 'colno', 'unknown')}",
                                "note": "JSON error despite response_format=json_object - this should not happen!"
                            }
                        }
            
                except Exception as api_err:
                    self.logger.error(f"❌ OpenAI API Fehler für {wcag_area} (Versuch {attempt + 1}): {api_err}")
                    
                    if attempt < max_retries:
                        self.logger.info(f"🔄 Starte API-Retry {attempt + 2}/{max_retries + 1} für {wcag_area}")
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                        return {
                            "wcag_area": wcag_area,
                            "timestamp": time.strftime("%Y-%m-%d_%H-%M-%S"),
                            "api_call_successful": False,
                            "error": str(api_err),
                            "analysis_content": None,
                            "retry_attempt": attempt
                        }
            
        except Exception as e:
            self.logger.error(f"❌ OpenAI API Fehler für {wcag_area}: {e}")
            return {
                "wcag_area": wcag_area,
                "timestamp": time.strftime("%Y-%m-%d_%H-%M-%S"),
                "api_call_successful": False,
                "error": str(e),
                "analysis_content": None
            }
    
    def analyze_single_expert_prompt_with_data(self, expert_prompts_dir: str, wcag_area: str, technical_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analysiert einen einzelnen Expert-Prompt MIT technischen Daten
        
        Args:
            expert_prompts_dir: Verzeichnis mit den Expert-Prompts
            wcag_area: WCAG-Bereich (z.B. '1_1_textalternativen')
            technical_data: Technische Daten von der Website-Analyse
        
        Returns:
            Dict mit Analyse-Ergebnissen
        """
        try:
            self.logger.info(f"Lade Expert-Prompt für WCAG-Bereich: {wcag_area}")
            
            # Lade den Expert-Prompt
            prompt_file = Path(expert_prompts_dir) / f"prompt_{wcag_area}.md"
            if not prompt_file.exists():
                self.logger.error(f"Prompt-Datei nicht gefunden: {prompt_file}")
                return {
                    "wcag_area": wcag_area,
                    "api_call_successful": False,
                    "error": f"Prompt-Datei nicht gefunden: {prompt_file}"
                }
            
            with open(prompt_file, 'r', encoding='utf-8') as f:
                expert_prompt = f.read()
            
            # Erstelle den universellen Placeholder-Namen
            placeholder = "{WEBSITE_ANALYSIS_DATA}"
            
            # Konvertiere technische Daten zu JSON
            technical_data_str = json.dumps(technical_data, indent=2, ensure_ascii=False)
            
            # Versuche Placeholder zu ersetzen
            if placeholder in expert_prompt:
                expert_prompt_with_data = expert_prompt.replace(placeholder, technical_data_str)
                self.logger.info(f"✅ Universeller Placeholder erfolgreich ersetzt")
            else:
                # Fallback: Füge Daten am Ende hinzu
                expert_prompt_with_data = f"{expert_prompt}\n\n## Website-Analysedaten\n```json\n{technical_data_str}\n```"
                self.logger.warning(f"⚠️ Universeller Placeholder nicht gefunden, hänge Daten an")
            
            self.logger.info(f"Expert-Prompt für {wcag_area} mit technischen Daten erfolgreich geladen")
            
            # Führe Analyse durch
            return self.analyze_with_expert_prompt(expert_prompt_with_data, wcag_area)
        except Exception as e:
            self.logger.error(f"Fehler beim Laden des Expert-Prompts für {wcag_area}: {e}")
            return {
                "wcag_area": wcag_area,
                "api_call_successful": False,
                "error": str(e)
            }
    
    def analyze_single_expert_prompt(self, expert_prompts_dir: str, wcag_area: str) -> Dict[str, Any]:
        """
        Analysiert einen einzelnen Expert-Prompt
        
        Args:
            expert_prompts_dir: Verzeichnis mit generierten Expert-Prompts
            wcag_area: WCAG-Bereich (z.B. "1_1_textalternativen")
            
        Returns:
            Dict mit Analyse-Ergebnissen
        """
        prompts_path = Path(expert_prompts_dir)
        prompt_file = prompts_path / f"prompt_{wcag_area}.md"
        
        if not prompt_file.exists():
            self.logger.error(f"❌ Expert-Prompt Datei nicht gefunden: {prompt_file}")
            return None
        
        self.logger.info(f"📋 Analysiere einzelnen WCAG-Bereich: {wcag_area}")
        
        # Expert-Prompt laden
        with open(prompt_file, 'r', encoding='utf-8') as f:
            expert_prompt = f.read()
        
        # Analyse durchführen
        return self.analyze_with_expert_prompt(expert_prompt, wcag_area)
    
    def save_analysis_results(self, results: Dict[str, Any], output_file: str) -> None:
        """
        Speichert Analyse-Ergebnisse in JSON-Datei
        
        Args:
            results: Analyse-Ergebnisse
            output_file: Ausgabe-Datei
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"💾 Analyse-Ergebnisse gespeichert: {output_file}")

def main():
    """Test-Funktion für standalone Ausführung"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    try:
        # OpenAI Analyzer initialisieren
        analyzer = OpenAIWCAGAnalyzer()
        
        # Expert-Prompts Verzeichnis
        expert_prompts_dir = Path(__file__).parent.parent.parent / "expert_prompts" / "generated_prompts"
        
        # Teste eine einzelne Analyse - 1.1 Textalternativen
        print("🚀 Starte Test-Analyse: WCAG 1.1 Textalternativen...")
        result = analyzer.analyze_single_expert_prompt(str(expert_prompts_dir), "1_1_textalternativen")
        
        # Ergebnisse speichern
        output_file = f"openai_test_analysis_{time.strftime('%Y-%m-%d_%H-%M-%S')}.json"
        analyzer.save_analysis_results(result, output_file)
        
        if result.get("api_call_successful"):
            print(f"✅ Test erfolgreich!")
            print(f"📄 Ergebnisse: {output_file}")
            print(f"🎯 Token-Verbrauch: {result['token_usage']['total_tokens']}")
            print(f"📝 Erste 300 Zeichen der Analyse:")
            print(result['analysis_content'][:300] + "...")
        else:
            print(f"❌ Test fehlgeschlagen: {result.get('error')}")
        
    except Exception as e:
        print(f"❌ Fehler bei der Analyse: {e}")

if __name__ == "__main__":
    main() 