"""Request Controller for CareConnect Backend.

This module handles all request-related operations including creation,
update, deletion, and completion workflow for item requests.
"""

from flask import jsonify, request
from ..extensions import db
from ..models import Request, Item, Donation, Reservation, Manager
from ..services.find_user import get_current_user
from datetime import datetime, timezone, timedelta
from ..services.run_allocation import run_allocation
from ..services.metrics import check_and_broadcast_for_cc

class RequestController:
    """Controller for request management operations.
    
    Handles request lifecycle from creation through matching to completion.
    Includes allocation system and manager approval workflow.
    """
    def get_my_request(req_id: int):
        """Return a single request owned by current user.
        
        Args:
            req_id (int): ID of the request to retrieve.
            
        Returns:
            tuple: JSON response with request data and HTTP status code.
        """
        u = get_current_user()
        if not u: return jsonify({"message": "Unauthorized"}), 401

        r = Request.query.get(req_id)
        if not r or r.requester_email != u.email:
            return jsonify({"message": "Not found"}), 404

        return jsonify({
            "id": r.id,
            "request_category": r.request_category,
            "request_item": r.request_item,
            "request_quantity": r.request_quantity,
            "allocation": r.allocation,
            "location": r.location,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }), 200

    def update_pending_request(req_id: int):
        """Update a pending request.
        
        Only allow updates if status is Pending AND no items are allocated
        (allocation == 0 and no reservations). This prevents silent resource loss.
        
        Args:
            req_id (int): ID of request to update.
            
        Returns:
            tuple: JSON response and HTTP status code.
        """
        u = get_current_user()
        if not u: return jsonify({"message": "Unauthorized"}), 401

        r = Request.query.get(req_id)
        if not r or r.requester_email != u.email:
            return jsonify({"message": "Not found"}), 404

        if r.status != "Pending":
            return jsonify({"message": "Only Pending requests can be updated"}), 400

        # Double-check there are no reservations locked to this request
        has_res = Reservation.query.filter_by(request_id=r.id).count() > 0
        if has_res or (r.allocation or 0) > 0:
            return jsonify({"message": "Cannot update: items already allocated to this request"}), 400

        data = request.get_json(force=True, silent=True) or {}
        new_cat = (data.get("request_category") or r.request_category).strip()
        new_item = (data.get("request_item") or r.request_item).strip()
        new_qty  = int(data.get("request_quantity") or r.request_quantity)
        new_loc  = (data.get("location") or r.location).strip()

        if not new_cat:  return jsonify({"message": "request_category is required"}), 400
        
        # Validate category against allowed values
        valid_categories = ["Food", "Drinks", "Furnitures", "Electronics", "Essentials"]
        if new_cat not in valid_categories:
            return jsonify({"message": f"request_category must be one of: {', '.join(valid_categories)}"}), 400
            
        if not new_item: return jsonify({"message": "request_item is required"}), 400
        if len(new_item) > 120: return jsonify({"message": "request_item must be 120 characters or less"}), 400
        if new_qty < 1:  return jsonify({"message": "request_quantity must be >= 1"}), 400
        if not new_loc:  return jsonify({"message": "location is required"}), 400

        try:
            r.request_category = new_cat
            r.request_item = new_item
            r.request_quantity = new_qty
            r.location = new_loc
            db.session.commit()
            return jsonify({"ok": True, "id": r.id}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Failed to update request", "error": str(e)}), 500

    def delete_pending_request(req_id: int):
        """Delete a pending request.
        
        Delete a user's own Pending request.
        If any items are (already) allocated/reserved, release them first.
        
        Args:
            req_id (int): ID of request to delete.
            
        Returns:
            tuple: JSON response and HTTP status code.
        """
        u = get_current_user()
        if not u: return jsonify({"message": "Unauthorized"}), 401

        r = Request.query.get(req_id)
        if not r or r.requester_email != u.email:
            return jsonify({"message": "Not found"}), 404

        if r.status != "Pending":
            return jsonify({"message": "Only Pending requests can be deleted"}), 400

        try:
            # Release any reservations just in case allocator pre-reserved.
            res_list = Reservation.query.filter_by(request_id=r.id).all()
            released = []
            for res in res_list:
                it = Item.query.get(res.item_id)
                if it:
                    it.status = "Available"
                    released.append(it.id)
                db.session.delete(res)

            db.session.delete(r)
            db.session.commit()

            run_allocation()
            
            return jsonify({
                "ok": True,
                "deleted_request_id": req_id,
                "released_item_ids": released
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Failed to delete request", "error": str(e)}), 500
        
    def manager_matched_requests():
        """Get matched requests for manager's community club.
        
        Return all Matched requests for the manager's own community club (cc).
        
        Returns:
            tuple: JSON response with matched requests and HTTP status code.
        """
        u = get_current_user()
        if not u:
            return jsonify({"message": "Unauthorized"}), 401
        if u.role != "M":
            return jsonify({"message": "Forbidden: managers only"}), 403

        mgr = Manager.query.get(u.email)
        if not mgr:
            return jsonify({"message": "Manager profile not found"}), 404

        rows = (
            Request.query
            .filter(Request.status == "Matched", Request.location == mgr.cc)
            .order_by(Request.matched_at.desc().nullslast(), Request.id.desc())
            .all()
        )
        data = [{
            "id": r.id,
            "requester_email": r.requester_email,
            "request_category": r.request_category,
            "request_item": r.request_item,
            "request_quantity": r.request_quantity,
            "allocation": r.allocation,
            "location": r.location,
            "status": r.status,
            "matched_at": r.matched_at.isoformat() if r.matched_at else None,
        } for r in rows]
        return jsonify({"requests": data, "cc": mgr.cc}), 200

    def manager_complete_request(req_id: int):
        """Complete a matched request.
        
        Mark a single Matched request at this manager's CC as Completed.
        (Items were already allocated/unavailable; on completion we keep them consumed.)
        
        Args:
            req_id (int): ID of request to complete.
            
        Returns:
            tuple: JSON response and HTTP status code.
        """
        u = get_current_user()
        if not u:
            return jsonify({"message": "Unauthorized"}), 401
        if u.role != "M":
            return jsonify({"message": "Forbidden: managers only"}), 403

        mgr = Manager.query.get(u.email)
        if not mgr:
            return jsonify({"message": "Manager profile not found"}), 404

        req = Request.query.get(req_id)
        if not req:
            return jsonify({"message": "Request not found"}), 404

        if req.location != mgr.cc:
            return jsonify({"message": "Forbidden: request not in your CC"}), 403

        if req.status != "Matched":
            return jsonify({"message": "Only Matched requests can be completed"}), 400

        try:
            req.status = "Completed"
            db.session.commit()
            return jsonify({
                "message": "Request marked as Completed",
                "id": req.id,
                "status": req.status
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Failed to complete request", "error": str(e)}), 500
    
    # server/controllers/requests_controller.py  (REPLACE create_request)
    def create_request():
        """Create a new request.
        
        Returns:
            tuple: JSON response with request data and HTTP status code.
        """
        u = get_current_user()
        if not u: return jsonify({"message": "Unauthorized"}), 401

        data = request.get_json(force=True, silent=True) or {}
        request_category = (data.get("request_category") or "").strip()
        request_item = (data.get("request_item") or "").strip()
        request_quantity = data.get("request_quantity", 1)
        location = (data.get("location") or "").strip()

        if not request_category: return jsonify({"message": "request_category is required"}), 400
        
        # Validate category against allowed values
        valid_categories = ["Food", "Drinks", "Furnitures", "Electronics", "Essentials"]
        if request_category not in valid_categories:
            return jsonify({"message": f"request_category must be one of: {', '.join(valid_categories)}"}), 400
            
        if not request_item: return jsonify({"message": "request_item is required"}), 400
        
        try:
            request_quantity = int(request_quantity)
            if request_quantity < 1: raise ValueError
        except Exception:
            return jsonify({"message": "request_quantity must be a positive integer"}), 400
        if not location: return jsonify({"message": "location (CC) is required"}), 400

        try:
            req = Request(
                requester_email=u.email,
                request_category=request_category,
                request_item=request_item,
                request_quantity=request_quantity,
                location=location,
                status="Pending",
                allocation=0,
            )
            db.session.add(req)
            db.session.commit()
            
            run_allocation()

            # Check this CC's fulfilment after adding the new request
            check_and_broadcast_for_cc(location)

            return jsonify({
                "id": req.id, "status": req.status, "location": req.location,
                "request_item": req.request_item, "request_quantity": req.request_quantity,
                "allocation": req.allocation
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Failed to create request", "error": str(e)}), 500

    def my_requests():
        """Get all requests for current user.
        
        Returns:
            tuple: JSON response with requests array and HTTP status code.
        """
        u = get_current_user()
        if not u: return jsonify({"message": "Unauthorized"}), 401
        rows = Request.query.filter_by(requester_email=u.email).order_by(Request.id.desc()).all()
        data = [{
            "id": r.id, "request_category": r.request_category, "request_item": r.request_item,
            "request_quantity": r.request_quantity, "allocation": r.allocation,
            "location": r.location, "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        } for r in rows]
        return jsonify({"requests": data}), 200

    # server/controllers/requests_controller.py
    def reject_matched_request():
        """Reject a matched request.
        
        Returns:
            tuple: JSON response and HTTP status code.
        """
        u = get_current_user()
        if not u: return jsonify({"message": "Unauthorized"}), 401

        data = request.get_json(force=True, silent=True) or {}
        item_name = (data.get("i") or "").strip()
        location = (data.get("location") or "").strip()
        req_id = data.get("r")

        if not item_name or not location or not req_id:
            return jsonify({"message": "i, location and r are required"}), 400

        req = Request.query.get(req_id)
        if not req: return jsonify({"message": "Request not found"}), 404
        if req.requester_email != u.email: return jsonify({"message": "Forbidden"}), 403
        if req.status != "Matched": return jsonify({"message": "Only Matched requests can be rejected"}), 400

        try:
            reservations = Reservation.query.filter_by(request_id=req.id).all()
            freed_item_ids = []
            for res in reservations:
                it = Item.query.get(res.item_id)
                if it:
                    it.status = "Available"
                    freed_item_ids.append(it.id)
                db.session.delete(res)

            # Remove the request completely (keeps the system tidy).
            db.session.delete(req)
            db.session.commit()

            run_allocation()

            return jsonify({
                "message": "Request rejected. Items are now Available and will be reallocated by the scheduler.",
                "rejected_request_id": req_id,
                "freed_items": freed_item_ids
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Failed to reject request", "error": str(e)}), 500

