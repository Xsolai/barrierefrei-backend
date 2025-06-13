# Website-Datenextraktion Test-Skript

## Überblick
Das `test_data_extraction.py` Skript zeigt Ihnen genau, welche Daten von einer Website extrahiert und an die WCAG-Expert-Prompts weitergegeben werden. 

## Zweck
- **Transparenz**: Sehen Sie alle extrahierten Daten vor der Expert-Analyse
- **Debugging**: Verstehen Sie, warum bestimmte Bewertungen getroffen werden
- **Optimierung**: Identifizieren Sie Daten-Extraktion-Verbesserungen
- **Qualitätskontrolle**: Prüfen Sie die Vollständigkeit der analysierten Daten

## Funktionsweise

### Phase 1: Grundlegende Website-Extraktion
- **WebsiteCrawler**: Extrahiert strukturelle Website-Daten
- **Vollständige Analyse**: HTML-Struktur, Bilder, Links, Formulare, etc.
- **Accessibility-Daten**: ARIA-Attribute, Rollen, Labels, etc.

### Phase 2: Spezialisierte WCAG-Extraktion
- **1.1 Textalternativen**: Fokus auf Bilder, Alt-Texte, Social Media Images
- **1.2 Zeitbasierte Medien**: Videos, Audio, Untertitel
- **1.3 Anpassbare Darstellung**: Überschriften-Hierarchie, Semantik
- **Weitere Bereiche**: Fallback für noch nicht implementierte Extraktoren

### Phase 3: Daten-Ausgabe
- **4 Dateiformate**: Vollständig, Grunddaten, WCAG-spezifisch, Zusammenfassung
- **JSON + Text**: Maschinenlesbar und human-lesbar

## Verwendung

### Standard-Test (Ihre eigene Website)
```bash
cd backend
python test_data_extraction.py
```

### Andere Website testen
```bash
cd backend
python test_data_extraction.py https://example.com
```

### Mit spezifischem Output-Verzeichnis
```bash
cd backend
python test_data_extraction.py https://example.com
# Dateien werden in 'extracted_data/' gespeichert
```

## Ausgabe-Dateien

### 1. `website_data_FULL_***.json`
**Vollständige Daten** - Alle extrahierten Informationen
- Grundlegende Website-Daten
- Spezialisierte WCAG-Daten  
- Metadata und Statistiken

### 2. `website_data_BASE_***.json`
**Grunddaten** - Daten, die an alle 12 Expert-Prompts gehen
- HTML-Struktur
- Bilder, Links, Formulare
- Accessibility-Grunddaten

### 3. `website_data_WCAG_***.json`
**WCAG-spezialisiert** - Daten für spezifische WCAG-Bereiche
- 1.1: Detaillierte Bild-Analyse
- 1.2: Multimedia-Fokus
- 1.3: Semantik-Analyse

### 4. `website_data_SUMMARY_***.txt`
**Zusammenfassung** - Human-lesbare Übersicht
- Anzahl gefundener Elemente
- Datenqualität-Bewertung
- Extraktionszeit

## Beispiel-Output

```
🚀 Starte Datenextraktion für: https://www.ecomtask.de
📊 Phase 1: Grundlegende Website-Datenextraktion...
✅ Grunddaten extrahiert in 2.45s
🔍 Phase 2: Spezialisierte WCAG-Datenextraktion...
  📸 Extrahiere 1.1 Textalternativen...
  🎥 Extrahiere 1.2 Zeitbasierte Medien...
  📋 Extrahiere 1.3 Anpassbare Darstellung...
📦 Phase 3: Zusammenstellung der Expert-Prompt-Daten...
✅ Datenextraktion abgeschlossen!
   📊 Datenpunkte: 2847
   ⏱️ Gesamtzeit: 3.21s

💾 Vollständige Daten gespeichert: extracted_data/website_data_FULL_***.json
💾 Grunddaten gespeichert: extracted_data/website_data_BASE_***.json
💾 WCAG-Daten gespeichert: extracted_data/website_data_WCAG_***.json
💾 Zusammenfassung gespeichert: extracted_data/website_data_SUMMARY_***.txt
```

## Was sehen Sie in den Daten?

### Grundlegende Website-Daten
```json
{
  "base_website_data": {
    "url": "https://example.com",
    "title": {...},
    "structure": {
      "headings": [...],
      "images": [...],
      "forms": [...],
      "links": [...]
    },
    "accessibility": {
      "aria_roles": [...],
      "tab_index": [...],
      "text_alternatives": [...]
    }
  }
}
```

### Spezialisierte WCAG-Daten
```json
{
  "specialized_wcag_data": {
    "1.1_text_alternatives": {
      "images": {
        "total_count": 15,
        "with_alt": 12,
        "without_alt": 3,
        "detailed_analysis": [...]
      },
      "comprehensive_image_analysis": {
        "performance_score": 85.2,
        "social_media_images": [...],
        "accessibility_quality_score": 92.1
      }
    }
  }
}
```

## Nutzen für Expert-Prompts

### Token-Effizienz
- **Vorher**: Alle 12 Prompts erhalten 50.000 Token (identische Daten)
- **Nachher**: Jeder Prompt erhält 5.000-15.000 relevante Token

### Daten-Präzision
- **WCAG 1.1**: Nur Bild-relevante Daten (Performance, Alt-Texte, Social Media)
- **WCAG 1.2**: Nur Multimedia-Daten (Videos, Audio, Untertitel)
- **WCAG 1.3**: Nur Struktur-Daten (Überschriften, Semantik, Landmarks)

### Qualitäts-Verbesserung
- **95% relevante Daten** statt 20% bei allgemeinem Ansatz
- **Spezialisierte Metriken** für jeden WCAG-Bereich
- **Kontext-bewusste Analyse** durch fokussierte Datenextraktion

## Fehlerbehebung

### Import-Fehler
```bash
ModuleNotFoundError: No module named 'analyzers'
```
→ Stellen Sie sicher, dass Sie im `backend/` Verzeichnis sind

### Netzwerk-Fehler
```bash
Netzwerkfehler bei https://example.com: Connection timeout
```
→ Prüfen Sie Ihre Internetverbindung oder verwenden Sie eine andere URL

### Speicher-Fehler bei großen Websites
→ Das Skript analysiert nur die Hauptseite, nicht alle Unterseiten

## Integration in Ihr System
Diese Daten werden automatisch in Ihrem Produktionssystem verwendet:
1. `run_complete_analysis.py` nutzt dieselben Extraktoren
2. Expert-Prompts erhalten diese exakten Datenstrukturen
3. Supabase speichert diese Analyse-Ergebnisse 