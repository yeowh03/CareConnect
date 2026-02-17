"""Community Club Controller for CareConnect Backend.

This module handles community club data retrieval and caching,
including fulfilment rate calculations for each community club.
"""

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

class CCController:
    """Controller for community club operations.
    
    Handles fetching community club data with caching and
    calculates fulfilment rates based on request allocations.
    """
    def community_clubs():
        """Get community clubs with fulfilment rates.
        
        Returns cached community club data with calculated fulfilment rates
        based on request allocation statistics. Supports search filtering.
        
        Returns:
            tuple: JSON response with markers array and HTTP status code.
        """
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

        # Calculate fulfillment rates for each community club
        # Request.location stores the CC name selected by users
        names = [m["name"] for m in markers]
        if names:
            for m in markers:
                cc_name = m["name"]

                # Aggregate request quantities and allocations for this CC
                req_row = db.session.query(
                        func.sum(Request.request_quantity),
                        func.sum(Request.allocation)
                ).filter(Request.location == cc_name).first()

                r_qty = req_row[0] if req_row[0] else 0    # Total requested
                r_alloc = req_row[1] if req_row[1] else 0  # Total allocated

                # Calculate fulfillment rate (100% if no requests)
                if r_qty == 0:
                    rate = 1.0  # 100% fulfillment when no requests
                else:
                    rate = round(r_alloc / r_qty, 2)
                
                # Add fulfillment metrics to marker data
                m["fulfilmentRate"] = rate  # e.g., 0.67 (67%)
                m["lowFulfilment"] = (rate is not None) and (rate < 0.5) and req_row[0]
        else:
            # No markers found, skip fulfillment calculation
            pass

        return jsonify({"markers": markers})
