# server/controllers/community_controller.py
from flask import jsonify, request
import time
from sqlalchemy import func
from ..extensions import db
from ..models import Request
from ..services.community_clubs import fetch_cc_markers_from_api

# simple in-memory cache (module-level)
_cc_cache = {"markers": None, "ts": 0}
_CACHE_TTL = 3600
_DATASET_ID = "d_f706de1427279e61fe41e89e24d440fa"

SUCCESS_STATUSES = ("Matched", "Completed")
CONSIDERED_STATUSES = ("Matched", "Completed", "Pending")

class CCController:
    def community_clubs():
        now = time.time()
        if not _cc_cache["markers"] or (now - _cc_cache["ts"] > _CACHE_TTL):
            try:
                _cc_cache["markers"] = fetch_cc_markers_from_api(_DATASET_ID)
                _cc_cache["ts"] = now
            except Exception as e:
                return jsonify({"error": str(e)}), 502

        q = (request.args.get("q") or "").strip().lower()
        markers = _cc_cache["markers"]
        if q:
            tokens = [t for t in q.split() if t]
            markers = [m for m in markers if all(t in m["name"].lower() for t in tokens)]

        # --- Fulfilment rate per CC ---
        # We assume Request.location stores the CC name chosen in the form (your frontend passes cc name).
        names = [m["name"] for m in markers]
        if names:
            # For simplicity (and clarity) do two small counts per CC.
            for m in markers:
                cc_name = m["name"]

                success_count = db.session.query(func.count(Request.id)).filter(
                    Request.location == cc_name,
                    Request.status.in_(SUCCESS_STATUSES),
                ).scalar() or 0

                considered_count = db.session.query(func.count(Request.id)).filter(
                    Request.location == cc_name,
                    Request.status.in_(CONSIDERED_STATUSES),
                ).scalar() or 0

                if considered_count == 0:
                    rate = None  # no relevant requests yet
                else:
                    rate = success_count / float(considered_count)

                m["fulfilmentRate"] = rate  # e.g., 0.67 or None
                m["lowFulfilment"] = (rate is not None) and (rate < 0.5)
                m["counts"] = {
                    "success": int(success_count),
                    "considered": int(considered_count),
                }
        else:
            # no names => no markers => nothing to annotate
            pass

        return jsonify({"markers": markers})
