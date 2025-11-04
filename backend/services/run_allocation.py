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
    # Get current date in Singapore timezone for expiry checks
    sg_today = datetime.now(SG_TZ).date()
    now_utc = datetime.now(timezone.utc)

    # Get all pending requests ordered by creation time (FIFO)
    pending: List[Request] = (Request.query
        .filter(Request.status == "Pending")
        .order_by(Request.created_at.asc(), Request.id.asc())
        .all())

    changed = False  # Track if any changes were made

    # Process each pending request in FIFO order
    for req in pending:
        requested = (req.request_quantity or 0)
        allocated = (req.allocation or 0)
        need = max(0, requested - allocated)  # How many more items needed

        # If request is already fully allocated, mark as Matched
        if need == 0:
            if requested > 0 and req.status != "Matched":
                req.status = "Matched"
                req.matched_at = now_utc
                changed = True
            continue  # Move to next request

        # Find matching available items for this request
        # Match criteria: same location, same item type, not expired
        candidates = (db.session.query(Item)
            .join(Donation, Item.donation_id == Donation.id)
            .filter(
                Item.status == "Available",                    # Item must be available
                Donation.location == req.location,             # Same community club
                Donation.donation_item == req.request_item,    # Same item type
                # Either no expiry date or not yet expired in Singapore timezone
                or_(Donation.expiryDate.is_(None), Donation.expiryDate >= sg_today),
            )
            .order_by(Item.id.asc())  # FIFO allocation (earliest items first)
            .limit(need)              # Only get as many as needed
            .all())

        # Allocate each candidate item to this request
        for it in candidates:
            it.status = "Unavailable"  # Mark item as allocated
            db.session.add(Reservation(request_id=req.id, item_id=it.id))  # Create reservation
            req.allocation = (req.allocation or 0) + 1  # Increment allocation count
            changed = True

        # If request is now fully allocated, mark as Matched and notify user
        if (req.allocation or 0) >= requested and requested > 0:
            req.status = "Matched"
            req.matched_at = now_utc
            changed = True

            # Send notification to requester about successful match
            message = (
                f"Good news! Your request '{req.request_item}' in {req.location} "
                "has been successfully matched with available items."
            )
            notification_strategy = DatabaseNotificationStrategy()
            notification_strategy.create_notification(message=message, receiver_email=req.requester_email)

    # Commit all changes if any allocations were made
    if changed:
        db.session.commit()

    return {"job": "allocation", "status": "ok", "at": now_utc.isoformat()}