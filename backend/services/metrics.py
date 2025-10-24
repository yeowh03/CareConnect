from sqlalchemy import and_
from ..models import Request
from .broadcast_observer import subject

# fulfilment rate = (Matched + Completed) / (Matched + Completed + Pending)
# if denominator is 0 -> define as 1.0 (no pressure)

def compute_fulfilment_rate_for_cc(cc: str) -> float:
    matched = Request.query.filter(and_(Request.location == cc, Request.status == "Matched")).count()
    completed = Request.query.filter(and_(Request.location == cc, Request.status == "Completed")).count()
    pending = Request.query.filter(and_(Request.location == cc, Request.status == "Pending")).count()


    num = matched + completed
    denom = num + pending
    if denom == 0:
        return 1.0
    return num / float(denom)

# Public entrypoint used by routes or business logic

def check_and_broadcast_for_cc(cc: str) -> float:
    rate = compute_fulfilment_rate_for_cc(cc)
    subject.maybe_broadcast(cc, rate)
    return rate