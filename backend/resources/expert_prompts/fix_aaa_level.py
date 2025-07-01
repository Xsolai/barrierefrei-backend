#!/usr/bin/env python3
"""
Fix AAA Level - Make it practically unreachable
Setzt AAA-Level auf praktisch unerreichbare Werte (98+ oder entfernt es ganz)
"""

import os
import re
from pathlib import Path

def fix_aaa_level(content: str) -> str:
    """Macht AAA-Level praktisch unerreichbar"""
    
    # Aktuelle Compliance-Level ersetzen
    old_compliance = """### COMPLIANCE-LEVEL (FAIRE & REALISTISCHE SCHWELLENWERTE):
- **90-100**: AAA (Ausgezeichnete Barrierefreiheit - höchster Standard)
- **80-89**: AA (Sehr gute Barrierefreiheit - solider Standard)
- **65-79**: A (Gute Barrierefreiheit - Grundanforderungen erfüllt)
- **40-64**: PARTIAL (Teilweise barrierefrei - Verbesserungen nötig)
- **20-39**: POOR (Unzureichende Barrierefreiheit - erhebliche Probleme)
- **0-19**: CRITICAL (Kritische Barrieren - dringend überarbeiten!)"""
    
    # Neue Compliance-Level: AAA praktisch unmöglich
    new_compliance = """### COMPLIANCE-LEVEL (FAIRE & REALISTISCHE SCHWELLENWERTE):
- **98-100**: AAA (Perfektion - praktisch unerreichbar)
- **80-97**: AA (Sehr gute Barrierefreiheit - gesetzlicher Standard)
- **65-79**: A (Gute Barrierefreiheit - Grundanforderungen erfüllt)
- **40-64**: PARTIAL (Teilweise barrierefrei - Verbesserungen nötig)
- **20-39**: POOR (Unzureichende Barrierefreiheit - erhebliche Probleme)
- **0-19**: CRITICAL (Kritische Barrieren - dringend überarbeiten!)"""
    
    content = content.replace(old_compliance, new_compliance)
    
    # Auch Assessment-Texte anpassen
    content = content.replace(
        "if score >= 90:  # AAA",
        "if score >= 98:  # AAA"
    )
    
    content = content.replace(
        "- **AAA-Level (90+) für exzellente Implementierungen**",
        "- **AAA-Level (98+) praktisch nur bei Perfektion erreichbar**"
    )
    
    content = content.replace(
        "**90-100**: AAA (Ausgezeichnete Barrierefreiheit - höchster Standard)",
        "**98-100**: AAA (Perfektion - praktisch unerreichbar)"
    )
    
    content = content.replace(
        "**80-89**: AA (Sehr gute Barrierefreiheit - solider Standard)",
        "**80-97**: AA (Sehr gute Barrierefreiheit - gesetzlicher Standard)"
    )
    
    return content

def update_all_prompts():
    """Aktualisiert alle Expert Prompts mit unerreichbarem AAA-Level"""
    prompts_dir = Path(__file__).parent
    md_files = prompts_dir.glob("prompt_*.md")
    
    updated = 0
    for md_file in md_files:
        if "fix_" in str(md_file) or "make_" in str(md_file) or "cleanup" in str(md_file):
            continue
            
        print(f"AAA-Level Korrektur: {md_file.name}...")
        
        # Lese Original-Inhalt
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Korrigiere AAA-Level
        new_content = fix_aaa_level(content)
        
        # Speichere wenn sich etwas geändert hat
        if new_content != content:
            with open(md_file, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"✅ {md_file.name} - AAA auf 98+ gesetzt")
            updated += 1
        else:
            print(f"⏩ {md_file.name} - bereits korrekt")
    
    print(f"\n🎉 Fertig! {updated} Prompts korrigiert")
    print("🚨 AAA-Level jetzt bei 98+ (praktisch unerreichbar)")
    print("✅ AA-Level bleibt bei 80+ (gesetzlicher Standard)")
    print("📊 Kunden bekommen realistisch nur noch AA maximum")

if __name__ == "__main__":
    update_all_prompts() 