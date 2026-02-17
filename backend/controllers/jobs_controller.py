"""Jobs Controller for CareConnect Backend.

This module manages periodic background jobs including cleanup operations,
expiry management, and manual job triggers with status tracking.
"""

import threading
import time
from dataclasses import dataclass, asdict
from typing import Dict

from ..services.jobs_service import (
    run_cleanup_expired_items_once,
    run_expire_matched_requests_once,
    run_cleanup_approved_donations_once,
)

@dataclass
class JobStatus:
    """Data class for tracking job execution status.
    
    Attributes:
        last_ok (str): Timestamp of last successful execution.
        last_error (str): Last error message if any.
        running (bool): Whether job is currently running.
    """
    last_ok: str = ""
    last_error: str = ""
    running: bool = False


class JobsController:
    """Controller for managing background jobs and manual triggers.
    
    Provides manual job execution endpoints and manages periodic
    background schedulers for system maintenance tasks.
    """

    status: Dict[str, JobStatus] = {
        "allocation": JobStatus(),
        "cleanup_expired_items": JobStatus(),
        "expire_matched_requests": JobStatus(),
        "cleanup_approved_donations": JobStatus(),
    }

    _schedulers_started = False  # prevent double-starts

    # ---------- Internal helper ----------
    @staticmethod
    def _safe_run(job_key: str, fn):
        """Run a job safely with status tracking.
        
        Prevents overlapping executions and updates job status.
        
        Args:
            job_key (str): Key identifying the job type.
            fn (callable): Function to execute.
        """
        s = JobsController.status[job_key]
        if s.running:
            return
        s.running = True
        try:
            result = fn()
            s.last_ok = (result or {}).get("at", "")
            s.last_error = ""
        except Exception as e:
            # Capture full error message for /status endpoint
            s.last_error = str(e)
        finally:
            s.running = False

    # ---------- Manual job triggers (requests have app context) ----------
    @staticmethod
    def run_cleanup_now():
        """Manually trigger cleanup of expired items.
        
        Returns:
            dict: Job execution result and status.
        """
        JobsController._safe_run("cleanup_expired_items", run_cleanup_expired_items_once)
        return {"ok": True, "status": asdict(JobsController.status["cleanup_expired_items"])}

    @staticmethod
    def run_expiry_now(days: int = 2):
        """Manually trigger expiry of matched requests.
        
        Args:
            days (int): Days until expiry (default 2).
            
        Returns:
            dict: Job execution result and status.
        """
        JobsController._safe_run(
            "expire_matched_requests",
            lambda: run_expire_matched_requests_once(days_until_expire=days),
        )
        return {"ok": True, "status": asdict(JobsController.status["expire_matched_requests"])}

    @staticmethod
    def get_status():
        """Get current job status for all background jobs.
        
        Returns:
            dict: Status information for all managed jobs.
        """
        return {k: asdict(v) for k, v in JobsController.status.items()}

    # ---------- Background schedulers ----------
    @staticmethod
    def start_schedulers(app):
        """Start periodic background job schedulers.
        
        Called once from app.py to initialize background threads.
        IMPORTANT: push app.app_context() inside each thread before DB work.
        
        Args:
            app (Flask): Flask application instance for context.
        """
        if JobsController._schedulers_started:
            return
        JobsController._schedulers_started = True

        def cleanup_loop():
            while True:
                with app.app_context():
                    JobsController._safe_run("cleanup_expired_items", run_cleanup_expired_items_once)
                time.sleep(24*60*60)  # daily

        def expiry_loop():
            while True:
                with app.app_context():
                    JobsController._safe_run("expire_matched_requests", run_expire_matched_requests_once)
                time.sleep(24*60*60)  # daily
                
        def approved_donation_loop():
            while True:
                with app.app_context():
                    JobsController._safe_run(
                        "cleanup_approved_donations",
                        run_cleanup_approved_donations_once
                    )
                time.sleep(24 * 60 * 60)  # run daily
        
        threading.Thread(target=cleanup_loop, name="jobs-cleanup", daemon=True).start()
        threading.Thread(target=expiry_loop, name="jobs-expiry", daemon=True).start()
        threading.Thread(target=approved_donation_loop, name="jobs-approved-cleanup", daemon=True).start()
