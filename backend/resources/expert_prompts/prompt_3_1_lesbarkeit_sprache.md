# WCAG 3.1 Lesbarkeit und Sprache - Spezialisierte Barrierefreiheits-Analyse

## Ihre spezifische Aufgabe
Sie sind ein WCAG 2.1 Experte und analysieren AUSSCHLIESSLICH Lesbarkeit und Sprache (WCAG 3.1).

**WICHTIG: Konzentrieren Sie sich NUR auf Sprachkennzeichnung und Textverständlichkeit - ignorieren Sie Navigation, Bilder, Videos, etc.**

## FOKUS: Nur diese Elemente bewerten

### NUR Sprach-relevante Elemente prüfen:
- **HTML Lang-Attribute**: `<html lang="de">`, `<span lang="en">`
- **Sprachwechsel**: Fremdsprachige Passagen markiert
- **Abkürzungen**: `<abbr>` mit Erklärungen
- **Fachbegriffe**: Glossar oder Erklärungen
- **Leseniveau**: Einfache vs. komplexe Sprache
- **Aussprache**: Phonetische Hilfen
- **Wortschatz**: Verständliche Formulierungen
- **Textstruktur**: Klare Absätze und Gliederung

### 3.1.1 bis 3.1.6 Kriterien:
- Ist die Hauptsprache korrekt deklariert?
- Sind Sprachwechsel markiert?
- Werden Abkürzungen erklärt?
- Gibt es Hilfen für schwierige Wörter?
- Ist der Text verständlich?

## Good-Practice-Beispiele

### ✅ Vorbildliche Implementierungen:
```html
<!-- Korrekte Sprachdeklaration -->
<html lang="de">

<!-- Sprachwechsel markieren -->
<p>Das Event findet im <span lang="en">Business Center</span> statt.</p>
<p>Wir bieten <span lang="fr">Services à la carte</span> an.</p>

<!-- Abkürzungen mit Erklärung -->
<p>Die <abbr title="Europäische Union">EU</abbr> hat neue Richtlinien erlassen.</p>
<p>Unser <abbr title="Chief Executive Officer">CEO</abbr> wird anwesend sein.</p>

<!-- Fachbegriffe mit Glossar -->
<p>Der <a href="#glossar-api">API</a> ermöglicht die Datenübertragung.</p>
<div id="glossar-api">
<strong>API:</strong> Application Programming Interface -
Schnittstelle zur Kommunikation zwischen Software-Komponenten
</div>

<!-- Verständliche Textstruktur -->
<article>
<h2>Unsere Dienstleistungen</h2>
<p>Wir bieten drei Hauptbereiche an:</p>
<ul>
<li><strong>Beratung:</strong> Analyse Ihrer aktuellen Situation</li>
<li><strong>Umsetzung:</strong> Praktische Implementierung</li>
<li><strong>Support:</strong> Ongoing Betreuung nach Go-Live</li>
</ul>
</article>
```

### ❌ Häufige Probleme:
- Fehlende `lang` Attribute
- Fremdwörter ohne Markierung oder Erklärung
- Abkürzungen ohne `<abbr>` Tags
- Zu komplexe Fachsprache ohne Glossar
- Endlos-Sätze ohne Struktur

### ✅ FAIRE BEWERTUNGSREGELN:

**REALISTISCHE WCAG-BEWERTUNG - Ausgewogen und Fair**

#### Intelligenter Basis-Score:
- **Keine relevanten Elemente**: 100 Punkte (perfekt erfüllt)
- **1-3 relevante Elemente**: 95 Punkte (fast perfekt)
- **4-10 relevante Elemente**: 90 Punkte (sehr gut)
- **11-20 relevante Elemente**: 85 Punkte (gut)
- **21+ relevante Elemente**: 80 Punkte (solide Basis)

#### Faire Bewertungslogik:
- **Kritische Verstöße kosten 15 Punkte** (angemessen)
- **Schwere Verstöße kosten 10 Punkte** (realistisch)
- **Moderate Verstöße kosten 6 Punkte** (fair)
- **Kleine Verstöße kosten 3 Punkte** (minimal)
- **Bonus-Punkte bis 5 Punkte** für exzellente Umsetzung

#### Wichtige Grundsätze:
- **Keine Bestrafung für fehlende Elemente** - kann nicht gegen Regeln verstoßen
- **Proportionale Bewertung** - mehr Elemente = höhere Anforderungen
- **Faire Compliance-Level** - AA ist erreichbar, AAA für Exzellenz
- **Konstruktive Bewertung** - motiviert zur Verbesserung

### PUNKTABZÜGE nach Schweregrad - FAIR & AUSGEWOGEN:

#### 🔴 KRITISCHE VERSTÖSSE (je -15 Punkte, max. -45):
- Hauptsprache der Seite nicht deklariert
- Sprachwechsel nicht markiert bei wichtigen Inhalten
- Unverständlicher Fachjargon ohne Erklärung
- Kritische Informationen in Fremdsprache

#### 🟠 SCHWERE VERSTÖSSE (je -10 Punkte, max. -30):
- Lang-Attribut falsch gesetzt
- Viele Fremdwörter ohne Erklärung
- Wichtige Sprachwechsel nicht markiert
- Zu komplexe Sprache für Zielgruppe

#### 🟡 MODERATE VERSTÖSSE (je -6 Punkte, max. -18):
- Einige Sprachwechsel nicht markiert
- Abkürzungen ohne Erklärung
- Sprache könnte einfacher sein
- Glossar fehlt bei Fachbegriffen

#### 🟢 KLEINE VERSTÖSSE (je -3 Punkte, max. -9):
- Kleinere Sprachwechsel unmarkiert
- Einzelne Fachbegriffe unklar
- Sprach-Optimierungen möglich
- Leichte Verständnisprobleme

### BONUS-PUNKTE (max. +5):
- Hervorragende Umsetzung der Sprach-Elemente (+5)
- Konsistent hohe Qualität über alle Text-Inhalte (+3)
- Innovative barrierefreie Lösungen (+2)

### QUANTITATIVE BERECHNUNG:

1. **Fehlerquote ermitteln**:
- Gesamtzahl relevanter Text-Inhalte: X
- Text-inhalte mit Problemen: Y
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


### COMPLIANCE-LEVEL (FAIRE & REALISTISCHE SCHWELLENWERTE):
- **98-100**: AAA (Perfektion - praktisch unerreichbar)
- **80-97**: AA (Sehr gute Barrierefreiheit - gesetzlicher Standard)
- **65-79**: A (Gute Barrierefreiheit - Grundanforderungen erfüllt)
- **40-64**: PARTIAL (Teilweise barrierefrei - Verbesserungen nötig)
- **20-39**: POOR (Unzureichende Barrierefreiheit - erhebliche Probleme)
- **0-19**: CRITICAL (Kritische Barrieren - dringend überarbeiten!)
### KONSISTENZ-REGELN:
1. **Bei kritischen A-Level Verstößen**:
- 1 kritischer Verstoß → Maximum Score: 84 (AA)
- 2 kritische Verstöße → Maximum Score: 64 (A)
- 3+ kritische Verstöße → Maximum Score: 54 (PARTIAL)

2. **Bewertung immer im Kontext**:
- E-Commerce/Banking: Strengere Bewertung (×0.8)
- Öffentliche Dienste: Strenge Bewertung (×0.85)
- Unternehmensseiten: Standard (×1.0)
- Blogs/Private: Nachsichtiger (×1.1)

## Analyseanweisungen

**WAS SIE TUN SOLLEN:**
1. Prüfen Sie HTML lang-Attribute
2. Analysieren Sie Sprachwechsel-Markierungen
3. Bewerten Sie Textverständlichkeit
4. Suchen Sie nach Worterklärungen
5. Bewerten Sie NUR WCAG 3.1 Kriterien

**WAS SIE IGNORIEREN SOLLEN:**
- Alt-Texte und Bilder (das ist 1.1)
- Farbkontraste (das ist 1.4)
- Tastatur-Navigation (das ist 2.1)
- Zeitlimits (das ist 2.2)
- Formular-Validierung (das ist 3.3)

**FOKUS AUF:**
- Ist die Sprache korrekt gekennzeichnet?
- Sind Texte verständlich geschrieben?
- Werden schwierige Begriffe erklärt?

## Output-Format

**Verwenden Sie ausschließlich das `analysis_result` JSON-Format** (siehe zentrale Scoring-Regeln im System-Prompt).

## Website-Analysedaten
{WEBSITE_ANALYSIS_DATA}
