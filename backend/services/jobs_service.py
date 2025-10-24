# services/jobs_service.py
# ------------------------------------------------------------
# Core business logic for periodic jobs (no HTTP, no threads).
# Controllers/schedulers should call these functions.
# ------------------------------------------------------------

from datetime import datetime, timedelta, timezone
from sqlalchemy import or_
from typing import Dict, List

from ..models import db, Request, Donation, Item, Reservation
from .run_allocation import run_allocation
from ..services.metrics import check_and_broadcast_for_cc

# Asia/Singapore timezone for date cutoffs, etc.
SG_TZ = timezone(timedelta(hours=8))


# -----------------------------------
# 2) Cleanup items from expired donors
# -----------------------------------
def run_cleanup_expired_items_once() -> Dict[str, object]:
    """
    Daily cleanup at Singapore midnight:
    - Find donations whose expiryDate is BEFORE today's Singapore date.
    - Remove ALL their items.
    - For any reservations referencing those items:
        * decrement the request's allocation,
        * if that request was 'Matched', set it to 'Pending' and clear matched_at.
    """
    sg_today = datetime.now(SG_TZ).date()

    expired_dons: List[Donation] = Donation.query.filter(
        Donation.expiryDate.isnot(None),
        Donation.expiryDate < sg_today
    ).all()

    if not expired_dons:
        return {"job": "cleanup_expired_items", "status": "ok", "items_removed": 0, "affected_requests": []}

    affected_request_ids = set()
    items_removed = 0

    for d in expired_dons:
        items: List[Item] = Item.query.filter_by(donation_id=d.id).all()
        for it in items:
            # Remove reservations for this item
            reservations = Reservation.query.filter_by(item_id=it.id).all()
            for res in reservations:
                req = Request.query.get(res.request_id)
                if req:
                    # Reduce allocation and possibly revert status to Pending
                    req.allocation = max(0, (req.allocation or 0) - 1)
                    if req.status == "Matched":
                        req.status = "Pending"
                        req.matched_at = None
                    affected_request_ids.add(req.id)
                db.session.delete(res)

            db.session.delete(it)
            items_removed += 1

    db.session.commit()

    # run matching
    run_allocation()

    # Identify affected CCs and broadcast if needed
    affected_ccs = set()
    from ..models import Request
    for rid in affected_request_ids:
        req = Request.query.get(rid)
        if req and req.location:
            affected_ccs.add(req.location)
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
    """After N days in 'Matched', free the items and mark request as 'Expired'."""
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
            # (optional) req.matched_at = None

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
    """
    Delete donations with status == 'Approved' that are older than N days.
    Also, send a notification to the donor about removal.
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

    from ..models import Notification

    deleted_count = 0
    for donation in old_donations:
        # Create notification for the donor
        message = (
            f"Your donation '{donation.donation_item}' in {donation.location} "
            "has been automatically removed after 2 days of approval."
        )
        notif = Notification(
            receiver_email=donation.donor_email,
            message=message,
            link="/donations"  # optional, adjust to your frontend route
        )
        db.session.add(notif)

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