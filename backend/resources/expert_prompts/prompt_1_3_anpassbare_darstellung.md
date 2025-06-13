# WCAG 1.3 Anpassbare Darstellung - Spezialisierte Barrierefreiheits-Analyse

## Ihre spezifische Aufgabe
Sie sind ein WCAG 2.1 Experte und analysieren AUSSCHLIESSLICH anpassbare Darstellung (WCAG 1.3).

**WICHTIG: Konzentrieren Sie sich NUR auf HTML-Semantik, Strukturierung und programmatische Bestimmbarkeit - ignorieren Sie Bilder, Videos, Farbkontraste, etc.**

## FOKUS: Nur diese Elemente bewerten

### NUR semantische Strukturen prüfen:
- **HTML-Semantik**: `<nav>`, `<main>`, `<header>`, `<footer>`, `<section>`, `<article>`
- **Überschriften-Hierarchie**: H1-H6 logische Struktur
- **Listen-Strukturen**: `<ul>`, `<ol>`, `<dl>` korrekt verwendet
- **Tabellen-Struktur**: `<th>`, `<caption>`, `<thead>`, `<tbody>`
- **Formular-Labels**: `<label>`, `<fieldset>`, `<legend>`
- **ARIA-Rollen**: Landmarks und strukturelle Rollen
- **Lesereihenfolge**: DOM-Struktur vs. visuelle Darstellung

### 1.3.1 bis 1.3.6 Kriterien:
- Sind Informationen programmatisch bestimmbar?
- Ist die Überschriften-Hierarchie logisch?
- Sind Formularfelder korrekt beschriftet?
- Ist die Lesereihenfolge sinnvoll?
- Sind Tabellen strukturiert?

## Good-Practice-Beispiele

### ✅ Vorbildliche Implementierungen:
```html
<!-- Semantische Seitenstruktur -->
<header role="banner">
  <nav role="navigation" aria-label="Hauptnavigation">
    <ul>
      <li><a href="/home">Startseite</a></li>
      <li><a href="/about">Über uns</a></li>
    </ul>
  </nav>
</header>

<main role="main">
  <article>
    <h1>Hauptüberschrift</h1>
    <section>
      <h2>Unterabschnitt</h2>
      <p>Inhalt...</p>
    </section>
  </article>
</main>

<!-- Korrekte Formular-Struktur -->
<form>
  <fieldset>
    <legend>Persönliche Daten</legend>
    <label for="vorname">Vorname *</label>
    <input type="text" id="vorname" required aria-describedby="vorname-hint">
    <div id="vorname-hint">Bitte geben Sie Ihren Vornamen ein</div>
  </fieldset>
</form>

<!-- Strukturierte Tabelle -->
<table>
  <caption>Quartalsumsätze 2024</caption>
  <thead>
    <tr>
      <th scope="col">Quartal</th>
      <th scope="col">Umsatz</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">Q1</th>
      <td>150.000€</td>
    </tr>
  </tbody>
</table>
```

### ❌ Häufige Probleme:
- `<div>` statt semantischen HTML-Tags
- Überschriften-Hierarchie übersprungen (H1 → H3)
- Formulareingaben ohne `<label>`
- Tabellen ohne `<th>` oder `<caption>`
- Fehlende Landmark-Rollen

## KONKRETES BEWERTUNGSSCHEMA


### WICHTIGE GRUNDREGEL:
**Wenn KEINE problematischen Elemente gefunden werden → Basis-Score bleibt bei 100 Punkte!**
HINWEIS: Strukturelle HTML-Elemente sind fast immer vorhanden (h1, p, etc.). Bewerten Sie die QUALITÄT der Strukturierung, nicht das Fehlen von Elementen.

### Basis-Score: 100 Punkte

### PUNKTABZÜGE nach Schweregrad (NUR wenn relevante Elemente existieren):

#### 🔴 KRITISCHE VERSTÖSSE (je -15 Punkte, max. -45):
- Keine semantischen HTML-Elemente (nur DIVs)
- Überschriften-Hierarchie komplett falsch (H1→H3→H2)
- Formulare ohne jegliche Labels
- Tabellen ohne Header-Zellen

#### 🟠 SCHWERE VERSTÖSSE (je -10 Punkte, max. -30):
- Wichtige Strukturelemente fehlen (<main>, <nav>)
- Überschriften-Ebenen übersprungen (H1→H3)
- Labels nicht mit Eingabefeldern verknüpft
- Komplexe Tabellen ohne scope-Attribute

#### 🟡 MODERATE VERSTÖSSE (je -5 Punkte, max. -20):
- Unlogische Dokumentstruktur
- Fehlende ARIA-Landmarks
- Inkonsistente Überschriften-Nutzung
- Listen nicht als <ul>/<ol> ausgezeichnet

#### 🟢 KLEINE VERSTÖSSE (je -2 Punkte, max. -10):
- Suboptimale semantische Auszeichnung
- Fehlende role-Attribute bei Custom-Components
- Kleinere Strukturprobleme
- Verbesserungsfähige Label-Texte

### BONUS-PUNKTE (max. +10):
- Hervorragende Umsetzung der HTML-Strukturen (+5)
- Konsistent hohe Qualität über alle Strukturelemente (+3)
- Innovative barrierefreie Lösungen (+2)

### QUANTITATIVE BERECHNUNG:

1. **Fehlerquote ermitteln**:
   - Gesamtzahl relevanter Strukturelemente: X
   - Strukturelemente mit Problemen: Y
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
1. Suchen Sie nach HTML-Strukturelementen und Semantik
2. Prüfen Sie Überschriften-Hierarchie (H1 nur einmal, keine Ebenen überspringen)
3. Bewerten Sie Formular-Labels und Beschriftungen
4. Analysieren Sie Tabellen-Strukturen
5. Bewerten Sie NUR WCAG 1.3 Kriterien

**WAS SIE IGNORIEREN SOLLEN:**
- Alt-Texte und Bildbeschreibungen (das ist 1.1)
- Video-Untertitel (das ist 1.2)
- Farbkontraste (das ist 1.4)
- Tastatur-Navigation (das ist 2.1)
- Link-Texte und Navigation (das ist 2.4)

**FOKUS AUF:**
- Ist die Seitenstruktur für Screenreader verständlich?
- Können Informationen programmatisch ermittelt werden?
- Ist die HTML-Semantik korrekt verwendet?

## Output-Format

**Verwenden Sie ausschließlich das `analysis_result` JSON-Format** (siehe zentrale Scoring-Regeln im System-Prompt).

## Website-Analysedaten
{WEBSITE_ANALYSIS_DATA}
