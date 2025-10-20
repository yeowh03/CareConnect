from datetime import datetime, timedelta, timezone
from sqlalchemy import or_
from typing import Dict, List

from ..models import db, Request, Donation, Item, Reservation

# Asia/Singapore timezone for date cutoffs, etc.
SG_TZ = timezone(timedelta(hours=8))

# ---------------------------
# 1) Allocate pending requests
# ---------------------------

def run_allocation() -> Dict[str, str]:
    """Match Pending requests to Available items (FIFO within each queue)."""
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

    if changed:
        db.session.commit()

    return {"job": "allocation", "status": "ok", "at": now_utc.isoformat()}