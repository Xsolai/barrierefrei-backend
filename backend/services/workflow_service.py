import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from .supabase_service import SupabaseService

logger = logging.getLogger(__name__)

class WorkflowService:
    """Service für Project Workflow Management"""
    
    def __init__(self):
        self.supabase = SupabaseService()
        logger.info("Workflow Service initialisiert")
    
    def create_project_workflow(
        self, 
        job_id: str, 
        customer_id: str, 
        web_development_requested: bool = False,
        certification_requested: bool = False
    ) -> Optional[str]:
        """
        Erstellt einen neuen Project Workflow
        
        Args:
            job_id: Analysis Job ID
            customer_id: Kunde User ID
            web_development_requested: Ob Webentwicklung angefragt wurde
            certification_requested: Ob Zertifizierung angefragt wurde
            
        Returns:
            Workflow ID oder None bei Fehler
        """
        if not self.supabase.client:
            logger.warning("Supabase Client nicht verfügbar")
            return None
            
        try:
            workflow_data = {
                'job_id': job_id,
                'customer_id': customer_id,
                'current_stage': 'analysis',
                'web_development_requested': web_development_requested,
                'certification_requested': certification_requested,
                'web_development_status': 'pending' if web_development_requested else None,
                'certification_status': 'pending' if certification_requested else None,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.supabase.client.table('project_workflow').insert(workflow_data).execute()
            
            if result.data and len(result.data) > 0:
                workflow_id = result.data[0]['id']
                logger.info(f"Workflow erstellt: {workflow_id} für Job {job_id}")
                return workflow_id
            else:
                logger.error(f"Fehler beim Erstellen des Workflows: {result}")
                return None
                
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Workflows: {str(e)}")
            return None
    
    def get_available_projects_for_developer(self) -> List[Dict[str, Any]]:
        """
        Holt verfügbare Projekte für Webentwickler
        
        Returns:
            Liste von verfügbaren Projekten
        """
        if not self.supabase.client:
            return []
            
        try:
            result = self.supabase.client.table('project_workflow')\
                .select('''
                    *,
                    analysis_jobs(url, plan, status, created_at),
                    customer_profile:user_profiles!customer_id(full_name, company)
                ''')\
                .eq('web_development_requested', True)\
                .is_('web_developer_id', None)\
                .eq('web_development_status', 'pending')\
                .order('created_at', desc=False)\
                .execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Fehler beim Laden verfügbarer Entwickler-Projekte: {str(e)}")
            return []
    
    def get_available_projects_for_certifier(self) -> List[Dict[str, Any]]:
        """
        Holt verfügbare Projekte für Zertifizierer
        
        Returns:
            Liste von verfügbaren Projekten
        """
        if not self.supabase.client:
            return []
            
        try:
            result = self.supabase.client.table('project_workflow')\
                .select('''
                    *,
                    analysis_jobs(url, plan, status, created_at),
                    customer_profile:user_profiles!customer_id(full_name, company),
                    web_developer_profile:user_profiles!web_developer_id(full_name, company)
                ''')\
                .eq('certification_requested', True)\
                .is_('certifier_id', None)\
                .eq('certification_status', 'pending')\
                .in_('current_stage', ['certification', 'web_development'])\
                .order('created_at', desc=False)\
                .execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Fehler beim Laden verfügbarer Zertifizierer-Projekte: {str(e)}")
            return []
    
    def assign_developer_to_project(self, workflow_id: str, developer_id: str) -> bool:
        """
        Weist einen Webentwickler einem Projekt zu
        
        Args:
            workflow_id: Workflow ID
            developer_id: Entwickler User ID
            
        Returns:
            True bei Erfolg
        """
        if not self.supabase.client:
            return False
            
        try:
            result = self.supabase.client.table('project_workflow')\
                .update({
                    'web_developer_id': developer_id,
                    'web_development_status': 'assigned',
                    'web_development_started_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                })\
                .eq('id', workflow_id)\
                .execute()
            
            success = result.data and len(result.data) > 0
            if success:
                logger.info(f"Entwickler {developer_id} dem Workflow {workflow_id} zugewiesen")
            else:
                logger.error(f"Fehler beim Zuweisen des Entwicklers: {result}")
            
            return success
            
        except Exception as e:
            logger.error(f"Fehler beim Zuweisen des Entwicklers: {str(e)}")
            return False
    
    def assign_certifier_to_project(self, workflow_id: str, certifier_id: str) -> bool:
        """
        Weist einen Zertifizierer einem Projekt zu
        
        Args:
            workflow_id: Workflow ID
            certifier_id: Zertifizierer User ID
            
        Returns:
            True bei Erfolg
        """
        if not self.supabase.client:
            return False
            
        try:
            result = self.supabase.client.table('project_workflow')\
                .update({
                    'certifier_id': certifier_id,
                    'certification_status': 'assigned',
                    'certification_started_at': datetime.now().isoformat(),
                    'current_stage': 'certification',
                    'updated_at': datetime.now().isoformat()
                })\
                .eq('id', workflow_id)\
                .execute()
            
            success = result.data and len(result.data) > 0
            if success:
                logger.info(f"Zertifizierer {certifier_id} dem Workflow {workflow_id} zugewiesen")
            else:
                logger.error(f"Fehler beim Zuweisen des Zertifizierers: {result}")
            
            return success
            
        except Exception as e:
            logger.error(f"Fehler beim Zuweisen des Zertifizierers: {str(e)}")
            return False
    
    def update_development_status(
        self, 
        workflow_id: str, 
        status: str, 
        notes: Optional[str] = None
    ) -> bool:
        """
        Aktualisiert den Webentwicklungs-Status
        
        Args:
            workflow_id: Workflow ID
            status: Neuer Status (assigned, in_progress, completed, rejected)
            notes: Optionale Notizen
            
        Returns:
            True bei Erfolg
        """
        if not self.supabase.client:
            return False
            
        try:
            update_data = {
                'web_development_status': status,
                'updated_at': datetime.now().isoformat()
            }
            
            if notes:
                update_data['web_development_notes'] = notes
            
            if status == 'completed':
                update_data['web_development_completed_at'] = datetime.now().isoformat()
                update_data['current_stage'] = 'certification'  # Weiterleitung zur Zertifizierung
            
            result = self.supabase.client.table('project_workflow')\
                .update(update_data)\
                .eq('id', workflow_id)\
                .execute()
            
            success = result.data and len(result.data) > 0
            if success:
                logger.info(f"Entwicklungs-Status für Workflow {workflow_id} auf {status} aktualisiert")
            else:
                logger.error(f"Fehler beim Aktualisieren des Entwicklungs-Status: {result}")
            
            return success
            
        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren des Entwicklungs-Status: {str(e)}")
            return False
    
    def update_certification_status(
        self, 
        workflow_id: str, 
        status: str, 
        notes: Optional[str] = None
    ) -> bool:
        """
        Aktualisiert den Zertifizierungs-Status
        
        Args:
            workflow_id: Workflow ID
            status: Neuer Status (assigned, testing, completed, rejected)
            notes: Optionale Notizen
            
        Returns:
            True bei Erfolg
        """
        if not self.supabase.client:
            return False
            
        try:
            update_data = {
                'certification_status': status,
                'updated_at': datetime.now().isoformat()
            }
            
            if notes:
                update_data['certification_notes'] = notes
            
            if status == 'completed':
                update_data['certification_completed_at'] = datetime.now().isoformat()
                update_data['current_stage'] = 'completed'  # Projekt vollständig abgeschlossen
            elif status == 'testing':
                update_data['current_stage'] = 'certification'
            
            result = self.supabase.client.table('project_workflow')\
                .update(update_data)\
                .eq('id', workflow_id)\
                .execute()
            
            success = result.data and len(result.data) > 0
            if success:
                logger.info(f"Zertifizierungs-Status für Workflow {workflow_id} auf {status} aktualisiert")
            else:
                logger.error(f"Fehler beim Aktualisieren des Zertifizierungs-Status: {result}")
            
            return success
            
        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren des Zertifizierungs-Status: {str(e)}")
            return False
    
    def get_projects_for_developer(self, developer_id: str) -> List[Dict[str, Any]]:
        """
        Holt alle Projekte eines Webentwicklers
        
        Args:
            developer_id: Entwickler User ID
            
        Returns:
            Liste von Projekten
        """
        if not self.supabase.client:
            return []
            
        try:
            result = self.supabase.client.table('project_workflow')\
                .select('''
                    *,
                    analysis_jobs(url, plan, status, created_at),
                    customer_profile:user_profiles!customer_id(full_name, company)
                ''')\
                .eq('web_developer_id', developer_id)\
                .order('updated_at', desc=True)\
                .execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Fehler beim Laden der Entwickler-Projekte: {str(e)}")
            return []
    
    def get_projects_for_certifier(self, certifier_id: str) -> List[Dict[str, Any]]:
        """
        Holt alle Projekte eines Zertifizierers
        
        Args:
            certifier_id: Zertifizierer User ID
            
        Returns:
            Liste von Projekten
        """
        if not self.supabase.client:
            return []
            
        try:
            result = self.supabase.client.table('project_workflow')\
                .select('''
                    *,
                    analysis_jobs(url, plan, status, created_at),
                    customer_profile:user_profiles!customer_id(full_name, company),
                    web_developer_profile:user_profiles!web_developer_id(full_name, company)
                ''')\
                .eq('certifier_id', certifier_id)\
                .order('updated_at', desc=True)\
                .execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Fehler beim Laden der Zertifizierer-Projekte: {str(e)}")
            return []
    
    def send_message(
        self, 
        workflow_id: str, 
        sender_id: str, 
        recipient_id: str, 
        message_type: str,
        subject: str,
        message: str,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """
        Sendet eine Nachricht zwischen Projekt-Teilnehmern
        
        Args:
            workflow_id: Workflow ID
            sender_id: Absender User ID
            recipient_id: Empfänger User ID
            message_type: Art der Nachricht (status_update, question, feedback, file_upload)
            subject: Betreff
            message: Nachrichtentext
            attachments: Optionale Datei-URLs
            
        Returns:
            True bei Erfolg
        """
        if not self.supabase.client:
            return False
            
        try:
            message_data = {
                'workflow_id': workflow_id,
                'sender_id': sender_id,
                'recipient_id': recipient_id,
                'message_type': message_type,
                'subject': subject,
                'message': message,
                'attachments': attachments or [],
                'is_read': False,
                'created_at': datetime.now().isoformat()
            }
            
            result = self.supabase.client.table('project_communications')\
                .insert(message_data)\
                .execute()
            
            success = result.data and len(result.data) > 0
            if success:
                logger.info(f"Nachricht gesendet von {sender_id} an {recipient_id} für Workflow {workflow_id}")
            else:
                logger.error(f"Fehler beim Senden der Nachricht: {result}")
            
            return success
            
        except Exception as e:
            logger.error(f"Fehler beim Senden der Nachricht: {str(e)}")
            return False 