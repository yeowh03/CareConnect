from flask import Blueprint
from ..controllers.inventory_controller import InventoryController as c

inventory_bp = Blueprint("inventory", __name__, url_prefix="/api")

@inventory_bp.route("/manager/cc_summary", methods=["GET"])
def get_manager_summary():
    return c.manager_cc_summary()

@inventory_bp.route("/manager/severe_shortage/<string:location>", methods=["GET"])
def get_severe_shortage(location):
    return c.severe_shortage(location)

@inventory_bp.route("/manager/inventory/<string:location>")
def get_cc_inventory(location):
    return c.get_cc_inventory(location)

@inventory_bp.route("/client/cc_summary", methods=["GET"])
def get_client_summary(): return c.client_cc_summary()