from flask import request, jsonify
from sqlalchemy import func, case
from datetime import datetime, timedelta
from ..models import Donation, Request, db  
from ..controllers.community_controller import _cc_cache

# ----------------------------------------------------------
# 🔹 Unified Helper Function
# ----------------------------------------------------------

class InventoryController:
    @staticmethod
    def get_cc_summary():
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
        """Overall summary for every CC (including 0-activity ones)."""
        summary = InventoryController.get_cc_summary()
        return jsonify(summary)


    # ----------------------------------------------------------
    # 🔹 Client Summary Endpoint
    # ----------------------------------------------------------
    @staticmethod
    def client_cc_summary():
        """Simplified summary for clients: totals + severe shortages."""
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
        """Return all inventory items for a CC, highlighting shortage items."""

        items = (
            db.session.query(
                Request.request_item.label("item_name"),
                func.sum(Request.request_quantity).label("total_requested"),
                func.sum(Request.allocation).label("fulfilled_quantity"),
                func.coalesce(func.sum(
                    case(
                        (Donation.status == "Added", Donation.donation_quantity),
                        else_=0
                    )
                ), 0).label("total_donated")
            )
            .outerjoin(Donation, Donation.donation_item == Request.request_item)
            .filter(Request.location == location)
            .group_by(Request.request_item)
            .all()
        )

        result = []
        for i in items:
            total_req = int(i.total_requested or 0)
            fulfilled = int(i.fulfilled_quantity or 0)
            fulfill_pct = round((fulfilled / total_req) * 100, 1) if total_req > 0 else 1
            result.append({
                "item_name": i.item_name,
                "total_requested": total_req,
                "total_donated": int(i.total_donated or 0),
                "fulfillment_pct": fulfill_pct
            })

        return jsonify(result)