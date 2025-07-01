# BarrierefreiCheck Backend

Dieses Backend verarbeitet die Barrierefreiheits-Analysen für die BarrierefreiCheck-Webanwendung.

## Installation

1. Python 3.8 oder höher installieren
2. Virtuelle Umgebung erstellen und aktivieren:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Unter Windows: venv\Scripts\activate
   ```
3. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```
4. Playwright Browser installieren:
   ```bash
   playwright install
   ```

## Entwicklung

1. Server starten:
   ```bash
   python main.py
   ```
   Der Server läuft dann unter http://localhost:8000

2. API-Dokumentation:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Umgebungsvariablen

Erstellen Sie eine `.env`-Datei im Backend-Verzeichnis mit folgenden Variablen:
```
OPENAI_API_KEY=ihr_api_key
```

## Projektstruktur

```
backend/
├── main.py              # Hauptanwendung
├── requirements.txt     # Python-Abhängigkeiten
├── analyzers/          # Analyse-Module
├── utils/             # Hilfsfunktionen
└── tests/             # Testfälle
``` 