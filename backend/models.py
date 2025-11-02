"""Database Models for CareConnect Application.

This module defines all SQLAlchemy database models used in the CareConnect system,
including User, Manager, Client, Request, Donation, Item, Reservation, and Notification models.
"""

from datetime import datetime, timezone
from .extensions import db

class User(db.Model):
    """User model representing both managers and clients.
    
    Attributes:
        email (str): Primary key, unique email address
        name (str): User's full name
        contact_number (str): Unique contact number
        password_hash (str): Hashed password (null for Google OAuth users)
        role (str): User role - 'M' for Manager, 'C' for Client
    """
    __tablename__ = "user"
    email = db.Column(db.String(255), primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=True)
    contact_number = db.Column(db.String(50), nullable=True, unique=True)
    password_hash = db.Column(db.Text, nullable=True)   # null if Google-only
    role = db.Column(db.Enum("M", "C", name="role_enum"), nullable=False)

class Manager(db.Model):
    """Manager model for community club managers.
    
    Attributes:
        email (str): Foreign key to User.email
        cc (str): Community club name the manager oversees
    """
    __tablename__ = "manager"
    email = db.Column(db.String(255), db.ForeignKey("user.email", ondelete="CASCADE"), primary_key=True)
    cc = db.Column(db.String(255), nullable=False)

class Client(db.Model):
    """Client model for users who can make requests and donations.
    
    Attributes:
        email (str): Foreign key to User.email
        monthly_income (Decimal): Client's monthly income
        account_status (str): Account status - Pending, Confirmed, or Rejected
        gmail_acc (bool): Whether user registered via Google OAuth
    """
    __tablename__ = "client"
    email = db.Column(db.String(255), db.ForeignKey("user.email", ondelete="CASCADE"), primary_key=True)
    monthly_income = db.Column(db.Numeric(12, 2), nullable=True)
    account_status = db.Column(db.Enum("Pending", "Confirmed", "Rejected", name="account_status"), nullable=False, default="Pending")
    gmail_acc = db.Column(db.Boolean, nullable=False, default=False)

class Request(db.Model):
    """Request model for items requested by clients.
    
    Attributes:
        id (int): Primary key
        requester_email (str): Foreign key to Client.email
        request_category (str): Category - Food, Drinks, Furnitures, Electronics, Essentials
        request_item (str): Name of requested item
        request_quantity (int): Quantity requested
        allocation (int): Number of items allocated
        location (str): Pickup location
        status (str): Request status - Pending, Matched, Expired, Completed
        created_at (datetime): When request was created
        matched_at (datetime): When request was matched with donations
    """
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
    """Donation model for items donated by clients.
    
    Attributes:
        id (int): Primary key
        donor_email (str): Foreign key to Client.email
        donation_category (str): Category - Food, Drinks, Furnitures, Electronics, Essentials
        donation_item (str): Name of donated item
        donation_quantity (int): Quantity donated
        location (str): Donation location
        image_link (str): URL to donation image
        expiryDate (date): Expiry date for perishable items
        approved_at (datetime): When donation was approved
        status (str): Donation status - Pending, Approved, Added
    """
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
    """Item model representing individual units from donations.
    
    Attributes:
        id (int): Primary key
        donation_id (int): Foreign key to Donation.id
        status (str): Item availability - Available or Unavailable
    """
    __tablename__ = "item"
    id = db.Column(db.Integer, primary_key=True)
    donation_id = db.Column(db.Integer, db.ForeignKey("donation.id", ondelete="CASCADE"), nullable=False)
    status = db.Column(db.Enum("Available", "Unavailable", name="Availability"), nullable=False, default="Available")

class Reservation(db.Model):
    """Reservation model linking requests to specific items.
    
    Attributes:
        id (int): Primary key
        request_id (int): Foreign key to Request.id
        item_id (int): Foreign key to Item.id
    """
    __tablename__ = "reservation"
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("request.id", ondelete="CASCADE"), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("item.id", ondelete="CASCADE"), nullable=False)

class Notification(db.Model):
    """Notification model for user notifications.
    
    Attributes:
        id (int): Primary key
        receiver_email (str): Foreign key to User.email
        message (str): Notification message content
        created_at (datetime): When notification was created
        viewed (bool): Whether notification has been viewed
    """
    __tablename__ = "notification"
    id = db.Column(db.Integer, primary_key=True)
    receiver_email = db.Column(db.String(255), db.ForeignKey("user.email", ondelete="CASCADE"), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    viewed = db.Column(db.Boolean, default=False)
