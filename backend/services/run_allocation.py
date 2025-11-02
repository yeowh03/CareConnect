"""Allocation Service for CareConnect Backend.

This module handles the core allocation algorithm that matches
pending requests with available donated items using FIFO ordering.
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy import or_
from typing import Dict, List

from ..models import db, Request, Donation, Item, Reservation
from ..services.notification_strategies import DatabaseNotificationStrategy

# Asia/Singapore timezone for date cutoffs, etc.
SG_TZ = timezone(timedelta(hours=8))

def run_allocation() -> Dict[str, str]:
    """Match pending requests to available items using FIFO algorithm.
    
    Matches Pending requests to Available items (FIFO within each queue).
    Updates request status to 'Matched' when fully allocated and sends
    notifications to requesters.
    
    Returns:
        dict: Allocation job execution results.
    """
    sg_today = datetime.now(SG_TZ).date()
    now_utc = datetime.now(timezone.utc)

    pending: List[Request] = (Request.query
        .filter(Request.status == "Pending")
        .order_by(Request.created_at.asc(), Request.id.asc())
        .all())

    changed = False

    for req in pending:
        requested = (req.request_quantity or 0)
        allocated = (req.allocation or 0)
        need = max(0, requested - allocated)

        # If already fully allocated, ensure status is Matched
        if need == 0:
            if requested > 0 and req.status != "Matched":
                req.status = "Matched"
                req.matched_at = now_utc
                changed = True
            continue

        # Find earliest-available items that match the request (location + item)
        candidates = (db.session.query(Item)
            .join(Donation, Item.donation_id == Donation.id)
            .filter(
                Item.status == "Available",
                Donation.location == req.location,
                Donation.donation_item == req.request_item,
                # Either no expiry or not expired in SG
                or_(Donation.expiryDate.is_(None), Donation.expiryDate >= sg_today),
            )
            .order_by(Item.id.asc())
            .limit(need)
            .all())

        for it in candidates:
            it.status = "Unavailable"
            db.session.add(Reservation(request_id=req.id, item_id=it.id))
            req.allocation = (req.allocation or 0) + 1
            changed = True

        # If we fulfilled the whole request, mark as Matched
        if (req.allocation or 0) >= requested and requested > 0:
            req.status = "Matched"
            req.matched_at = now_utc
            changed = True

            message = (
                f"Good news! Your request '{req.request_item}' in {req.location} "
                "has been successfully matched with available items."
            )
            notification_strategy = DatabaseNotificationStrategy()
            notification_strategy.create_notification(message=message, receiver_email=req.requester_email)

    if changed:
        db.session.commit()

    return {"job": "allocation", "status": "ok", "at": now_utc.isoformat()}