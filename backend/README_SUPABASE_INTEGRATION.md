# Backend Supabase Integration

## Übersicht

Das Backend ist jetzt vollständig mit Supabase integriert, um Analyse-Jobs und Ergebnisse persistent zu speichern.

## Neue Features

### 1. Asynchrone Analyse mit Supabase-Speicherung

- **Endpoint**: `POST /analyze-complete-async`
- Erstellt einen Job in Supabase
- Speichert Fortschritt und Module-Ergebnisse in Echtzeit
- Unterstützt verschiedene Pläne (basic, pro, enterprise)

### 2. Job-Status-Abfrage

- **Endpoint**: `GET /analyze-status/{job_id}`
- Prüft zuerst In-Memory-Cache, dann Supabase
- Gibt vollständige Ergebnisse zurück, wenn verfügbar

### 3. Ergebnisse abrufen

- **Endpoint**: `GET /analyze-results/{job_id}`
- Holt vollständige Analyseergebnisse aus Supabase
- Inkludiert alle Module-Ergebnisse und den finalen Bericht

### 4. Job-Liste

- **Endpoint**: `GET /jobs?limit=10&offset=0`
- Listet alle Analyse-Jobs mit Pagination
- Sortiert nach Erstellungsdatum (neueste zuerst)

## Datenbank-Schema

### analysis_jobs
- `id`: UUID (Primary Key)
- `url`: Analysierte URL
- `status`: running, completed, failed
- `progress`: 0-100
- `plan`: basic, pro, enterprise
- `created_at`, `updated_at`, `completed_at`
- `error`: Fehlermeldung (falls vorhanden)

### analysis_results
- `id`: UUID (Primary Key)
- `job_id`: Referenz zu analysis_jobs
- `module_name`: WCAG-Bereich (z.B. '1_1_textalternativen')
- `status`: pending, running, completed, failed
- `result`: JSON mit Analyseergebnis
- `token_usage`: Anzahl verwendeter Tokens
- `created_at`, `completed_at`
- `error`: Fehlermeldung (falls vorhanden)

### analysis_reports
- `id`: UUID (Primary Key)
- `job_id`: Referenz zu analysis_jobs
- `technical_analysis`: Technische Analyse-Ergebnisse
- `expert_analyses`: KI-Expertenanalysen
- `executive_summary`: Zusammenfassung für Entscheider
- `recommendations`: Empfehlungen
- `conformance_level`: A, AA, AAA oder "Nicht konform"
- `certification`: Zertifikat-Daten (wird im Frontend generiert)

## Konfiguration

1. Kopiere `env.example` zu `.env`:
```bash
cp env.example .env
```

2. Füge deine Supabase-Credentials ein:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

## API-Beispiele

### Starte eine Analyse
```bash
curl -X POST http://localhost:8003/analyze-complete-async \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "plan": "pro",
    "max_pages": 5
  }'
```

### Prüfe Status
```bash
curl http://localhost:8003/analyze-status/{job_id}
```

### Hole Ergebnisse
```bash
curl http://localhost:8003/analyze-results/{job_id}
```

### Liste alle Jobs
```bash
curl http://localhost:8003/jobs?limit=10&offset=0
```

## Fortschritts-Updates

Die Analyse aktualisiert den Fortschritt in folgenden Schritten:

1. **0-5%**: Initialisierung
2. **5-10%**: Website-Crawling
3. **10-20%**: Automatische Barrierefreiheitschecks
4. **20-85%**: KI-Expertenanalysen (pro Modul)
5. **85-95%**: Zusammenfassung erstellen
6. **95-100%**: Finaler Bericht speichern

## Fehlerbehandlung

- Alle Fehler werden in Supabase gespeichert
- Module können einzeln fehlschlagen ohne die gesamte Analyse zu stoppen
- Detaillierte Fehlermeldungen für Debugging

## Monitoring

- Alle API-Calls werden geloggt
- Token-Verbrauch wird pro Modul gespeichert
- Analyse-Dauer wird erfasst 