# controllers/jobs_controller.py
# ------------------------------------------------------------
# Controller layer for periodic background jobs.
# Talks to services/jobs_service.py for actual logic.
# ------------------------------------------------------------

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
    last_ok: str = ""
    last_error: str = ""
    running: bool = False


class JobsController:
    """Controller for managing background jobs and manual triggers."""

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
        """Run a job safely, update status (no overlaps)."""
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
        JobsController._safe_run("cleanup_expired_items", run_cleanup_expired_items_once)
        return {"ok": True, "status": asdict(JobsController.status["cleanup_expired_items"])}

    @staticmethod
    def run_expiry_now(days: int = 2):
        JobsController._safe_run(
            "expire_matched_requests",
            lambda: run_expire_matched_requests_once(days_until_expire=days),
        )
        return {"ok": True, "status": asdict(JobsController.status["expire_matched_requests"])}

    @staticmethod
    def get_status():
        """Return current job health/status dictionary."""
        return {k: asdict(v) for k, v in JobsController.status.items()}

    # ---------- Background schedulers ----------
    @staticmethod
    def start_schedulers(app):
        """
        Start periodic jobs (called once from app.py).
        IMPORTANT: push app.app_context() inside each thread before DB work.
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
