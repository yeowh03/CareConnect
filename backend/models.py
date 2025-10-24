# server/models.py
from datetime import datetime, timezone
from .extensions import db

class User(db.Model):
    __tablename__ = "user"
    email = db.Column(db.String(255), primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=True)
    contact_number = db.Column(db.String(50), nullable=True, unique=True)
    password_hash = db.Column(db.Text, nullable=True)   # null if Google-only
    role = db.Column(db.Enum("M", "C", name="role_enum"), nullable=False)

class Manager(db.Model):
    __tablename__ = "manager"
    email = db.Column(db.String(255), db.ForeignKey("user.email", ondelete="CASCADE"), primary_key=True)
    cc = db.Column(db.String(255), nullable=False)

class Client(db.Model):
    __tablename__ = "client"
    email = db.Column(db.String(255), db.ForeignKey("user.email", ondelete="CASCADE"), primary_key=True)
    monthly_income = db.Column(db.Numeric(12, 2), nullable=True)
    account_status = db.Column(db.Enum("Pending", "Confirmed", "Rejected", name="account_status"), nullable=False, default="Pending")
    gmail_acc = db.Column(db.Boolean, nullable=False, default=False)

class Request(db.Model):
    __tablename__ = "request"
    id = db.Column(db.Integer, primary_key=True)
    requester_email = db.Column(db.String(255), db.ForeignKey("client.email", ondelete="CASCADE"), nullable=False)
    request_category = db.Column(db.Enum("Food", "Drinks", "Furnitures", "Electronics", "Essentials", name="category_enum"), nullable=False)
    request_item = db.Column(db.String(120), nullable=False)
    request_quantity = db.Column(db.Integer, nullable=False, default=1)
    allocation = db.Column(db.Integer, nullable=False, default=0)
    location = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Enum("Pending", "Matched", "Expired", "Completed", name="s"), nullable=False, default="Pending")
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False)
    matched_at = db.Column(db.DateTime(timezone=True), nullable=True)

class Donation(db.Model):
    __tablename__ = "donation"
    id = db.Column(db.Integer, primary_key=True)
    donor_email = db.Column(db.String(255), db.ForeignKey("client.email", ondelete="CASCADE"), nullable=False)
    donation_category = db.Column(db.Enum("Food", "Drinks", "Furnitures", "Electronics", "Essentials", name="category_enum"), nullable=False)
    donation_item = db.Column(db.String(120), nullable=False)
    donation_quantity = db.Column(db.Integer, nullable=False, default=1)
    location = db.Column(db.String(255), nullable=False)
    image_link = db.Column(db.Text, nullable=False)
    expiryDate = db.Column(db.Date, nullable=True)
    approved_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    status = db.Column(db.Enum("Pending", "Approved", "Added", name="s2"), default="Pending")

class Item(db.Model):
    __tablename__ = "item"
    id = db.Column(db.Integer, primary_key=True)
    donation_id = db.Column(db.Integer, db.ForeignKey("donation.id", ondelete="CASCADE"), nullable=False)
    status = db.Column(db.Enum("Available", "Unavailable", name="Availability"), nullable=False, default="Available")

class Reservation(db.Model):
    __tablename__ = "reservation"
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("request.id", ondelete="CASCADE"), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("item.id", ondelete="CASCADE"), nullable=False)

class Notification(db.Model):
    __tablename__ = "notification"
    id = db.Column(db.Integer, primary_key=True)
    receiver_email = db.Column(db.String(255), db.ForeignKey("user.email", ondelete="CASCADE"), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
