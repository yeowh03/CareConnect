"""Metrics Service for CareConnect Backend.

This module calculates fulfillment metrics for community clubs
and triggers broadcasts when fulfillment rates are low.
"""

from sqlalchemy import and_, func
from ..models import Request
from ..broadcast_observer import subject
from ..models import Request, db  

def check_and_broadcast_for_cc(cc: str) -> float:
    """Check fulfillment rate for a community club and broadcast if low.
    
    Args:
        cc (str): Community club name.
        
    Returns:
        float: Fulfillment rate (0.0 to 1.0).
    """
    
    req_row = (
        db.session.query(
            func.sum(Request.request_quantity),
            func.sum(Request.allocation)
        )
        .filter(Request.location==cc)
        .first()
    )

    allocated = req_row[1] if req_row[1] else 0
    total_req = req_row[0] if req_row[0] else 0
    
    if total_req == 0:
        rate = 1.0
    else:
        rate = allocated / total_req

    subject.maybe_broadcast(cc, rate)
    return rate