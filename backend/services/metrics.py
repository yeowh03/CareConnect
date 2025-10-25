from sqlalchemy import and_, func
from ..models import Request
from .broadcast_observer import subject
from ..models import Request, db  

# Public entrypoint used by routes or business logic

def check_and_broadcast_for_cc(cc: str) -> float:
    
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
    
    if allocated == 0:
        rate = 1.0
    else:
        rate = allocated / total_req

    subject.maybe_broadcast(cc, rate)
    return rate