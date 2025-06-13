#!/usr/bin/env python3
"""
Update Expert Prompts
Entfernt das redundante JSON-Format aus allen Expert Prompts
"""

import os
from pathlib import Path

def clean_prompt(content: str) -> str:
    """Entfernt das JSON-Format und behält nur die WCAG-Kriterien"""
    # Finde den Anfang des JSON-Formats
    format_markers = [
        "### Ausgabeformat",
        "## Antwortformat",
        "```json",
        "Bitte geben Sie Ihre Analyse im folgenden JSON-Format zurück:"
    ]
    
    for marker in format_markers:
        if marker in content:
            parts = content.split(marker)
            # Behalte nur den Teil bis zum Analysedaten-Abschnitt
            if "## Analysedaten" in parts[0]:
                content = parts[0].split("## Analysedaten")[0].strip()
                content += "\n\n## Analysedaten\n{" + content.split("{")[-1].strip()
            else:
                content = parts[0].strip()
    
    return content

def update_prompts():
    """Aktualisiert alle Expert Prompts"""
    # Finde alle .md Dateien im expert_prompts Verzeichnis
    prompts_dir = Path(__file__).parent
    md_files = prompts_dir.glob("prompt_*.md")
    
    updated = 0
    for md_file in md_files:
        if "generated_prompts" in str(md_file):
            continue
            
        print(f"Verarbeite {md_file.name}...")
        
        # Lese Original-Inhalt
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Entferne JSON-Format
        new_content = clean_prompt(content)
        
        # Speichere nur wenn sich etwas geändert hat
        if new_content != content:
            with open(md_file, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"✅ {md_file.name} aktualisiert")
            updated += 1
        else:
            print(f"⏩ Keine Änderungen nötig in {md_file.name}")
    
    print(f"\n🎉 Fertig! {updated} Prompts aktualisiert")

if __name__ == "__main__":
    update_prompts() 