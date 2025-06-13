# WCAG 3.3 Eingabeunterstützung - Spezialisierte Barrierefreiheits-Analyse

## Ihre spezifische Aufgabe
Sie sind ein WCAG 2.1 Experte und analysieren AUSSCHLIESSLICH Eingabeunterstützung (WCAG 3.3).

**WICHTIG: Konzentrieren Sie sich NUR auf Formulare, Fehlermeldungen und Eingabehilfen - ignorieren Sie Navigation, Bilder, Videos, etc.**

## FOKUS: Nur diese Elemente bewerten

### NUR Formular-relevante Elemente prüfen:
- **Fehlermeldungen**: Klar, verständlich, hilfreich
- **Pflichtfelder**: Deutlich gekennzeichnet
- **Eingabeformate**: Beispiele und Hinweise
- **Validierung**: Sofortige Rückmeldung
- **Korrekturvorschläge**: Bei Tippfehlern
- **Bestätigungen**: Bei wichtigen Aktionen
- **Hilfe-Texte**: Kontextsensitive Unterstützung
- **Datenverlust-Prävention**: Speichern/Rückgängig

### 3.3.1 bis 3.3.6 Kriterien:
- Sind Fehler klar identifiziert?
- Gibt es hilfreiche Beschriftungen?
- Werden Korrekturvorschläge gemacht?
- Kann man Eingaben überprüfen?
- Gibt es Kontext-Hilfe?

## Good-Practice-Beispiele

### ✅ Vorbildliche Implementierungen:
```html
<!-- Klare Formular-Beschriftung mit Hilfetexten -->
<form>
  <fieldset>
    <legend>Kontaktdaten</legend>
    
    <!-- Pflichtfeld klar markiert -->
    <label for="email">E-Mail-Adresse *</label>
    <input type="email" 
           id="email" 
           required 
           aria-describedby="email-hint email-error"
           aria-invalid="false">
    <div id="email-hint">Wir verwenden Ihre E-Mail nur für wichtige Updates</div>
    <div id="email-error" role="alert" style="display: none;">
      Bitte geben Sie eine gültige E-Mail-Adresse ein (z.B. name@example.com)
    </div>
    
    <!-- Eingabeformat-Hilfe -->
    <label for="phone">Telefonnummer</label>
    <input type="tel" 
           id="phone" 
           aria-describedby="phone-hint"
           placeholder="0123 456789">
    <div id="phone-hint">Format: 0123 456789 (mit Leerzeichen)</div>
    
    <!-- Komplexe Eingabe mit Validierung -->
    <label for="password">Passwort *</label>
    <input type="password" 
           id="password" 
           required 
           minlength="8"
           aria-describedby="password-requirements">
    <div id="password-requirements">
      <p>Passwort muss enthalten:</p>
      <ul>
        <li id="length">✗ Mindestens 8 Zeichen</li>
        <li id="uppercase">✗ Einen Großbuchstaben</li>
        <li id="number">✗ Eine Zahl</li>
      </ul>
    </div>
  </fieldset>
  
  <!-- Wichtige Aktion mit Bestätigung -->
  <button type="submit" onclick="return confirmSubmit()">
    Absenden
  </button>
</form>

<!-- Globale Fehlermeldung -->
<div role="alert" id="form-errors" style="display: none;">
  <h2>Bitte korrigieren Sie folgende Fehler:</h2>
  <ul id="error-list"></ul>
</div>
```

```javascript
// Hilfreiche Eingabeunterstützung
function validateEmail(input) {
  const email = input.value;
  const errorDiv = document.getElementById('email-error');
  
  if (!email) {
    showError(input, 'E-Mail-Adresse ist erforderlich');
  } else if (!email.includes('@')) {
    showError(input, 'E-Mail-Adresse muss ein @ enthalten');
  } else if (!email.includes('.')) {
    showError(input, 'E-Mail-Adresse scheint unvollständig zu sein');
  } else {
    clearError(input);
  }
}

function showError(input, message) {
  input.setAttribute('aria-invalid', 'true');
  const errorDiv = document.getElementById(input.id + '-error');
  errorDiv.textContent = message;
  errorDiv.style.display = 'block';
}

// Datenverlust-Prävention
window.addEventListener('beforeunload', function(e) {
  const formData = new FormData(document.querySelector('form'));
  const hasData = Array.from(formData.values()).some(value => value.trim());
  
  if (hasData) {
    e.preventDefault();
    return 'Sie haben ungespeicherte Änderungen. Wirklich verlassen?';
  }
});

// Bestätigung bei wichtigen Aktionen
function confirmSubmit() {
  return confirm('Möchten Sie das Formular wirklich absenden?');
}
```

### ❌ Häufige Probleme:
- Fehlermeldungen wie "Eingabe ungültig" ohne Erklärung
- Pflichtfelder nur mit rotem Rahmen markiert
- Keine Eingabeformat-Beispiele
- Formulare ohne Bestätigung bei wichtigen Aktionen
- Validierung erst nach Submit

## KONKRETES BEWERTUNGSSCHEMA


### WICHTIGE GRUNDREGEL:
**Wenn KEINE relevanten Elemente (Formulare, Eingabefelder) gefunden werden → Automatisch 100 Punkte!**
Eine Website kann nicht gegen diese Richtlinien verstoßen, wenn die entsprechenden Elemente nicht vorhanden sind.

### Basis-Score: 100 Punkte

### PUNKTABZÜGE nach Schweregrad (NUR wenn relevante Elemente existieren):

#### 🔴 KRITISCHE VERSTÖSSE (je -15 Punkte, max. -45):
- Keine Fehlermeldungen bei falschen Eingaben
- Fehler nur farblich markiert
- Keine Möglichkeit zur Fehlerkorrektur
- Datenverlust bei Validierungsfehlern

#### 🟠 SCHWERE VERSTÖSSE (je -10 Punkte, max. -30):
- Fehlermeldungen unklar oder verwirrend
- Keine Hinweise bei Pflichtfeldern
- Validierung erst nach Submit
- Fehlerposition nicht erkennbar

#### 🟡 MODERATE VERSTÖSSE (je -5 Punkte, max. -20):
- Fehlermeldungen könnten hilfreicher sein
- Eingabeformate nicht klar kommuniziert
- Validierung inkonsistent
- Hilfe-Texte fehlen teilweise

#### 🟢 KLEINE VERSTÖSSE (je -2 Punkte, max. -10):
- Fehlermeldungen optimierbar
- Kleine Validierungsprobleme
- Hilfe-Texte verbesserungsfähig
- Minimale Eingabe-Probleme

### BONUS-PUNKTE (max. +10):
- Hervorragende Umsetzung der Eingabefelder (+5)
- Konsistent hohe Qualität über alle Formular-Elemente (+3)
- Innovative barrierefreie Lösungen (+2)

### QUANTITATIVE BERECHNUNG:

1. **Fehlerquote ermitteln**:
   - Gesamtzahl relevanter Formular-Elemente: X
   - Formular-elemente mit Problemen: Y
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
1. Suchen Sie nach Formularen und Eingabefeldern
2. Prüfen Sie Fehlermeldungen und deren Hilfestellung
3. Analysieren Sie Beschriftungen und Hinweise
4. Bewerten Sie Validierung und Korrekturmöglichkeiten
5. Bewerten Sie NUR WCAG 3.3 Kriterien

**WAS SIE IGNORIEREN SOLLEN:**
- Alt-Texte und Bilder (das ist 1.1)
- Farbkontraste (das ist 1.4)
- Tastatur-Navigation (das ist 2.1)
- Zeitlimits (das ist 2.2)
- Sprachkennzeichnung (das ist 3.1)

**FOKUS AUF:**
- Werden Nutzer bei der Eingabe unterstützt?
- Sind Fehlermeldungen hilfreich?
- Können Fehler leicht korrigiert werden?

## Output-Format

**Verwenden Sie ausschließlich das `analysis_result` JSON-Format** (siehe zentrale Scoring-Regeln im System-Prompt).

## Website-Analysedaten
{WEBSITE_ANALYSIS_DATA}
