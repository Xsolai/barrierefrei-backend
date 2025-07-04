#!/usr/bin/env python3
"""
Manuelles Erstellen eines Certificate Tasks für bezahlte Session
"""
import os
import sys
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.supabase_service import SupabaseService

def create_certificate_task():
    """Erstellt manuell einen Certificate Task für die bezahlte Session"""
    
    # Session-Details
    job_id = "7a1779ae-98b6-4d37-8793-b275201ae86e"
    user_id = "268d857c-379c-4112-8b5c-a8acc0dfa444"
    session_id = "cs_live_b1o9TlmwYSPEdNwi2d1D2LwnXDXh1yIHnrPObVfyiJbf0itnSM0UI78fxT"
    
    print(f"🏆 Erstelle Certificate Task für Job: {job_id}")
    print(f"👤 User: {user_id}")
    print(f"💳 Session: {session_id}")
    
    # Supabase-Verbindung
    supabase = SupabaseService()
    if not supabase.client:
        print("❌ Supabase-Verbindung fehlgeschlagen")
        return False
    
    try:
        # Prüfe ob Job existiert
        job_result = supabase.client.table('analysis_jobs')\
            .select('*')\
            .eq('id', job_id)\
            .eq('user_id', user_id)\
            .execute()
        
        if not job_result.data:
            print(f"❌ Job {job_id} nicht gefunden oder gehört nicht User {user_id}")
            return False
        
        job = job_result.data[0]
        print(f"✅ Job gefunden: {job['url']} - Status: {job['status']}")
        
        # Prüfe ob bereits Certificate Task existiert
        existing_task_result = supabase.client.table('upgrade_tasks')\
            .select('id')\
            .eq('job_id', job_id)\
            .eq('upgrade_type', 'certificate')\
            .execute()
        
        if existing_task_result.data:
            print(f"⚠️ Certificate Task existiert bereits: {existing_task_result.data[0]['id']}")
            return True
        
        # Erstelle Certificate Task
        task_data = {
            'job_id': job_id,
            'upgrade_type': 'certificate',
            'status': 'requested',
            'assigned_to': 'certifier',
            'customer_notified': False,
            'trigger_source': 'manual',
            'triggered_by_user_id': user_id,
            'payment_session_id': session_id,
            'created_at': datetime.now().isoformat()
        }
        
        task_result = supabase.client.table('upgrade_tasks')\
            .insert(task_data)\
            .execute()
        
        if task_result.data and len(task_result.data) > 0:
            task_id = task_result.data[0]['id']
            print(f"✅ Certificate Task erfolgreich erstellt: {task_id}")
            print(f"🎯 Task-Details:")
            print(f"   📋 Task-ID: {task_id}")
            print(f"   🔗 Job-ID: {job_id}")
            print(f"   👤 User: {user_id}")
            print(f"   💳 Session: {session_id}")
            print(f"   🌐 Website: {job['url']}")
            print(f"   📍 Status: requested")
            print(f"   👨‍💼 Assigned to: certifier")
            return True
        else:
            print(f"❌ Fehler beim Erstellen des Certificate Tasks: {task_result}")
            return False
            
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

if __name__ == "__main__":
    success = create_certificate_task()
    if success:
        print("\n🎉 Certificate Task erfolgreich erstellt!")
        print("🏆 Der Task erscheint jetzt im Certifier Dashboard")
    else:
        print("\n❌ Certificate Task konnte nicht erstellt werden")
    
    sys.exit(0 if success else 1) 