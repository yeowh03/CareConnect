"""Donation Controller for CareConnect Backend.

This module handles all donation-related operations including creation,
approval workflow, and inventory management for donated items.
"""

from flask import jsonify, request
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from ..extensions import db
from ..models import Donation, Item, Request, Reservation
from ..services.find_user import get_current_user, find_manager_by_email
from ..services.image_upload import upload_image_to_supabase
from datetime import datetime, timezone
from ..services.run_allocation import run_allocation
from ..services.notification_strategies import DatabaseNotificationStrategy
from ..services.find_user import find_managers_by_cc

class DonationController:
    """Controller for donation management operations.
    
    Handles donation lifecycle from creation through approval to inventory addition.
    Includes notification system for donors and managers.
    """
    def __init__(self):
        self.notification_strategy = DatabaseNotificationStrategy()
    def get_my_donation(donation_id: int):
        """Get donation details for current user.
        
        Args:
            donation_id (int): ID of the donation to retrieve.
            
        Returns:
            tuple: JSON response with donation data and HTTP status code.
        """
        u = get_current_user()
        if not u: return jsonify({"message": "Unauthorized"}), 401

        d = Donation.query.get(donation_id)
        if not d or d.donor_email != u.email:
            return jsonify({"message": "Not found"}), 404

        return jsonify({
            "id": d.id,
            "donation_category": d.donation_category,
            "donation_item": d.donation_item,
            "donation_quantity": d.donation_quantity,
            "location": d.location,
            "status": d.status,
            "image_link": d.image_link,
            "expiryDate": d.expiryDate.isoformat() if d.expiryDate else None,
        }), 200

    def update_pending_donation(donation_id: int, supabase, bucket):
        """Update a pending donation.
        
        Only allow updates when donation is Pending.
        Optional image replacement; Food/Drinks still require an expiry date.
        
        Args:
            donation_id (int): ID of donation to update.
            supabase: Supabase client for image upload.
            bucket: Storage bucket name.
            
        Returns:
            tuple: JSON response and HTTP status code.
        """
        u = get_current_user()
        if not u: return jsonify({"message": "Unauthorized"}), 401

        d = Donation.query.get(donation_id)
        if not d or d.donor_email != u.email:
            return jsonify({"message": "Not found"}), 404

        if d.status != "Pending":
            return jsonify({"message": "Only Pending donations can be updated"}), 400

        donation_category = (request.form.get("donation_category") or d.donation_category).strip()
        donation_item     = (request.form.get("donation_item") or d.donation_item).strip()
        donation_quantity = int(request.form.get("donation_quantity") or d.donation_quantity)
        location          = (request.form.get("location") or d.location).strip()
        expiry_str        = (request.form.get("expiryDate") or (d.expiryDate.isoformat() if d.expiryDate else "")).strip()
        image_file        = request.files.get("image")

        if donation_quantity < 1: return jsonify({"message": "donation_quantity must be >= 1"}), 400
        if not donation_category: return jsonify({"message": "donation_category is required"}), 400
        if not donation_item: return jsonify({"message": "donation_item is required"}), 400
        if not location: return jsonify({"message": "location is required"}), 400

        expiry_date = None
        if donation_category in ("Food", "Drinks"):
            if not expiry_str:
                return jsonify({"message": "expiryDate is required for Food and Drinks"}), 400
            from datetime import datetime as _dt
            try:
                expiry_date = _dt.strptime(expiry_str, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"message": "expiryDate must be YYYY-MM-DD"}), 400

        try:
            d.donation_category = donation_category
            d.donation_item = donation_item
            d.donation_quantity = donation_quantity
            d.location = location
            d.expiryDate = expiry_date

            # optional new image
            if image_file:
                new_url = upload_image_to_supabase(image_file, supabase, bucket)
                d.image_link = new_url

            db.session.commit()
            return jsonify({"ok": True, "id": d.id}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Failed to update donation", "error": str(e)}), 500

    def delete_pending_or_approved(donation_id: int):
        """Delete a pending or approved donation.
        
        Donor may delete if status is Pending or Approved (i.e., not yet 'Added' into items).
        
        Args:
            donation_id (int): ID of donation to delete.
            
        Returns:
            tuple: JSON response and HTTP status code.
        """
        u = get_current_user()
        if not u: return jsonify({"message": "Unauthorized"}), 401

        d = Donation.query.get(donation_id)
        if not d or d.donor_email != u.email:
            return jsonify({"message": "Not found"}), 404

        if d.status not in ("Pending", "Approved"):
            return jsonify({"message": "Only Pending or Approved donations can be deleted"}), 400

        try:
            db.session.delete(d)
            db.session.commit()
            return jsonify({"ok": True, "deleted_donation_id": donation_id}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Failed to delete donation", "error": str(e)}), 500
        
    def create_donation(supabase, bucket):
        """Create a new donation.
        
        Args:
            supabase: Supabase client for image upload.
            bucket: Storage bucket name.
            
        Returns:
            tuple: JSON response with donation data and HTTP status code.
        """
        u = get_current_user()
        if not u:
            return jsonify({"message": "Unauthorized"}), 401

        donation_category = request.form.get("donation_category", "").strip()
        donation_item     = request.form.get("donation_item", "").strip()
        donation_quantity = request.form.get("donation_quantity", "1").strip()
        location          = request.form.get("location", "").strip()
        image_file        = request.files.get("image")
        expiry_str        = request.form.get("expiryDate", "").strip()

        if not donation_category: return jsonify({"message": "donation_category is required"}), 400
        if not donation_item: return jsonify({"message": "donation_item is required"}), 400
        try:
            donation_quantity = int(donation_quantity)
            if donation_quantity < 1: raise ValueError
        except Exception:
            return jsonify({"message": "donation_quantity must be a positive integer"}), 400
        if not location: return jsonify({"message": "location is required"}), 400
        if not image_file: return jsonify({"message": "image is required"}), 400

        expiry_date = None
        if donation_category in ("Food", "Drinks"):
            if not expiry_str:
                return jsonify({"message": "expiryDate is required for Food and Drinks"}), 400
            from datetime import datetime
            try:
                expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"message": "expiryDate must be in YYYY-MM-DD format"}), 400

        try:
            public_url = upload_image_to_supabase(image_file, supabase, bucket)
        except FileNotFoundError:
            return jsonify({"message": "Image file not found or corrupted"}), 400
        except PermissionError:
            return jsonify({"message": "Permission denied accessing image file"}), 403
        except ConnectionError:
            return jsonify({"message": "Failed to connect to image storage service"}), 503
        except Exception as e:
            return jsonify({"message": f"Image upload failed: {e}"}), 400

        d = Donation(
            donor_email=u.email, donation_category=donation_category, donation_item=donation_item,
            donation_quantity=donation_quantity, location=location, status="Pending",
            image_link=public_url, expiryDate=expiry_date
        )
        db.session.add(d); db.session.commit()

        # notify manager
        try:
            manager = find_managers_by_cc(location) or {}
            if manager:
                msg = (
                    f"New pending donation at {location}: '{donation_item}' x{donation_quantity} "
                    f"submitted by {u.name} ({u.email}). Please review and approve/reject."
                )
                notification_strategy = DatabaseNotificationStrategy()
                notification_strategy.create_notification(message=msg, receiver_email=manager.email)

        except Exception as e:
            # Soft-fail the notifications (donation was already created successfully)
            print("Manager notification failed:", e)

        return jsonify({
            "id": d.id, "image_link": d.image_link, "status": d.status,
            "expiryDate": d.expiryDate.isoformat() if d.expiryDate else None,
        }), 201

    def my_donations():
        """Get all donations for current user.
        
        Returns:
            tuple: JSON response with donations array and HTTP status code.
        """
        u = get_current_user()
        if not u: return jsonify({"message": "Unauthorized"}), 401
        rows = Donation.query.filter_by(donor_email=u.email).order_by(Donation.id.desc()).all()
        data = [{
            "id": d.id, "donation_category": d.donation_category, "donation_item": d.donation_item,
            "donation_quantity": d.donation_quantity, "location": d.location,
            "image_link": d.image_link, "status": d.status, "expiryDate":d.expiryDate
        } for d in rows]
        return jsonify({"donations": data}), 200

    def manager_list_donations():
        """Get donations for manager's community club.
        
        Returns:
            tuple: JSON response with pending and approved donations and HTTP status code.
        """
        u = get_current_user()
        if not u: return jsonify({"message": "Unauthorized"}), 401
        m = find_manager_by_email(u.email)
        rows = Donation.query.filter(Donation.location == m.cc, Donation.status.in_(["Pending", "Approved"]))\
                            .order_by(Donation.id.desc()).all()
        def ser(d: Donation):
            return {
                "id": d.id, "donor_email": d.donor_email, "donation_category": d.donation_category,
                "donation_item": d.donation_item, "donation_quantity": d.donation_quantity,
                "location": d.location, "image_link": d.image_link, "status": d.status,
                "expiryDate": d.expiryDate.isoformat() if d.expiryDate else None,
            }
        pending = [ser(d) for d in rows if d.status == "Pending"]
        approved = [ser(d) for d in rows if d.status == "Approved"]
        return jsonify({"pending": pending, "approved": approved}), 200

    def manager_approve(donation_id: int):
        """Approve a pending donation.
        
        Args:
            donation_id (int): ID of donation to approve.
            
        Returns:
            tuple: JSON response and HTTP status code.
        """
        u = get_current_user()
        if not u: return jsonify({"message": "Unauthorized"}), 401
        m = find_manager_by_email(u.email)
        d = Donation.query.get(donation_id)
        if not d: return jsonify({"message": "Donation not found"}), 404
        if d.location != m.cc: return jsonify({"message": "Cannot modify donations outside your CC"}), 403
        if d.status != "Pending": return jsonify({"message": "Only Pending donations can be approved"}), 400
        d.status = "Approved"; db.session.commit()

        # notify donor
        msg = (
            f"Your donation '{d.donation_item}' at {d.location} was approved by {m.cc}. "
            "Please come down within 2 days to donate your items. Thanks for contributing!"
        )
        notification_strategy = DatabaseNotificationStrategy()
        notification_strategy.create_notification(message=msg, receiver_email=d.donor_email)

        return jsonify({"ok": True, "id": d.id, "status": d.status}), 200

    def manager_reject(donation_id: int):
        """Reject a pending or approved donation.
        
        Args:
            donation_id (int): ID of donation to reject.
            
        Returns:
            tuple: JSON response and HTTP status code.
        """
        u = get_current_user()
        if not u: return jsonify({"message": "Unauthorized"}), 401
        m = find_manager_by_email(u.email)
        d = Donation.query.get(donation_id)
        if not d: return jsonify({"message": "Donation not found"}), 404
        if d.location != m.cc: return jsonify({"message": "Cannot modify donations outside your CC"}), 403
        if d.status not in ("Pending", "Approved"):
            return jsonify({"message": "Only Pending or Approved donations can be rejected"}), 400
        db.session.delete(d)
        db.session.commit()
        
        # notify donor
        msg = (
            f"Your donation '{d.donation_item}' at {d.location} was rejected. "
            "If you believe this was a mistake, please submit a new donation."
        )
        notification_strategy = DatabaseNotificationStrategy()
        notification_strategy.create_notification(message=msg, receiver_email=d.donor_email)

        return jsonify({"ok": True, "id": donation_id, "deleted": True}), 200

    def manager_add(donation_id: int):
        """Add approved donation to inventory.
        
        Approve → Added:
        - Create Item rows as Available only (no reservations).
        - Allocation is performed by the 10-min background allocator.
        
        Args:
            donation_id (int): ID of donation to add to inventory.
            
        Returns:
            tuple: JSON response with created items and HTTP status code.
        """
        u = get_current_user()
        if not u: return jsonify({"message": "Unauthorized"}), 401
        m = find_manager_by_email(u.email)

        d = Donation.query.get(donation_id)
        if not d: return jsonify({"message": "Donation not found"}), 404
        if d.location != m.cc: return jsonify({"message": "Cannot modify donations outside your CC"}), 403
        if d.status != "Approved": return jsonify({"message": "Only Approved donations can be added"}), 400

        try:
            d.status = "Added"
            created_items = []
            for _ in range(int(d.donation_quantity) or 0):
                it = Item(donation_id=d.id, status="Available")
                db.session.add(it)
                created_items.append(it)

            db.session.commit()

            # notify donors
            msg = (
                f"Your donation '{d.donation_item}' at {d.location} has been added to inventory "
                f"with {len(created_items)} item(s). We’ll match them to requests soon!"
            )
            notification_strategy = DatabaseNotificationStrategy()
            notification_strategy.create_notification(message=msg, receiver_email=d.donor_email)

            run_allocation()

            return jsonify({
                "message": f"{len(created_items)} items created as Available for donation {d.id}",
                "donation": {"id": d.id, "status": d.status},
                "items": [{"id": it.id, "status": it.status} for it in created_items],
                "note": "Allocator will match these to Pending requests automatically."
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Failed to add items for donation", "error": str(e)}), 500

