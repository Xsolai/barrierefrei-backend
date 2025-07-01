-- ============================================================================
-- Cleanup Script: Automatisch erstellte upgrade_tasks bereinigen
-- ============================================================================
-- Problem: Enterprise-Jobs haben automatisch upgrade_tasks für Zertifizierung erstellt,
-- obwohl der Kunde diese nicht explizit ausgelöst hat.
-- 
-- Diese Tasks sollen nur existieren, wenn:
-- 1. Kunde hat explizit "Zertifizierung starten" geklickt (trigger_source='manual')
-- 2. Professional Fix ist abgeschlossen (trigger_source='after_professional_fix')
-- ============================================================================

-- 1. PRÜFUNG: Zeige alle automatisch erstellten certificate Tasks
SELECT 
  ut.id as task_id,
  ut.job_id,
  ut.upgrade_type,
  ut.status,
  ut.trigger_source,
  ut.created_at as task_created,
  aj.url,
  aj.plan,
  aj.selected_upgrades,
  aj.created_at as job_created,
  up.email as customer_email
FROM upgrade_tasks ut
JOIN analysis_jobs aj ON ut.job_id = aj.id
LEFT JOIN user_profiles up ON aj.user_id = up.id
WHERE ut.upgrade_type = 'certificate'
  AND ut.assigned_to = 'certifier'
  AND (ut.trigger_source IS NULL OR ut.trigger_source = 'automatic')
  AND aj.plan = 'enterprise'
ORDER BY ut.created_at DESC;

-- 2. ZÄHLUNG: Wie viele Tasks sind betroffen?
SELECT 
  COUNT(*) as automatische_certificate_tasks,
  COUNT(DISTINCT ut.job_id) as betroffene_jobs
FROM upgrade_tasks ut
JOIN analysis_jobs aj ON ut.job_id = aj.id
WHERE ut.upgrade_type = 'certificate'
  AND ut.assigned_to = 'certifier'
  AND (ut.trigger_source IS NULL OR ut.trigger_source = 'automatic')
  AND aj.plan = 'enterprise';

-- 3. BEREINIGUNG (STEP 1): Markiere Tasks als 'automatic' falls trigger_source NULL ist
UPDATE upgrade_tasks 
SET trigger_source = 'automatic'
WHERE upgrade_type = 'certificate'
  AND trigger_source IS NULL;

-- 4. BEREINIGUNG (STEP 2): Lösche automatische Tasks die noch nicht bearbeitet wurden
-- VORSICHT: Diese Abfrage erst ausführen, wenn Step 1-3 geprüft wurden!

-- DELETE FROM upgrade_tasks 
-- WHERE upgrade_type = 'certificate'
--   AND assigned_to = 'certifier'
--   AND trigger_source = 'automatic'
--   AND status IN ('requested', 'pending');

-- 5. ALTERNATIVE: Setze Status auf 'cancelled' statt löschen (sicherer)
UPDATE upgrade_tasks 
SET 
  status = 'cancelled',
  notes = 'Automatisch erstellt - vom System storniert da nicht explizit vom Kunden ausgelöst'
WHERE upgrade_type = 'certificate'
  AND assigned_to = 'certifier'
  AND trigger_source = 'automatic'
  AND status IN ('requested', 'pending');

-- 6. VERIFIKATION: Prüfe das Ergebnis
SELECT 
  trigger_source,
  status,
  COUNT(*) as anzahl
FROM upgrade_tasks 
WHERE upgrade_type = 'certificate'
  AND assigned_to = 'certifier'
GROUP BY trigger_source, status
ORDER BY trigger_source, status;

-- 7. INFORMATION: Zeige verbleibende aktive certificate Tasks
SELECT 
  ut.id,
  ut.job_id,
  ut.status,
  ut.trigger_source,
  aj.url,
  up.email
FROM upgrade_tasks ut
JOIN analysis_jobs aj ON ut.job_id = aj.id
LEFT JOIN user_profiles up ON aj.user_id = up.id
WHERE ut.upgrade_type = 'certificate'
  AND ut.assigned_to = 'certifier'
  AND ut.status NOT IN ('cancelled', 'completed')
ORDER BY ut.created_at DESC; 