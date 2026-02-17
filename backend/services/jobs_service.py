"""Jobs Service for CareConnect Backend.

This module contains core business logic for periodic background jobs
including cleanup operations, expiry management, and allocation tasks.
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy import or_
from typing import Dict, List

from ..models import db, Request, Donation, Item, Reservation
from .run_allocation import run_allocation
from ..services.metrics import check_and_broadcast_for_cc
from ..services.notification_strategies import DatabaseNotificationStrategy

# Asia/Singapore timezone for date cutoffs, etc.
SG_TZ = timezone(timedelta(hours=8))

def run_cleanup_expired_items_once() -> Dict[str, object]:
    """Clean up expired donation items.
    
    Daily cleanup at Singapore midnight:
    - Find donations whose expiryDate is BEFORE today's Singapore date.
    - Remove ALL their items.
    - For any reservations referencing those items:
        * decrement the request's allocation,
        * if that request was 'Matched', set it to 'Pending' and clear matched_at.
        
    Returns:
        dict: Job execution results with counts and affected items.
    """
    sg_today = datetime.now(SG_TZ).date()

    # Find donations that have expired (past their expiry date in Singapore timezone)
    expired_dons: List[Donation] = Donation.query.filter(
        Donation.expiryDate.isnot(None),
        Donation.expiryDate < sg_today
    ).all()

    # Early return if no expired donations found
    if not expired_dons:
        return {"job": "cleanup_expired_items", "status": "ok", "items_removed": 0, "affected_requests": []}

    affected_request_ids = set()  # Track requests affected by item removal
    items_removed = 0

    # Process each expired donation
    for d in expired_dons:
        items: List[Item] = Item.query.filter_by(donation_id=d.id).all()
        
        # Remove all items from this expired donation
        for it in items:
            # Find and remove reservations for this item
            reservations = Reservation.query.filter_by(item_id=it.id).all()
            for res in reservations:
                req = Request.query.get(res.request_id)
                if req:
                    # Reduce allocation count and revert to Pending if was Matched
                    req.allocation = max(0, (req.allocation or 0) - 1)
                    if req.status == "Matched":
                        req.status = "Pending"  # Allow re-matching with other items
                        req.matched_at = None
                    affected_request_ids.add(req.id)
                db.session.delete(res)  # Remove the reservation

            db.session.delete(it)  # Remove the expired item
            items_removed += 1

    db.session.commit()

    # Run allocation algorithm to re-match affected requests
    run_allocation()

    # Check fulfillment rates for affected CCs and broadcast if low
    affected_ccs = set()
    from ..models import Request
    for rid in affected_request_ids:
        req = Request.query.get(rid)
        if req and req.location:
            affected_ccs.add(req.location)
    
    # Broadcast low fulfillment alerts for affected community clubs
    for cc in affected_ccs:
        check_and_broadcast_for_cc(cc)

    return {
        "job": "cleanup_expired_items",
        "status": "ok",
        "items_removed": items_removed,
        "affected_requests": sorted(list(affected_request_ids)),
        "at": datetime.utcnow().isoformat(),
    }


# ----------------------------------------
# 3) Expire old matches (uncollected items)
# ----------------------------------------
def run_expire_matched_requests_once(days_until_expire: int = 2) -> Dict[str, str]:
    """Expire old matched requests that haven't been collected.
    
    After N days in 'Matched', free the items and mark request as 'Expired'.
    
    Args:
        days_until_expire (int): Number of days before expiring matched requests.
        
    Returns:
        dict: Job execution results.
    """
    now_utc = datetime.now(timezone.utc)
    cutoff = now_utc - timedelta(days=days_until_expire)

    to_expire: List[Request] = (Request.query
        .filter(
            Request.status == "Matched",
            Request.matched_at.isnot(None),
            Request.matched_at <= cutoff,
        )
        .order_by(Request.id.asc())
        .all())

    if not to_expire:
        return {"job": "expire_matched_requests", "status": "ok", "at": now_utc.isoformat()}

    try:
        for req in to_expire:
            # Free all reserved items
            reservations = Reservation.query.filter_by(request_id=req.id).all()
            for res in reservations:
                item = Item.query.get(res.item_id)
                if item:
                    item.status = "Available"
                db.session.delete(res)

            req.status = "Expired"
            
            msg = (
                f"Your request '{req.request_item}' in {req.location} "
                "has expired after 2 days of being matched."
                "Please make another request if needed."
            )
            notification_strategy = DatabaseNotificationStrategy()
            notification_strategy.create_notification(message=msg, receiver_email=req.requester_email)

        db.session.commit()

        # run matching
        run_allocation()
        
        return {"job": "expire_matched_requests", "status": "ok", "count": len(to_expire), "at": now_utc.isoformat()}
    except Exception as e:
        db.session.rollback()
        raise e
    
# ----------------------------------------
# 3) Expire approved donations (uncollected items)
# ----------------------------------------
def run_cleanup_approved_donations_once(days_until_delete: int = 2) -> Dict[str, str]:
    """Clean up old approved donations that haven't been collected.
    
    Delete donations with status == 'Approved' that are older than N days.
    Also, send a notification to the donor about removal.
    
    Args:
        days_until_delete (int): Number of days before deleting approved donations.
        
    Returns:
        dict: Job execution results with deletion count.
    """
    now_utc = datetime.now(timezone.utc)
    cutoff = now_utc - timedelta(days=days_until_delete)

    # Find old approved donations
    old_donations: List[Donation] = Donation.query.filter(
        Donation.status == "Approved",
        Donation.approved_at <= cutoff
    ).all()

    if not old_donations:
        return {"job": "cleanup_approved_donations", "status": "ok", "deleted": 0, "at": now_utc.isoformat()}

    deleted_count = 0
    for donation in old_donations:
        # Create notification for the donor
        message = (
            f"Your donation '{donation.donation_item}' in {donation.location} "
            "has been automatically removed after 2 days of approval."
        )
        notification_strategy = DatabaseNotificationStrategy()
        notification_strategy.create_notification(message=message, receiver_email=donation.donor_email)

        # Delete donation (cascade removes items, reservations)
        db.session.delete(donation)
        deleted_count += 1

    db.session.commit()

    return {
        "job": "cleanup_approved_donations",
        "status": "ok",
        "deleted": deleted_count,
        "at": now_utc.isoformat(),
    }