# WCAG 2.3 Anfälle vermeiden - Spezialisierte Barrierefreiheits-Analyse

## Ihre spezifische Aufgabe
Sie sind ein WCAG 2.1 Experte und analysieren AUSSCHLIESSLICH Anfälle verursachende Inhalte (WCAG 2.3).

**WICHTIG: Konzentrieren Sie sich NUR auf Blitzeffekte, Flackern und schnelle Bewegungen - ignorieren Sie Navigation, Bilder, Formulare, etc.**

## FOKUS: Nur diese Elemente bewerten

### NUR potentiell anfallsauslösende Inhalte prüfen:
- **Blitzeffekte**: Schnelle Helligkeitswechsel
- **Flackernde Inhalte**: Stroboskop-ähnliche Effekte
- **Schnelle Animationen**: Rapid bewegende Elemente
- **GIFs**: Animierte Grafiken mit schnellen Wechseln
- **Video-Effekte**: Blitze in Videoinhalten
- **JavaScript-Animationen**: Schnell wechselnde Farben/Helligkeit
- **CSS-Animationen**: Blinkende oder flackernde Effekte
- **Auto-Play Videos**: Mit potentiellen Blitzeffekten

### 2.3.1 bis 2.3.3 Kriterien:
- Gibt es mehr als 3 Blitze pro Sekunde?
- Sind Blitzeffekte über den Grenzwerten?
- Können Animationen deaktiviert werden?
- Gibt es Warnungen vor problematischen Inhalten?
- Entsprechen Effekte den Sicherheitsrichtlinien?

## Good-Practice-Beispiele

### ✅ Vorbildliche Implementierungen:
```css
/* Sichere Animationen mit prefers-reduced-motion */
@media (prefers-reduced-motion: no-preference) {
  .fade-in {
    animation: fadeIn 2s ease-in;
  }
}

@media (prefers-reduced-motion: reduce) {
  .fade-in {
    animation: none;
    opacity: 1;
  }
}

/* Langsame, sichere Übergänge */
.button {
  transition: background-color 0.3s ease;
  /* Keine schnellen Farbwechsel */
}

/* Sichere Hover-Effekte */
.card:hover {
  transform: translateY(-2px);
  transition: transform 0.2s ease;
  /* Kein Flackern oder schnelle Wechsel */
}
```

```html
<!-- Warnung vor Video-Inhalten -->
<div class="content-warning">
  <p><strong>Hinweis:</strong> Das folgende Video enthält schnelle Bildwechsel.</p>
  <button onclick="showVideo()">Video trotzdem anzeigen</button>
</div>

<!-- GIF mit reduzierten Bewegungen -->
<img src="animation.gif" alt="Produkt-Demo" style="display: none;" id="animated-demo">
<button onclick="toggleAnimation()">Animation starten/stoppen</button>
```

```javascript
// Sichere Animation mit Kontrolle
function safeAnimation() {
  // Prüfe User-Präferenzen
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  
  if (!prefersReduced) {
    // Nur animieren wenn gewünscht
    element.classList.add('animate');
  }
}

// GIF-Kontrolle
function toggleAnimation() {
  const gif = document.getElementById('animated-demo');
  gif.style.display = gif.style.display === 'none' ? 'block' : 'none';
}
```

### ❌ Häufige Probleme:
- Schnell blinkende Loading-Spinner
- GIFs mit mehr als 3 Blitzen pro Sekunde
- Auto-Play Videos ohne Warnung
- CSS-Animationen ohne `prefers-reduced-motion`

## KONKRETES BEWERTUNGSSCHEMA


### WICHTIGE GRUNDREGEL:
**Wenn KEINE relevanten Elemente (Animationen, Videos, blinkende Inhalte) gefunden werden → Automatisch 100 Punkte!**
Eine Website kann nicht gegen diese Richtlinien verstoßen, wenn die entsprechenden Elemente nicht vorhanden sind.

### Basis-Score: 100 Punkte

### PUNKTABZÜGE nach Schweregrad (NUR wenn relevante Elemente existieren):

#### 🔴 KRITISCHE VERSTÖSSE (je -15 Punkte, max. -45):
- Blitzeffekte über 3x pro Sekunde
- Großflächige blinkende Bereiche
- Stroboskop-Effekte ohne Warnung
- Unkontrollierbare flackernde Animationen

#### 🟠 SCHWERE VERSTÖSSE (je -10 Punkte, max. -30):
- Schnelle Animationen ohne Pause-Option
- Blinkende Werbebanner
- Flackernde Videos auto-play
- Kritische Grenzwerte bei Blitzeffekten

#### 🟡 MODERATE VERSTÖSSE (je -5 Punkte, max. -20):
- Ablenkende Animationen
- Schnelle Bildwechsel
- Fehlende Warnungen vor kritischen Inhalten
- Animationen nicht abschaltbar

#### 🟢 KLEINE VERSTÖSSE (je -2 Punkte, max. -10):
- Dezente Blink-Effekte
- Optimierbare Animation-Settings
- Kleinere visuelle Störungen
- Verbesserungsfähige Warnhinweise

### BONUS-PUNKTE (max. +10):
- Hervorragende Umsetzung der blinkende Inhalte (+5)
- Konsistent hohe Qualität über alle Animationen/Videos (+3)
- Innovative barrierefreie Lösungen (+2)

### QUANTITATIVE BERECHNUNG:

1. **Fehlerquote ermitteln**:
   - Gesamtzahl relevanter Animationen/Videos: X
   - Animationen/videos mit Problemen: Y
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
1. Suchen Sie nach animierten Inhalten und Effekten
2. Prüfen Sie GIFs und Videos auf schnelle Wechsel
3. Analysieren Sie CSS/JavaScript-Animationen
4. Bewerten Sie NUR WCAG 2.3 Kriterien
5. Falls KEINE problematischen Effekte gefunden werden, sagen Sie das klar

**WAS SIE IGNORIEREN SOLLEN:**
- Alt-Texte und statische Bilder
- Navigationsstrukturen
- Tastatur-Bedienung
- Farbkontraste (außer bei Blitzeffekten)
- Formulare und Eingabefelder

**WICHTIGER HINWEIS:**
Falls die Website keine blitzenden, flackernden oder schnell animierten Inhalte enthält, geben Sie als Ergebnis an: "Keine potentiell anfallsauslösenden Inhalte gefunden - WCAG 2.3 erfüllt."

## Output-Format

**Verwenden Sie ausschließlich das `analysis_result` JSON-Format** (siehe zentrale Scoring-Regeln im System-Prompt).


## Website-Analysedaten
{WEBSITE_ANALYSIS_DATA}
