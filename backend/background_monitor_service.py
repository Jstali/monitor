#!/usr/bin/env python3
"""
Background Monitoring Service
Runs on the server and monitors active sessions automatically
No client-side agent needed!
"""

import os
import time
import threading
import requests
from datetime import datetime
from models import db, MonitoringSession, Employee
from app import create_app
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackgroundMonitorService:
    def __init__(self):
        self.app = create_app()
        self.running = True
        self.active_monitors = {}  # session_id -> monitor_thread
        
    def check_active_sessions(self):
        """Check for active monitoring sessions"""
        with self.app.app_context():
            active_sessions = MonitoringSession.query.filter_by(is_active=True).all()
            
            for session in active_sessions:
                if session.id not in self.active_monitors:
                    # Start monitoring for this session
                    logger.info(f"Starting monitor for session {session.id}")
                    thread = threading.Thread(
                        target=self.monitor_session,
                        args=(session.id, session.employee_id),
                        daemon=True
                    )
                    thread.start()
                    self.active_monitors[session.id] = thread
            
            # Clean up stopped sessions
            current_session_ids = {s.id for s in active_sessions}
            for session_id in list(self.active_monitors.keys()):
                if session_id not in current_session_ids:
                    logger.info(f"Session {session_id} stopped, cleaning up")
                    del self.active_monitors[session_id]
    
    def monitor_session(self, session_id, employee_id):
        """Monitor a specific session (simulated)"""
        logger.info(f"Monitoring session {session_id} for employee {employee_id}")
        
        while True:
            with self.app.app_context():
                session = MonitoringSession.query.get(session_id)
                if not session or not session.is_active:
                    logger.info(f"Session {session_id} ended")
                    break
                
                # Here you would capture screenshots and log activities
                # For server-side monitoring, you'd need to:
                # 1. Use browser automation (Selenium/Playwright)
                # 2. Or have the employee install a lightweight client
                # 3. Or use browser extension
                
                logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] Monitoring session {session_id}")
                
                # Sleep for screenshot interval
                time.sleep(60)
    
    def start(self):
        """Start the background service"""
        logger.info("Background Monitor Service started")
        
        try:
            while self.running:
                self.check_active_sessions()
                time.sleep(5)  # Check every 5 seconds
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self.running = False

if __name__ == '__main__':
    service = BackgroundMonitorService()
    service.start()
