# WCAG 3.2 Vorhersehbarkeit - Spezialisierte Barrierefreiheits-Analyse

## Ihre spezifische Aufgabe
Sie sind ein WCAG 2.1 Experte und analysieren AUSSCHLIESSLICH Vorhersehbarkeit (WCAG 3.2).

**WICHTIG: Konzentrieren Sie sich NUR auf konsistente Bedienung und erwartbares Verhalten - ignorieren Sie Bilder, Videos, Farbkontraste, etc.**

## FOKUS: Nur diese Elemente bewerten

### NUR Vorhersehbarkeits-Aspekte prüfen:
- **Fokus-Verhalten**: Keine unerwarteten Kontextwechsel
- **Eingabe-Verhalten**: Keine automatischen Submits
- **Navigation**: Konsistente Menüstruktur
- **Bezeichnungen**: Einheitliche Benennung
- **Funktionen**: Vorhersehbares Verhalten
- **Pop-ups**: Keine unerwarteten Dialoge
- **Weiterleitungen**: Angekündigte Redirects
- **Statusänderungen**: Klare Kommunikation

### 3.2.1 bis 3.2.5 Kriterien:
- Gibt es unerwartete Fokus-Änderungen?
- Werden Formulare automatisch abgeschickt?
- Ist die Navigation konsistent?
- Sind Bezeichnungen einheitlich?
- Werden Änderungen angekündigt?

## Good-Practice-Beispiele

### ✅ Vorbildliche Implementierungen:
```html
<!-- Konsistente Navigation auf allen Seiten -->
<nav role="navigation" aria-label="Hauptnavigation">
  <ul>
    <li><a href="/home">Startseite</a></li>
    <li><a href="/services">Dienstleistungen</a></li>
    <li><a href="/about">Über uns</a></li>
    <li><a href="/contact">Kontakt</a></li>
  </ul>
</nav>

<!-- Vorhersehbare Formulare ohne Auto-Submit -->
<form action="/search" method="get">
  <label for="search">Suchbegriff</label>
  <input type="text" id="search" name="q">
  <button type="submit">Suchen</button>
  <!-- Kein onchange="submit()" -->
</form>

<!-- Angekündigte Weiterleitungen -->
<p>Sie werden in 5 Sekunden zur neuen Seite weitergeleitet.</p>
<p><a href="/new-page">Sofort weiterleiten</a></p>

<!-- Konsistente Button-Beschriftungen -->
<button type="submit">Absenden</button> <!-- Überall gleich -->
<button type="button">Abbrechen</button> <!-- Überall gleich -->
<button type="button">Bearbeiten</button> <!-- Überall gleich -->

<!-- Fokus-freundliche Interaktionen -->
<button onclick="showDetails()" aria-expanded="false">
  Details anzeigen
</button>
<!-- Fokus bleibt auf Button, keine unerwarteten Sprünge -->
```

```javascript
// Vorhersehbares Verhalten
function showDialog() {
  // Kein unerwarteter Fokus-Wechsel
  const dialog = document.getElementById('dialog');
  dialog.style.display = 'block';
  
  // Benutzer wird informiert
  document.getElementById('status').textContent = 'Dialog geöffnet';
}

// Konsistente Funktionalität
class ConsistentComponents {
  // Alle "Schließen"-Buttons verhalten sich gleich
  closeButton(element) {
    element.style.display = 'none';
    // Immer zurück zum auslösenden Element
    this.returnFocus();
  }
  
  // Vorhersehbare Navigation
  navigate(url) {
    // Warnung bei externen Links
    if (url.includes('://') && !url.includes(window.location.hostname)) {
      if (confirm('Sie verlassen unsere Website. Fortfahren?')) {
        window.open(url, '_blank');
      }
    } else {
      window.location.href = url;
    }
  }
}
```

### ❌ Häufige Probleme:
- Dropdown-Menüs die bei onFocus automatisch öffnen
- Formulare die bei Eingabe automatisch submitten
- Inkonsistente Navigationspositionen zwischen Seiten
- "Speichern" vs "Senden" vs "Absenden" durcheinander
- Pop-ups ohne Vorwarnung

## KONKRETES BEWERTUNGSSCHEMA


### WICHTIGE GRUNDREGEL:
**Wenn KEINE relevanten Elemente (interaktive UI-Elemente) gefunden werden → Automatisch 100 Punkte!**
Eine Website kann nicht gegen diese Richtlinien verstoßen, wenn die entsprechenden Elemente nicht vorhanden sind.

### Basis-Score: 100 Punkte

### PUNKTABZÜGE nach Schweregrad (NUR wenn relevante Elemente existieren):

#### 🔴 KRITISCHE VERSTÖSSE (je -15 Punkte, max. -45):
- Kontext ändert sich unerwartet bei Fokus
- Automatische Weiterleitungen beim Tippen
- Navigation völlig inkonsistent
- Formulare werden ohne Warnung abgeschickt

#### 🟠 SCHWERE VERSTÖSSE (je -10 Punkte, max. -30):
- Wichtige UI-Elemente verhalten sich inkonsistent
- Unerwartete Popups bei Interaktion
- Navigation ändert sich zwischen Seiten
- Verwirrende Interaktionsmuster

#### 🟡 MODERATE VERSTÖSSE (je -5 Punkte, max. -20):
- Leichte Inkonsistenzen in der Navigation
- Einige unerwartete Verhaltensweisen
- UI-Patterns nicht durchgängig
- Feedback könnte klarer sein

#### 🟢 KLEINE VERSTÖSSE (je -2 Punkte, max. -10):
- Minimale Inkonsistenzen
- Kleine Überraschungen bei Interaktion
- Verbesserungsfähiges Feedback
- Leichte Vorhersehbarkeits-Probleme

### BONUS-PUNKTE (max. +10):
- Hervorragende Umsetzung der UI-Verhalten (+5)
- Konsistent hohe Qualität über alle Interaktions-Elemente (+3)
- Innovative barrierefreie Lösungen (+2)

### QUANTITATIVE BERECHNUNG:

1. **Fehlerquote ermitteln**:
   - Gesamtzahl relevanter Interaktions-Elemente: X
   - Interaktions-elemente mit Problemen: Y
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
1. Prüfen Sie Fokus- und Eingabeverhalten
2. Analysieren Sie Navigationskonsistenz
3. Bewerten Sie Bezeichnungen und Funktionen
4. Suchen Sie nach unerwarteten Änderungen
5. Bewerten Sie NUR WCAG 3.2 Kriterien

**WAS SIE IGNORIEREN SOLLEN:**
- Alt-Texte und Bilder (das ist 1.1)
- Farbkontraste (das ist 1.4)
- Tastatur-Navigation (das ist 2.1)
- Zeitlimits (das ist 2.2)
- Formular-Validierung (das ist 3.3)

**FOKUS AUF:**
- Ist das Verhalten vorhersehbar?
- Sind Änderungen erwartbar?
- Bleibt die Navigation konsistent?

## Output-Format

**Verwenden Sie ausschließlich das `analysis_result` JSON-Format** (siehe zentrale Scoring-Regeln im System-Prompt).

## Website-Analysedaten
{WEBSITE_ANALYSIS_DATA}
