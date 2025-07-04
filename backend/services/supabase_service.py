import os
from supabase import create_client, Client
from typing import Dict, Any, Optional
import logging
from datetime import datetime
import json
import uuid
import traceback
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class SupabaseService:
    def __init__(self):
        # Explizit .env laden um sicherzustellen dass Variablen verfügbar sind
        load_dotenv()
        
        # Lade Umgebungsvariablen
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not supabase_url or not supabase_key:
            logger.warning("⚠️ Supabase-Umgebungsvariablen fehlen - arbeite im Offline-Modus")
            self.client = None
            return
        
        # Vereinfachte und robuste Initialisierung
        try:
            # Versuche die einfachste Initialisierung
            self.client: Client = create_client(supabase_url, supabase_key)
            logger.info("✅ Supabase-Service erfolgreich initialisiert")
            
        except Exception as e:
            logger.error(f"❌ Supabase-Initialisierungsfehler: {str(e)}")
            logger.error(f"🔍 Traceback: {traceback.format_exc()}")
            logger.warning("🔄 Wechsle zu Offline-Modus")
            self.client = None

    def create_analysis_job(self, url: str, plan: str, user_id: str = None, payment_session_id: str = None, selected_upgrades: list = None) -> str:
        """
        Erstellt einen neuen Analysis Job in Supabase
        
        Args:
            url: Website URL
            plan: Plan (basic, enterprise)
            user_id: User ID (optional)
            payment_session_id: Stripe Payment Session ID (optional)
            selected_upgrades: Liste der ausgewählten Upgrades (optional)
            
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        
        if not self.client:
            logger.error("❌ Supabase Client nicht verfügbar - kann Job nicht in DB erstellen!")
            logger.warning(f"🆔 Verwende Offline-Job-ID: {job_id}")
            return job_id
            
        try:
            job_data = {
                'id': job_id,
                'url': url,
                'plan': plan,
                'status': 'running',
                'progress': 0,
                'created_at': datetime.now().isoformat(),
                'user_id': user_id,
                'payment_session_id': payment_session_id
            }
            
            # Füge selected_upgrades hinzu, falls vorhanden
            if selected_upgrades:
                # Speichere direkt als Array (nicht als JSON-String) für jsonb-Feld
                job_data['selected_upgrades'] = selected_upgrades
                logger.info(f"📋 Speichere Upgrades für Job {job_id}: {selected_upgrades}")
            
            # Entferne None-Werte
            job_data = {k: v for k, v in job_data.items() if v is not None}
            
            logger.info(f"📝 Versuche Job zu erstellen: {job_data}")
            
            result = self.client.table('analysis_jobs').insert(job_data).execute()
            
            if result.data:
                logger.info(f"✅ Analysis Job erfolgreich in Supabase erstellt: {job_id}")
                logger.info(f"   📊 URL: {url}, User: {user_id}, Payment: {payment_session_id}")
                if selected_upgrades:
                    logger.info(f"   🎯 Upgrades: {selected_upgrades}")
                return job_id
            else:
                logger.error(f"❌ Fehler beim Erstellen des Analysis Jobs - keine Daten zurück: {result}")
                return job_id
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Erstellen des Analysis Jobs in Supabase: {str(e)}")
            logger.error(f"   🔍 Job-Daten waren: {job_data}")
            return job_id

    def update_job_progress(self, job_id: str, progress: int, status: str = 'running'):
        """Aktualisiert den Fortschritt eines Jobs"""
        if not self.client:
            return
            
        try:
            update_data = {
                'progress': progress,
                'status': status,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            if status == 'completed':
                update_data['completed_at'] = datetime.utcnow().isoformat()
                
            self.client.table('analysis_jobs').update(update_data).eq('id', job_id).execute()
            logger.debug(f"Job {job_id} Progress: {progress}%")
            
        except Exception as e:
            logger.error(f"Fehler beim Update des Job-Progress: {e}")

    def save_module_result(self, job_id: str, module_name: str, result: Dict[str, Any], token_usage: int, user_id: Optional[str] = None):
        """Speichert das Ergebnis eines einzelnen Analyse-Moduls"""
        if not self.client:
            logger.error(f"❌ Supabase Client nicht verfügbar - kann Modul-Ergebnis {module_name} nicht speichern!")
            return
            
        try:
            logger.info(f"💾 Versuche Modul-Ergebnis zu speichern: {module_name} für Job {job_id}")
            
            # Prüfe ob Eintrag bereits existiert
            existing_query = self.client.table('analysis_results').select('id').eq('job_id', job_id).eq('module_name', module_name)
            if user_id:
                existing_query = existing_query.eq('user_id', user_id)
            existing = existing_query.execute()
            
            result_data = {
                'job_id': job_id,
                'module_name': module_name,
                'status': 'completed',
                'result': result,
                'token_usage': token_usage,
                'completed_at': datetime.utcnow().isoformat()
            }
            if user_id:
                result_data['user_id'] = user_id
            
            if existing.data:
                # Update existing
                logger.info(f"🔄 Aktualisiere existierenden Eintrag für {module_name}")
                update_query = self.client.table('analysis_results').update(result_data).eq('id', existing.data[0]['id'])
                update_result = update_query.execute()
                logger.info(f"✅ Update-Ergebnis: {update_result.data}")
            else:
                # Insert new
                logger.info(f"➕ Erstelle neuen Eintrag für {module_name}")
                insert_result = self.client.table('analysis_results').insert(result_data).execute()
                logger.info(f"✅ Insert-Ergebnis: {insert_result.data}")
                
            logger.info(f"✅ Modul-Ergebnis erfolgreich gespeichert: {module_name} für Job {job_id}, User: {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Speichern des Modul-Ergebnisses {module_name}: {e}")
            logger.error(f"   🔍 Daten waren: job_id={job_id}, user_id={user_id}, token_usage={token_usage}")

    def save_module_error(self, job_id: str, module_name: str, error: str, user_id: Optional[str] = None):
        """Speichert einen Fehler für ein Analyse-Modul"""
        if not self.client:
            return
            
        try:
            error_data = {
                'job_id': job_id,
                'module_name': module_name,
                'status': 'failed',
                'error': error,
                'completed_at': datetime.utcnow().isoformat()
            }
            if user_id:
                error_data['user_id'] = user_id
            
            # Prüfe ob Eintrag bereits existiert
            existing_query = self.client.table('analysis_results').select('id').eq('job_id', job_id).eq('module_name', module_name)
            if user_id:
                existing_query = existing_query.eq('user_id', user_id)
            existing = existing_query.execute()
            
            if existing.data:
                update_query = self.client.table('analysis_results').update(error_data).eq('id', existing.data[0]['id'])
                update_query.execute()
            else:
                self.client.table('analysis_results').insert(error_data).execute()
                
            logger.error(f"Modul-Fehler gespeichert: {module_name} für Job {job_id}, User: {user_id}")
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern des Modul-Fehlers: {e}")

    def save_final_report(self, job_id: str, report_data: Dict[str, Any]):
        """Speichert den finalen Analyse-Bericht direkt im analysis_jobs result Feld"""
        if not self.client:
            logger.warning("Supabase-Client nicht verfügbar - kann finalen Bericht nicht speichern")
            return
            
        try:
            logger.debug(f"Speichere finalen Bericht für Job {job_id} im result Feld")
            
            # Speichere den Bericht direkt im result Feld des Jobs
            report_summary = {
                'final_report': report_data,
                'conformance_level': report_data.get('conformance_level'),
                'overall_score': report_data.get('overall_score', 0),
                'total_issues': report_data.get('total_issues', 0),
                'critical_issues': report_data.get('critical_issues', 0),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            # Update den Job mit dem Bericht
            self.client.table('analysis_jobs').update({
                'result': report_summary
            }).eq('id', job_id).execute()
            
            logger.debug(f"Finaler Bericht erfolgreich im Job {job_id} gespeichert")
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern des Berichts für Job {job_id}: {str(e)}")
            logger.debug("Details zum Fehler:", exc_info=True)

    def mark_job_failed(self, job_id: str, error_message: str):
        """Markiert einen Job als fehlgeschlagen"""
        if not self.client:
            logger.warning("Supabase-Client nicht verfügbar - kann Job-Status nicht aktualisieren")
            return
            
        try:
            self.client.table('analysis_jobs').update({
                'status': 'failed',
                'error': error_message,
                'completed_at': datetime.now().isoformat()
            }).eq('id', job_id).execute()
            logger.debug(f"Job {job_id} als fehlgeschlagen markiert")
        except Exception as e:
            logger.error(f"Fehler beim Markieren des Jobs als fehlgeschlagen: {e}")

    def mark_job_completed(self, job_id: str):
        """Markiert einen Job als erfolgreich abgeschlossen"""
        if not self.client:
            logger.warning("Supabase-Client nicht verfügbar - kann Job-Status nicht aktualisieren")
            return
            
        try:
            self.client.table('analysis_jobs').update({
                'status': 'completed',
                'progress': 100,
                'completed_at': datetime.now().isoformat()
            }).eq('id', job_id).execute()
            logger.debug(f"Job {job_id} als erfolgreich abgeschlossen markiert")
        except Exception as e:
            logger.error(f"Fehler beim Markieren des Jobs als abgeschlossen: {e}")

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Holt den aktuellen Status eines Jobs"""
        if not self.client:
            return None
            
        try:
            response = self.client.table('analysis_jobs').select('*').eq('id', job_id).execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des Job-Status: {e}")
            return None

    def get_job_results(self, job_id: str) -> Dict[str, Any]:
        """Holt alle Ergebnisse eines Jobs"""
        if not self.client:
            return {}
            
        try:
            # Hole Job-Details mit result Feld (enthält den finalen Bericht)
            job = self.get_job_status(job_id)
            
            # Hole alle Modul-Ergebnisse
            results_response = self.client.table('analysis_results').select('*').eq('job_id', job_id).execute()
            
            # Extrahiere finalen Bericht aus dem job result Feld
            final_report = None
            if job and job.get('result'):
                final_report = job['result'].get('final_report') if isinstance(job['result'], dict) else None
            
            return {
                'job': job,
                'modules': results_response.data if results_response.data else [],
                'report': final_report  # Finaler Bericht aus job.result statt separater Tabelle
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Job-Ergebnisse: {e}")
            return {}

    def get_user_jobs(self, user_id: str, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """Holt alle Jobs eines Users"""
        if not self.client:
            return {'jobs': [], 'total': 0}
            
        try:
            # Hole Jobs des Users
            response = self.client.table('analysis_jobs').select('*').eq('user_id', user_id).order('created_at', desc=True).range(offset, offset + limit - 1).execute()
            
            # Hole Gesamtanzahl
            count_response = self.client.table('analysis_jobs').select('id', count='exact').eq('user_id', user_id).execute()
            
            return {
                'jobs': response.data if response.data else [],
                'total': count_response.count if count_response.count else 0,
                'limit': limit,
                'offset': offset
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der User-Jobs: {e}")
            return {'jobs': [], 'total': 0} 