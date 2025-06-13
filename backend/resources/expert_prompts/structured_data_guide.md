# Strukturierte Datennutzung in WCAG Expert-Prompts

## Optimierte Datenstruktur

Die Website-Analysedaten werden jetzt in einer optimierten Struktur bereitgestellt:

```json
{
  "wcag_area": "1_1_textalternativen",
  "summary_statistics": {
    "total_images": 50,
    "images_without_alt": 5,
    "images_with_alt": 45,
    "alt_coverage_percentage": 90.0,
    "critical_issues": 5
  },
  "critical_findings": [
    {
      "type": "missing_alt",
      "severity": "critical",
      "element": {
        "src": "/images/hero.jpg",
        "context": "Hero-Banner auf Startseite"
      }
    }
  ],
  "representative_examples": {
    "good_practices": [
      {
        "alt": "CEO Maria Schmidt lächelt in die Kamera",
        "src": "/team/ceo.jpg"
      }
    ],
    "violations": [
      {
        "issue": "missing_alt",
        "src": "/products/product-123.jpg"
      }
    ]
  },
  "context": {
    "pages_analyzed": ["https://example.com", "https://example.com/about"],
    "total_elements_checked": 50
  }
}
```

## Wie Sie die Daten nutzen sollten

### 1. **Beginnen Sie mit summary_statistics**
- Verschaffen Sie sich einen Überblick
- Berechnen Sie den Basis-Score basierend auf der Fehlerquote

### 2. **Analysieren Sie critical_findings**
- Diese sind die wichtigsten Probleme
- Jedes kritische Problem = -15 Punkte

### 3. **Nutzen Sie representative_examples**
- Geben Sie konkrete Beispiele in Ihrer Bewertung
- Zeigen Sie sowohl gute als auch schlechte Praktiken

### 4. **Berücksichtigen Sie den context**
- Wie viele Seiten wurden analysiert?
- Ist die Stichprobe repräsentativ?

## Beispiel-Bewertungslogik

```
WENN summary_statistics.total_images == 0:
    RETURN Score: 100, "Keine Bilder gefunden"

SONST:
    fehlerquote = summary_statistics.images_without_alt / summary_statistics.total_images
    
    basis_score = 100
    
    # Kritische Abzüge
    kritische_abzuege = MIN(45, critical_findings.length * 15)
    
    # Fehlerquoten-Abzug
    WENN fehlerquote > 0.5:
        zusatz_abzug = 30
    WENN fehlerquote > 0.3:
        zusatz_abzug = 20
    ...
    
    final_score = basis_score - kritische_abzuege - zusatz_abzug
```

## Wichtige Hinweise

1. **Daten sind voroptimiert**: Sie müssen nicht mehr durch hunderte Bilder iterieren
2. **Fokus auf Wesentliches**: Die kritischen Findings sind bereits identifiziert
3. **Beispiele nutzen**: Verwenden Sie die konkreten Beispiele in Ihrer Bewertung
4. **Kontext beachten**: Eine Seite mit 5 Bildern ist anders zu bewerten als eine mit 500 