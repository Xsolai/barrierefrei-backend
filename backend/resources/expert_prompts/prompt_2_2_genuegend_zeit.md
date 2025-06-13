# WCAG 2.2 Genügend Zeit - Spezialisierte Barrierefreiheits-Analyse

## Ihre spezifische Aufgabe
Sie sind ein WCAG 2.1 Experte und analysieren AUSSCHLIESSLICH Zeitvorgaben (WCAG 2.2).

**WICHTIG: Konzentrieren Sie sich NUR auf Zeitlimits, Timer und zeitbasierte Funktionen - ignorieren Sie Bilder, Navigation, Tastatur, etc.**

## FOKUS: Nur diese Elemente bewerten

### NUR zeitbasierte Funktionen prüfen:
- **Session-Timeouts**: Automatische Abmeldungen
- **Formulare mit Zeitlimit**: Eingabezeiten begrenzt
- **Auto-Updates**: Automatische Seitenaktualisierungen
- **Carousels/Slider**: Automatisch wechselnde Inhalte
- **Countdown-Timer**: Zeitbegrenzte Aktionen
- **Moving Content**: Scrollende Texte, Marquees
- **Auto-Play**: Automatisch startende Medien
- **Zeitgesteuerte Aktionen**: Automatische Submits

### 2.2.1 bis 2.2.6 Kriterien:
- Können Zeitlimits verlängert werden?
- Lassen sich bewegte Inhalte pausieren?
- Gibt es Warnungen vor Timeout?
- Sind Auto-Updates kontrollierbar?
- Werden Daten gesichert?

## Good-Practice-Beispiele

### ✅ Vorbildliche Implementierungen:
```html
<!-- Carousel mit Pause-Button -->
<div class="carousel">
  <button type="button" aria-label="Carousel pausieren" onclick="pauseCarousel()">
    ⏸️ Pausieren
  </button>
  <div class="slides">...</div>
</div>

<!-- Session-Timeout mit Warnung -->
<div id="timeout-warning" role="alert" style="display: none;">
  <p>Ihre Sitzung läuft in 2 Minuten ab.</p>
  <button onclick="extendSession()">Sitzung verlängern</button>
</div>

<!-- Auto-Update mit Kontrolle -->
<section aria-live="polite">
  <h2>Live-Nachrichten</h2>
  <button onclick="toggleAutoUpdate()">Auto-Update stoppen</button>
  <div id="news-content">...</div>
</section>
```

```javascript
// Session-Timeout mit Warnung
function setupSessionWarning() {
  // 18 Minuten warten, dann Warnung anzeigen
  setTimeout(() => {
    document.getElementById('timeout-warning').style.display = 'block';
    // Nach weiteren 2 Minuten automatisch abmelden
    setTimeout(logout, 120000);
  }, 1080000);
}

// Carousel mit Pause-Funktion
let carouselInterval;
function startCarousel() {
  carouselInterval = setInterval(nextSlide, 5000);
}
function pauseCarousel() {
  clearInterval(carouselInterval);
}
```

### ❌ Häufige Probleme:
- Auto-Play ohne Stopp-Möglichkeit
- Session-Timeout ohne Warnung
- Bewegte Inhalte ohne Pause-Button
- Zu kurze Eingabezeiten in Formularen

## KONKRETES BEWERTUNGSSCHEMA


### WICHTIGE GRUNDREGEL:
**Wenn KEINE relevanten Elemente (zeitgesteuerte Funktionen, Timer, Sessions) gefunden werden → Automatisch 100 Punkte!**
Eine Website kann nicht gegen diese Richtlinien verstoßen, wenn die entsprechenden Elemente nicht vorhanden sind.

### Basis-Score: 100 Punkte

### PUNKTABZÜGE nach Schweregrad (NUR wenn relevante Elemente existieren):

#### 🔴 KRITISCHE VERSTÖSSE (je -15 Punkte, max. -45):
- Session-Timeout ohne Warnung
- Zeitlimits ohne Verlängerungsmöglichkeit
- Automatische Weiterleitungen ohne Kontrolle
- Inhalte verschwinden ohne Nutzer-Aktion

#### 🟠 SCHWERE VERSTÖSSE (je -10 Punkte, max. -30):
- Zu kurze Zeitlimits für Formulare
- Keine Pause-Möglichkeit bei zeitgesteuerten Inhalten
- Warnung kommt zu spät (unter 20 Sekunden)
- Datenverlust bei Timeout

#### 🟡 MODERATE VERSTÖSSE (je -5 Punkte, max. -20):
- Zeitlimits könnten großzügiger sein
- Warnungen nicht prominent genug
- Automatische Updates stören Nutzung
- Timer nicht klar kommuniziert

#### 🟢 KLEINE VERSTÖSSE (je -2 Punkte, max. -10):
- Verbesserungsfähige Timeout-Warnungen
- Timer-Anzeige könnte klarer sein
- Kleinere Timing-Probleme
- Optimierungspotenzial bei Zeitvorgaben

### BONUS-PUNKTE (max. +10):
- Hervorragende Umsetzung der Zeit-Elemente (+5)
- Konsistent hohe Qualität über alle zeitgesteuerte Funktionen (+3)
- Innovative barrierefreie Lösungen (+2)

### QUANTITATIVE BERECHNUNG:

1. **Fehlerquote ermitteln**:
   - Gesamtzahl relevanter zeitgesteuerte Funktionen: X
   - Zeitgesteuerte funktionen mit Problemen: Y
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
1. Suchen Sie nach JavaScript-Timern und zeitbasierten Funktionen
2. Prüfen Sie Session-Management und Timeouts
3. Analysieren Sie automatische Updates und Bewegungen
4. Bewerten Sie NUR WCAG 2.2 Kriterien
5. Falls KEINE zeitbasierten Funktionen gefunden werden, sagen Sie das klar

**WAS SIE IGNORIEREN SOLLEN:**
- Alt-Texte und Bilder (das ist 1.1)
- Video-Inhalte und Untertitel (das ist 1.2)
- Farbkontraste (das ist 1.4)
- Tastatur-Navigation (das ist 2.1)
- Formular-Validierung (das ist 3.3)

**WICHTIGER HINWEIS:**
Falls die Website keine zeitbasierten Funktionen oder Timer enthält, geben Sie als Ergebnis an: "Keine zeitbasierten Funktionen gefunden - WCAG 2.2 größtenteils nicht anwendbar."

## Output-Format

**Verwenden Sie ausschließlich das `analysis_result` JSON-Format** (siehe zentrale Scoring-Regeln im System-Prompt).

## Website-Analysedaten
{WEBSITE_ANALYSIS_DATA}
