#!/usr/bin/env python3
"""
BarrierefreiCheck - Expert Prompt Generator
Automatische Generierung von WCAG-Experten-Prompts mit extrahierten Daten
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List
import logging
from datetime import datetime

# Mapping von WCAG-Kriterien zu Datenquellen - VEREINFACHT
WCAG_DATA_MAPPING = {
    "1_1_textalternativen": {
        "prompt_file": "prompt_1_1_textalternativen.md"
    },
    "1_2_zeitbasierte_medien": {
        "prompt_file": "prompt_1_2_zeitbasierte_medien.md"
    },
    "1_3_anpassbare_darstellung": {
        "prompt_file": "prompt_1_3_anpassbare_darstellung.md"
    },
    "1_4_wahrnehmbare_unterscheidungen": {
        "prompt_file": "prompt_1_4_wahrnehmbare_unterscheidungen.md"
    },
    "2_1_tastaturbedienung": {
        "prompt_file": "prompt_2_1_tastaturbedienung.md"
    },
    "2_2_genuegend_zeit": {
        "prompt_file": "prompt_2_2_genuegend_zeit.md"
    },
    "2_3_anfaelle_vermeiden": {
        "prompt_file": "prompt_2_3_anfaelle_vermeiden.md"
    },
    "2_4_navigation": {
        "prompt_file": "prompt_2_4_navigation.md"
    },
    "3_1_lesbarkeit_sprache": {
        "prompt_file": "prompt_3_1_lesbarkeit_sprache.md"
    },
    "3_2_vorhersehbarkeit": {
        "prompt_file": "prompt_3_2_vorhersehbarkeit.md"
    },
    "3_3_eingabeunterstuetzung": {
        "prompt_file": "prompt_3_3_eingabeunterstuetzung.md"
    },
    "4_1_robustheit_kompatibilitaet": {
        "prompt_file": "prompt_4_1_robustheit_kompatibilitaet.md"
    }
}

# Universeller Platzhalter für alle Prompts
UNIVERSAL_PLACEHOLDER = "{WEBSITE_ANALYSIS_DATA}"

class ExpertPromptGenerator:
    """Generator für WCAG-Expert-Prompts mit universellen Analysedaten"""
    
    def __init__(self, prompts_dir: str = "."):
        self.prompts_dir = Path(prompts_dir)
        self.logger = logging.getLogger(__name__)
        
    def validate_prompt_template(self, template: str, prompt_file: str) -> bool:
        """Überprüft ein Prompt-Template auf unerwünschte hartcodierte Daten"""
        problematic_patterns = [
            "ecomtask.de",
            "example.com",
            "beispiel.de",
            "www.",
            "http://",
            "https://",
            # Weitere typische Website-Muster
            ".com",
            ".de",
            ".org",
            ".net"
        ]
        
        for pattern in problematic_patterns:
            if pattern in template.lower():
                self.logger.warning(f"⚠️ Warnung: Möglicherweise hartcodierte Website-Daten gefunden ({pattern}) in {prompt_file}")
                return False
        return True
    
    def generate_expert_prompt(self, wcag_area: str, complete_analysis_data: Dict[str, Any]) -> str:
        """Generiere einen Expert-Prompt für einen spezifischen WCAG-Bereich mit allen Analysedaten"""
        if wcag_area not in WCAG_DATA_MAPPING:
            raise ValueError(f"Unbekannter WCAG-Bereich: {wcag_area}")
        
        mapping = WCAG_DATA_MAPPING[wcag_area]
        
        # Lade Prompt-Template
        prompt_path = self.prompts_dir / mapping["prompt_file"]
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt-Template nicht gefunden: {prompt_path}")
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
        
        # Validiere Template
        if not self.validate_prompt_template(prompt_template, mapping["prompt_file"]):
            self.logger.error(f"❌ Template enthält möglicherweise hartcodierte Website-Daten: {mapping['prompt_file']}")
        
        # Füge Metadaten hinzu
        complete_analysis_data["meta"] = {
            "wcag_area": wcag_area,
            "generated_at": datetime.now().isoformat(),
            "version": "2.0",
            "analysis_type": "complete_wcag_analysis",
            "universal_data": True
        }
        
        # Erstelle formatierten JSON-String für bessere Lesbarkeit
        formatted_data = json.dumps(complete_analysis_data, indent=2, ensure_ascii=False)
        
        # Ersetze universellen Placeholder mit allen Daten
        if UNIVERSAL_PLACEHOLDER in prompt_template:
            expert_prompt = prompt_template.replace(UNIVERSAL_PLACEHOLDER, formatted_data)
            self.logger.info(f"✅ Universeller Placeholder erfolgreich ersetzt für {wcag_area}")
        else:
            # Fallback: Füge Daten am Ende hinzu
            expert_prompt = f"{prompt_template}\n\n## Website-Analysedaten\n```json\n{formatted_data}\n```"
            self.logger.warning(f"⚠️ Universeller Placeholder nicht gefunden in {mapping['prompt_file']}, hänge Daten an")
        
        return expert_prompt
    
    def generate_all_prompts(self, complete_analysis_data: Dict[str, Any], output_dir: str = "generated_prompts") -> Dict[str, str]:
        """Generiere alle Expert-Prompts mit den vollständigen Analysedaten"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        generated_prompts = {}
        
        for wcag_area in WCAG_DATA_MAPPING.keys():
            try:
                self.logger.info(f"Generiere Prompt für WCAG-Bereich: {wcag_area}")
                
                expert_prompt = self.generate_expert_prompt(wcag_area, complete_analysis_data)
                
                # Speichere generierten Prompt
                output_file = output_path / f"prompt_{wcag_area}.md"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(expert_prompt)
                
                generated_prompts[wcag_area] = str(output_file)
                self.logger.info(f"✅ Prompt gespeichert: {output_file}")
                
            except Exception as e:
                self.logger.error(f"❌ Fehler bei Generierung für {wcag_area}: {e}")
                continue
        
        return generated_prompts
    
    def create_prompt_summary(self, generated_prompts: Dict[str, str]) -> str:
        """Erstelle eine Zusammenfassung aller generierten Prompts"""
        summary = """# 🎯 WCAG Expert-Prompts - Generiert mit kompletten Analysedaten

## Übersicht
Diese Prompts wurden automatisch mit den vollständigen Website-Analysedaten generiert.
Jeder Prompt enthält alle verfügbaren Daten und konzentriert sich auf spezifische WCAG-Kriterien.

## Verwendung mit ChatGPT-4
1. Kopiere den gewünschten Prompt vollständig
2. Füge ihn in ChatGPT-4 ein  
3. Erhalte eine detaillierte, datenbasierte Barrierefreiheits-Analyse

## Verfügbare Expert-Prompts:

"""
        
        for wcag_area, file_path in generated_prompts.items():
            mapping = WCAG_DATA_MAPPING[wcag_area]
            summary += f"### {wcag_area.replace('_', '.')}\n"
            summary += f"**Datei:** `{Path(file_path).name}`\n"
            summary += f"**Fokus:** {mapping['prompt_file'].replace('prompt_', '').replace('.md', '').replace('_', ' ').title()}\n"
            summary += f"**Daten:** Alle verfügbaren Analysedaten\n\n"
        
        summary += """
## Datenqualität
- ✅ Alle Prompts enthalten komplette Analysedaten
- ✅ JSON-Strukturen sind für ChatGPT-4 optimiert  
- ✅ Kontextuelle Anleitungen für präzise Analysen
- ✅ Praktische, umsetzbare Empfehlungen

## Nächste Schritte
1. Wähle den relevanten WCAG-Bereich für deine Analyse
2. Verwende den entsprechenden Expert-Prompt
3. Implementiere die erhaltenen Empfehlungen
4. Re-teste mit aktualisiertem BarrierefreiCheck

---
*Automatisch generiert vom BarrierefreiCheck Expert-Prompt-Generator*
"""
        
        return summary

def main():
    """Hauptfunktion zur Prompt-Generierung - Beispiel-Implementierung"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Initialisiere Generator
    generator = ExpertPromptGenerator()
    
    # Beispiel-Analysedaten (normalerweise von run_complete_analysis.py bereitgestellt)
    example_analysis_data = {
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "base_url": "https://example.com",
            "total_pages": 5
        },
        "crawl_results": {
            "pages_crawled": 5,
            "base_url": "https://example.com",
            "data": {}
        },
        "accessibility_results": {
            "violations": [],
            "warnings": [],
            "passed": []
        },
        "mapped_wcag_data": {},
        "context_info": {
            "page_structure": {
                "total_pages": 5,
                "base_url": "https://example.com"
            }
        }
    }
    
    # Generiere alle Prompts
    print("🎯 Starte Expert-Prompt-Generierung...")
    print("⚠️ HINWEIS: Diese main-Funktion verwendet Beispieldaten.")
    print("   In der Praxis werden die Daten von run_complete_analysis.py bereitgestellt.")
    
    generated_prompts = generator.generate_all_prompts(example_analysis_data)
    
    if generated_prompts:
        print(f"\n✅ {len(generated_prompts)} Expert-Prompts erfolgreich generiert!")
        
        # Erstelle Zusammenfassung
        summary = generator.create_prompt_summary(generated_prompts)
        summary_file = Path("generated_prompts/README.md")
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"📋 Zusammenfassung erstellt: {summary_file}")
        
        # Zeige generierte Dateien
        print("\n📁 Generierte Expert-Prompts:")
        for wcag_area, file_path in generated_prompts.items():
            print(f"   • {wcag_area}: {file_path}")
            
    else:
        print("❌ Keine Prompts konnten generiert werden.")

if __name__ == "__main__":
    main() 