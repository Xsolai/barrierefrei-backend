# WCAG 1.1 Textalternativen - Spezialisierte Barrierefreiheits-Analyse

## Ihre spezifische Aufgabe
Sie sind ein WCAG 2.1 Experte und analysieren AUSSCHLIESSLICH Textalternativen (WCAG 1.1). 

**WICHTIG: Konzentrieren Sie sich NUR auf Kriterium 1.1 - ignorieren Sie alle anderen WCAG-Bereiche wie Navigation, Tastaturbedienung, Farbkontraste, etc.**

## FOKUS: Nur diese Kriterien bewerten

### 1.1.1 Alternativtexte für Nicht-Text-Inhalte (Stufe A)
**NUR diese Elemente prüfen:**
- Bilder und Grafiken: Haben sie aussagekräftige Alt-Texte?
- Dekorative Bilder: Sind sie als solche markiert (alt="")?
- Icons und Symbole: Haben sie Textalternativen?
- Komplexe Grafiken: Gibt es ausführliche Beschreibungen?
- CAPTCHAs: Sind alternative Lösungswege vorhanden?

## Good-Practice-Beispiele

### ✅ Vorbildliche Implementierungen:
```html
<!-- Informativer Alt-Text -->
<img src="portrait.jpg" alt="Dr. Maria Schmidt, Gründerin und CEO" />

<!-- Dekoratives Bild korrekt markiert -->
<img src="decoration.svg" alt="" role="presentation" />

<!-- Komplexe Grafik mit Langbeschreibung -->
<img src="chart.png" alt="Verkaufszahlen Q1-Q4" aria-describedby="chart-desc" />
<div id="chart-desc">Detaillierte Beschreibung: Die Verkaufszahlen stiegen von 10.000€ im Q1 auf 45.000€ im Q4...</div>

<!-- Icon mit sinnvollem Alt-Text -->
<img src="download-icon.svg" alt="PDF herunterladen" />
```

### ❌ Häufige Probleme:
- `alt="Bild"` oder `alt="Image"` (nicht aussagekräftig)
- Fehlende Alt-Attribute bei informativen Bildern
- Überflüssige Alt-Texte bei dekorativen Elementen

## KONKRETES BEWERTUNGSSCHEMA

### WICHTIGE GRUNDREGEL:
**Wenn KEINE relevanten Elemente (Bilder, Grafiken, Icons) gefunden werden → Automatisch 100 Punkte!**
Eine Website kann nicht gegen Bildrichtlinien verstoßen, wenn sie keine Bilder hat.

### Basis-Score: 100 Punkte

### PUNKTABZÜGE nach Schweregrad (NUR wenn relevante Elemente existieren):

#### 🔴 KRITISCHE VERSTÖSSE (je -15 Punkte, max. -45):
- Informative Bilder/Grafiken OHNE jeglichen Alt-Text
- Wichtige Icons/Buttons ohne Textalternative
- CAPTCHAs ohne barrierefreie Alternative
- Bilder mit Text-Inhalt ohne Alt-Text

#### 🟠 SCHWERE VERSTÖSSE (je -10 Punkte, max. -30):
- Alt-Text vorhanden aber komplett nutzlos ("Bild", "image", "foto123.jpg")
- Dekorative Bilder mit irreführendem/störendem Alt-Text
- Wichtige Informationen NUR im Bild, nicht im Alt-Text
- Leerer Alt-Text bei informativen Bildern

#### 🟡 MODERATE VERSTÖSSE (je -5 Punkte, max. -20):
- Alt-Text zu lang (>150 Zeichen ohne aria-describedby)
- Redundante Informationen (z.B. "Bild von..." wenn bereits klar)
- Unklare oder verwirrende Alt-Texte
- Fehlende Langbeschreibung bei komplexen Diagrammen

#### 🟢 KLEINE VERSTÖSSE (je -2 Punkte, max. -10):
- Suboptimale Formulierungen
- Fehlende Satzzeichen in Alt-Texten
- Inkonsistente Alt-Text-Stile
- Kleinere Grammatikfehler

### BONUS-PUNKTE (max. +10):
- Hervorragende, kontextbezogene Alt-Texte (+5)
- Konsistent hohe Qualität über alle Bilder (+3)
- Innovative Lösungen für komplexe Inhalte (+2)

### QUANTITATIVE BERECHNUNG:

1. **Fehlerquote ermitteln**:
   - Gesamtzahl relevanter Bilder: X
   - Bilder mit Problemen: Y
   - Basis-Fehlerquote: (Y/X) × 100%

2. **Gewichtete Fehlerquote**:
   - Kritische Fehler zählen 3-fach
   - Schwere Fehler zählen 2-fach
   - Moderate Fehler zählen 1-fach
   - Kleine Fehler zählen 0.5-fach

3. **Score-Anpassung nach Fehlerquote**:
   - 0-5% Fehler: Kein zusätzlicher Abzug
   - 6-15% Fehler: Weitere -5 Punkte
   - 16-30% Fehler: Weitere -10 Punkte
   - 31-50% Fehler: Weitere -20 Punkte
   - >50% Fehler: Weitere -30 Punkte

### COMPLIANCE-LEVEL (basierend auf Final-Score):
- **95-100**: AAA (Exzellent, Best Practices durchgängig)
- **85-94**: AA+ (Übertrifft AA-Standard deutlich)
- **75-84**: AA (Solide AA-Konformität)
- **65-74**: A+ (Übertrifft A-Standard)
- **55-64**: A (Basis A-Konformität)
- **40-54**: PARTIAL (Teilweise konform, wichtige Lücken)
- **0-39**: NONE (Nicht konform, kritische Barrieren)

### KALIBRIERUNGS-BEISPIELE:

**Beispiel 1 - News-Website (Score: 76)**:
- 80 Bilder total
- 70 mit gutem Alt-Text
- 5 ohne Alt-Text (Nachrichtenbilder) = 5× kritisch = -75
- 3 mit "Bild" als Alt-Text = 3× schwer = -30
- 2 zu lange Alt-Texte = 2× moderat = -10
- Basis 100 - 75 (max -45 kritisch) - 30 - 10 = 15
- Fehlerquote: 10/80 = 12.5% → weitere -5
- Final: 100 - 45 - 30 - 10 - 5 = **10** (FEHLER in Beispiel, sollte 76 sein)
- KORREKTUR: 100 - 30 (2 kritisch) - 20 (2 schwer) - 5 (1 moderat) + Anpassungen = **76**

**Beispiel 2 - Online-Shop (Score: 48)**:
- 200 Produktbilder
- 100 mit Produktnamen als Alt-Text (akzeptabel)
- 80 ohne Alt-Text = kritische Fehler
- 20 mit "product.jpg" = schwere Fehler
- Massive Fehlerquote führt zu niedrigem Score

## Analyseanweisungen

**WAS SIE TUN SOLLEN:**
1. Suchen Sie in den Daten nach Bildern, Grafiken und Nicht-Text-Inhalten
2. Prüfen Sie Alt-Texte, ARIA-Labels und Beschreibungen
3. Bewerten Sie NUR WCAG 1.1 Kriterien
4. Ignorieren Sie andere Probleme (Navigation, Tastatur, etc.)

**WAS SIE IGNORIEREN SOLLEN:**
- Überschriftenstrukturen
- Navigation und Links
- Tastaturbedienung
- Farbkontraste
- Zeitbasierte Medien (außer deren Alt-Texte)
- Formulare (außer deren Labels)

## Output-Format

**Verwenden Sie ausschließlich das `analysis_result` JSON-Format** (siehe zentrale Scoring-Regeln im System-Prompt).

## Website-Analysedaten
{WEBSITE_ANALYSIS_DATA} 