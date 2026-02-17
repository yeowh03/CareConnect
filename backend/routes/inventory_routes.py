"""Inventory Routes for CareConnect Backend.

This module defines Flask routes for inventory management and reporting
including CC summaries, shortage tracking, and analytics.
"""

from flask import Blueprint
from ..controllers.inventory_controller import InventoryController as c

inventory_bp = Blueprint("inventory", __name__, url_prefix="/api")

# Manager: Get comprehensive CC summary with detailed statistics
@inventory_bp.route("/manager/cc_summary", methods=["GET"])
def get_manager_summary():
    return c.manager_cc_summary()

# Manager: Get severe shortage items for specific location
@inventory_bp.route("/manager/severe_shortage/<string:location>", methods=["GET"])
def get_severe_shortage(location):
    return c.severe_shortage(location)

# Manager: Get detailed inventory for specific CC
@inventory_bp.route("/manager/inventory/<string:location>")
def get_cc_inventory(location):
    return c.get_cc_inventory(location)

# Client: Get simplified CC summary with shortage highlights
@inventory_bp.route("/client/cc_summary", methods=["GET"])
def get_client_summary(): 
    return c.client_cc_summary()