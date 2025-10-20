# server/utils.py
import os, html, re, time, uuid
from werkzeug.utils import secure_filename
from flask import session
from passlib.hash import argon2
import requests
import threading, time
from datetime import datetime, timedelta, timezone
from sqlalchemy import or_

from .extensions import db
from .models import User, Client, Manager, Notification, Request
from .models import Donation, Item, Reservation

SG_TZ = timezone(timedelta(hours=8))

# def _allocate_pending_requests_once(app):
#     """
#     Central FIFO allocator:
#     - Walk Pending requests oldest-first.
#     - For each, take matching Available items (same location & item),
#       ignoring expired donations, and reserve them.
#     - If a request becomes fully allocated, mark it 'Matched' and stamp matched_at.
#     """
#     with app.app_context():
#         sg_today = datetime.now(SG_TZ).date()

#         pending_reqs = (
#             Request.query
#             .filter(Request.status == "Pending")
#             .order_by(Request.created_at.asc(), Request.id.asc())
#             .all()
#         )

#         now_utc = datetime.now(timezone.utc)
#         changed = False

#         for req in pending_reqs:
#             needed = max(0, (req.request_quantity or 0) - (req.allocation or 0))
#             if needed == 0:
#                 if req.status != "Matched" and (req.request_quantity or 0) > 0:
#                     req.status = "Matched"
#                     req.matched_at = now_utc
#                     changed = True
#                 continue

#             candidates = (
#                 db.session.query(Item)
#                 .join(Donation, Item.donation_id == Donation.id)
#                 .filter(
#                     Item.status == "Available",
#                     Donation.location == req.location,
#                     Donation.donation_item == req.request_item,
#                     # IMPORTANT: expiry by Singapore date
#                     or_(Donation.expiryDate.is_(None), Donation.expiryDate >= sg_today),
#                 )
#                 .order_by(Item.id.asc())
#                 .limit(needed)
#                 .all()
#             )

#             for it in candidates:
#                 it.status = "Unavailable"
#                 db.session.add(Reservation(request_id=req.id, item_id=it.id))
#                 req.allocation = (req.allocation or 0) + 1
#                 changed = True

#             if req.allocation >= (req.request_quantity or 0) and (req.request_quantity or 0) > 0:
#                 req.status = "Matched"
#                 req.matched_at = now_utc
#                 changed = True

#         if changed:
#             db.session.commit()

# def start_allocator_daemon(app, every_minutes: int = 10):
#     """
#     Runs _allocate_pending_requests_once(app) every `every_minutes` (SG time based).
#     """
#     def loop():
#         while True:
#             try:
#                 _allocate_pending_requests_once(app)
#             except Exception:
#                 pass
#             time.sleep(max(60, int(every_minutes) * 60))

#     t = threading.Thread(target=loop, name="fifo-allocator", daemon=True)
#     t.start()

# ------------------------------------------------------------------------------

# # server/utils.py  (REPLACE the existing _cleanup_expired_items_once)
# def _cleanup_expired_items_once(app):
#     """
#     Daily cleanup at Singapore midnight:
#     - Find donations whose expiryDate is BEFORE today's Singapore date.
#     - Remove ALL their items.
#     - For any reservations referencing those items:
#         * decrement the request's allocation,
#         * if that request was 'Matched', set it to 'Pending' and clear matched_at.
#     - Do NOT reallocate here; the 10-min allocator will handle it.
#     """
#     with app.app_context():
#         sg_today = datetime.now(SG_TZ).date()

#         expired = Donation.query.filter(
#             Donation.expiryDate.isnot(None),
#             Donation.expiryDate < sg_today
#         ).all()

#         if not expired:
#             return {"affected_requests": [], "items_removed": 0}

#         affected_request_ids = set()
#         items_removed = 0

#         for d in expired:
#             items = Item.query.filter_by(donation_id=d.id).all()
#             for it in items:
#                 # Free reservations tied to this item
#                 reservations = Reservation.query.filter_by(item_id=it.id).all()
#                 for res in reservations:
#                     req = Request.query.get(res.request_id)
#                     if req:
#                         req.allocation = max(0, (req.allocation or 0) - 1)
#                         affected_request_ids.add(req.id)
#                         if req.status == "Matched":
#                             req.status = "Pending"
#                             req.matched_at = None
#                     db.session.delete(res)

#                 # Remove the expired item itself
#                 db.session.delete(it)
#                 items_removed += 1

#         db.session.commit()
#         return {
#             "affected_requests": sorted(list(affected_request_ids)),
#             "items_removed": items_removed
#         }

# ------------------------------------------------------------------------------

# def _expire_matched_requests_once(app):
#     """
#     Any 'Matched' request older than 2 days -> mark 'Expired',
#     free its reserved items, and remove its reservations.
#     """
#     with app.app_context():
#         now_utc = datetime.now(timezone.utc)
#         cutoff = now_utc - timedelta(days=2)

#         to_expire = (
#             Request.query
#             .filter(
#                 Request.status == "Matched",
#                 Request.matched_at.isnot(None),
#                 Request.matched_at <= cutoff
#             )
#             .order_by(Request.id.asc())
#             .all()
#         )

#         if not to_expire:
#             return

#         try:
#             for req in to_expire:
#                 reservations = Reservation.query.filter_by(request_id=req.id).all()
#                 for res in reservations:
#                     it = Item.query.get(res.item_id)
#                     if it:
#                         it.status = "Available"
#                     db.session.delete(res)
#                 req.status = "Expired"

#             db.session.commit()
#         except Exception:
#             db.session.rollback()


# def _sleep_until_next_sg_time(hour: int, minute: int) -> float:
#     now = datetime.now(SG_TZ)
#     next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
#     if next_run <= now:
#         next_run += timedelta(days=1)
#     return (next_run - now).total_seconds()

# # ------------------------------------------------------------------------------

# def start_cleanup_expired_items_daemon(app, run_at_hour_sg: int = 0, run_at_minute_sg: int = 0):
#     """Daily daemon to clean up items from expired donations at HH:MM Singapore time."""
#     def loop():
#         while True:
#             try:
#                 time.sleep(_sleep_until_next_sg_time(run_at_hour_sg, run_at_minute_sg))
#                 _cleanup_expired_items_once(app)
#             except Exception:
#                 # Keep thread alive; optionally log
#                 time.sleep(60)

#     t = threading.Thread(target=loop, name="cleanup-expired-donation-items-sg", daemon=True)
#     t.start()


# def start_expire_matched_requests_daemon(app, run_at_hour_sg: int = 0, run_at_minute_sg: int = 0):
#     """Daily daemon to expire old Matched requests at HH:MM Singapore time (default 00:00)."""
#     def loop():
#         while True:
#             try:
#                 time.sleep(_sleep_until_next_sg_time(run_at_hour_sg, run_at_minute_sg))
#                 _expire_matched_requests_once(app)
#             except Exception:
#                 # Keep thread alive; optionally log
#                 time.sleep(60)

#     t = threading.Thread(target=loop, name="expire-matched-requests-daily-sg", daemon=True)
#     t.start()


# ---------- user helpers ----------
def get_current_user():
    email = session.get("user_email")
    if not email:
        return None
    return db.session.get(User, email)

def find_user_by_email(email): return User.query.get(email)
def find_client_by_email(email): return Client.query.get(email)
def find_manager_by_email(email): return Manager.query.get(email)

# ---------- CC dataset helpers ----------
def parse_desc_table(desc_html: str) -> dict:
    if not desc_html: return {}
    text = html.unescape(desc_html)
    pairs = re.findall(r"<th>(.*?)</th>\s*<td>(.*?)</td>", text, flags=re.I | re.S)
    data = {}
    tag_re = re.compile(r"<[^>]+>")
    for k, v in pairs:
        key = str(k).strip().upper()
        val = tag_re.sub("", v).strip()
        data[key] = val
    return data

def feat_to_marker(feat):
    geom = (feat or {}).get("geometry") or {}
    props = (feat or {}).get("properties") or {}
    if geom.get("type") != "Point": return None
    coords = geom.get("coordinates") or []
    if len(coords) < 2: return None
    lng, lat = float(coords[0]), float(coords[1])
    table = parse_desc_table(props.get("Description") or props.get("description") or "")
    name = table.get("NAME") or props.get("Name") or props.get("name") or "Community Club"
    address = " ".join([t for t in [
        table.get("ADDRESSBLOCKHOUSENUMBER") or "",
        table.get("ADDRESSSTREETNAME") or "",
        table.get("ADDRESSPOSTALCODE") or "",
    ] if t]).strip() or None
    link = table.get("HYPERLINK") or None
    return {"name": name, "lat": lat, "lng": lng, "address": address, "link": link}

def fetch_cc_markers_from_api(DATASET_ID: str):
    POLL_URL = f"https://api-open.data.gov.sg/v1/public/api/datasets/{DATASET_ID}/poll-download"
    j = requests.get(POLL_URL, timeout=20).json()
    if j.get("code") != 0 or "data" not in j or "url" not in j["data"]:
        raise RuntimeError(f"Poll Download failed: {j}")
    gj = requests.get(j["data"]["url"], timeout=60).json()
    features = (gj or {}).get("features") or []
    markers = []
    for f in features:
        m = feat_to_marker(f)
        if m: markers.append(m)
    return markers

# ---------- file upload (Supabase) ----------
def upload_image_to_supabase(file_storage, supabase, bucket: str) -> str:
    if not file_storage or file_storage.filename == "":
        raise ValueError("Image is required")
    if not (file_storage.mimetype or "").startswith("image/"):
        raise ValueError("File must be an image")

    original = secure_filename(file_storage.filename)
    ext = os.path.splitext(original)[1].lower()
    unique = f"{uuid.uuid4().hex}{ext}"
    dirpath = time.strftime("%Y/%m/%d")
    storage_path = f"{dirpath}/{unique}"

    data = file_storage.read()
    file_storage.stream.seek(0)

    resp = supabase.storage.from_(bucket).upload(
        file=data, path=storage_path,
        file_options={"content-type": file_storage.mimetype, "upsert": False},
    )
    if getattr(resp, "status_code", 200) >= 400:
        raise RuntimeError(f"Upload failed: {resp}")

    public_url = supabase.storage.from_(bucket).get_public_url(storage_path)
    if not public_url:
        raise RuntimeError("Could not get public URL for uploaded file")
    return public_url

# ---------- password helpers ----------
def hash_password(pw: str) -> str:
    return argon2.hash(pw)

def verify_password(pw: str, hashed: str) -> bool:
    from passlib.hash import argon2 as _argon
    return _argon.verify(pw, hashed)


