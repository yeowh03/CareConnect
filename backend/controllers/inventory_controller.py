"""Inventory Controller for CareConnect Backend.

This module handles inventory management and reporting including
community club summaries, fulfillment rates, and shortage tracking.
"""

from flask import request, jsonify
from sqlalchemy import func, case
from datetime import datetime, timedelta
from ..models import Donation, Request, db  
from ..controllers.community_controller import _cc_cache

class InventoryController:
    """Controller for inventory management and reporting.
    
    Provides summary statistics, fulfillment rates, and shortage
    analysis for community clubs and inventory items.
    """
    @staticmethod
    def get_cc_summary():
        """Generate community club summary statistics.
        
        Returns:
            list: Summary data for all community clubs.
        """
        # Aggregated data
        req_rows = (
            db.session.query(
                Request.location,
                func.sum(Request.request_quantity),
                func.sum(Request.allocation)
            )
            .group_by(Request.location)
            .all()
        )

        don_rows = (
            db.session.query(
                Donation.location,
                func.sum(
                case(
                        (Donation.status == "Added", Donation.donation_quantity),
                        else_=0
                    )
                )
            )
            .group_by(Donation.location)
            .all()
        )

        req_dict = {r[0]: {"total_requests": int(r[1] or 0), "fulfilled": int(r[2] or 0)} for r in req_rows}
        don_dict = {d[0]: int(d[1] or 0) for d in don_rows}

        # All CC names from cache
        cc_names = [m["name"] for m in _cc_cache["markers"]]

        summary = []
        for name in sorted(cc_names):
            req_info = req_dict.get(name, {"total_requests": 0, "fulfilled": 0})
            total_req = req_info["total_requests"]
            fulfilled = req_info["fulfilled"]
            if total_req == 0:
                fulfill_rate = 100
            else:
                fulfill_rate = (fulfilled / total_req * 100)
            total_don = don_dict.get(name, 0)

            summary.append({
                "location": name,
                "total_donations": total_don,
                "total_requests": total_req,
                "fulfilled_requests": fulfilled,
                "fulfillment_rate": round(fulfill_rate, 1)
            })

        return summary

    # ----------------------------------------------------------
    # 🔹 Manager Summary Endpoint
    # ----------------------------------------------------------
    @staticmethod
    def manager_cc_summary():
        """Get comprehensive CC summary for managers.
        
        Overall summary for every CC (including 0-activity ones).
        
        Returns:
            JSON response with detailed CC statistics.
        """
        summary = InventoryController.get_cc_summary()
        return jsonify(summary)


    # ----------------------------------------------------------
    # 🔹 Client Summary Endpoint
    # ----------------------------------------------------------
    @staticmethod
    def client_cc_summary():
        """Get simplified CC summary for clients.
        
        Simplified summary for clients: totals + severe shortages.
        
        Returns:
            JSON response with CC summaries and shortage items.
        """
        summary = InventoryController.get_cc_summary()

        # --- Identify severe shortage items ---
        items = (
            db.session.query(
                Request.location,
                Request.request_item,
                func.sum(Request.request_quantity).label("total_requested"),
                func.sum(Request.allocation).label("fulfilled_quantity")
            )
            .group_by(Request.location, Request.request_item)
            .all()
        )

        severe_items = {}
        for i in items:
            total_req = int(i.total_requested or 0)
            fulfilled = int(i.fulfilled_quantity or 0)
            if total_req > 0 and fulfilled < 0.5 * total_req:
                severe_items.setdefault(i.location, []).append(i.request_item)

        # --- Merge results with shortages ---
        for cc in summary:
            cc["severe_shortage_items"] = severe_items.get(cc["location"], [])

        return jsonify(summary)

    @staticmethod
    def get_cc_inventory(location):
    # 1) Aggregate requests per item for this CC
        req_agg = (
            db.session.query(
                Request.request_item.label("item_name"),
                func.sum(Request.request_quantity).label("total_requested"),
                func.sum(Request.allocation).label("fulfilled_quantity"),
            )
            .filter(Request.location == location)
            .group_by(Request.request_item)
            .subquery()
        )

        # 2) Aggregate donations per item for this CC (only status Added)
        don_agg = (
            db.session.query(
                Donation.donation_item.label("item_name"),
                func.sum(
                    case((Donation.status == "Added", Donation.donation_quantity), else_=0)
                ).label("total_donated"),
            )
            .filter(Donation.location == location)
            .group_by(Donation.donation_item)
            .subquery()
        )

        # 3) Left join donation totals onto request totals by item
        rows = (
            db.session.query(
                req_agg.c.item_name,
                req_agg.c.total_requested,
                req_agg.c.fulfilled_quantity,
                func.coalesce(don_agg.c.total_donated, 0).label("total_donated"),
            )
            .outerjoin(don_agg, don_agg.c.item_name == req_agg.c.item_name)
            .all()
        )

        result = []
        for r in rows:
            total_req = int(r.total_requested or 0)
            fulfilled = int(r.fulfilled_quantity or 0)
            fulfill_pct = round((fulfilled / total_req) * 100, 1) if total_req > 0 else 0.0
            result.append({
                "item_name": r.item_name,
                "total_requested": total_req,
                "total_donated": int(r.total_donated or 0),
                "fulfillment_pct": fulfill_pct,
            })

        return jsonify(result)