-- Migration: User-ID zu Analyse-Tabellen hinzufügen
-- Datum: 2025-05-27
-- Beschreibung: Erweitert die Tabellen um user_id Spalten für User-spezifische Analysen

-- 1. Füge user_id Spalte zur analysis_jobs Tabelle hinzu
ALTER TABLE analysis_jobs 
ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;

-- 2. Füge user_id Spalte zur analysis_results Tabelle hinzu  
ALTER TABLE analysis_results 
ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;

-- 3. Füge user_id Spalte zur analysis_reports Tabelle hinzu
ALTER TABLE analysis_reports 
ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;

-- 4. Erstelle Indizes für bessere Performance
CREATE INDEX IF NOT EXISTS idx_analysis_jobs_user_id ON analysis_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_analysis_results_user_id ON analysis_results(user_id);
CREATE INDEX IF NOT EXISTS idx_analysis_reports_user_id ON analysis_reports(user_id);

-- 5. Erstelle Row Level Security (RLS) Policies

-- Enable RLS auf allen Tabellen
ALTER TABLE analysis_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_reports ENABLE ROW LEVEL SECURITY;

-- Policy für analysis_jobs: Users können nur ihre eigenen Jobs sehen
CREATE POLICY "Users can view own jobs" ON analysis_jobs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own jobs" ON analysis_jobs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own jobs" ON analysis_jobs
    FOR UPDATE USING (auth.uid() = user_id);

-- Policy für analysis_results: Users können nur ihre eigenen Ergebnisse sehen
CREATE POLICY "Users can view own results" ON analysis_results
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own results" ON analysis_results
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Policy für analysis_reports: Users können nur ihre eigenen Berichte sehen
CREATE POLICY "Users can view own reports" ON analysis_reports
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own reports" ON analysis_reports
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- 6. Service Role Policies (für Backend-Zugriff)
-- Das Backend verwendet den Service Role Key und kann alle Daten lesen/schreiben

-- Policy für Service Role: Vollzugriff auf alle Tabellen
CREATE POLICY "Service role full access jobs" ON analysis_jobs
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access results" ON analysis_results
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access reports" ON analysis_reports
    FOR ALL USING (auth.role() = 'service_role');

-- 7. Trigger für automatische user_id Zuweisung (optional)
-- Falls user_id nicht explizit gesetzt wird, verwende auth.uid()

CREATE OR REPLACE FUNCTION set_user_id()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.user_id IS NULL THEN
        NEW.user_id = auth.uid();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger für analysis_jobs
CREATE TRIGGER trigger_set_user_id_jobs
    BEFORE INSERT ON analysis_jobs
    FOR EACH ROW
    EXECUTE FUNCTION set_user_id();

-- Trigger für analysis_results
CREATE TRIGGER trigger_set_user_id_results
    BEFORE INSERT ON analysis_results
    FOR EACH ROW
    EXECUTE FUNCTION set_user_id();

-- Trigger für analysis_reports
CREATE TRIGGER trigger_set_user_id_reports
    BEFORE INSERT ON analysis_reports
    FOR EACH ROW
    EXECUTE FUNCTION set_user_id();

-- 8. Beispiel-Abfragen für Testing

-- Alle Jobs eines Users abrufen
-- SELECT * FROM analysis_jobs WHERE user_id = auth.uid() ORDER BY created_at DESC;

-- Alle Ergebnisse eines Jobs abrufen
-- SELECT ar.* FROM analysis_results ar 
-- JOIN analysis_jobs aj ON ar.job_id = aj.id 
-- WHERE aj.user_id = auth.uid() AND aj.id = 'job-id-hier';

-- Statistiken pro User
-- SELECT 
--     user_id,
--     COUNT(*) as total_jobs,
--     COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_jobs,
--     COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_jobs
-- FROM analysis_jobs 
-- GROUP BY user_id; 