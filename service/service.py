"""
Inventory Service

Paths:

------

1. GET /inventory
    - Returns a list of all inventories in the inventory
2. GET /inventory?product_id=<int>
    - Returns the inventory record with the given product_id
3. GET /inventory/<int:product_id>/condition/<string:condition>
    - Returns the inventory record with the given product_id and condition

4. POST /inventory
    - Given the data body this creates an inventory record in the DB

5. PUT /inventory/<int:product_id>/condition/<string:condition>
    - Updates the inventory record with the given product_id and condition
6. PUT /inventory/<int:product_id>/condition/<string:condition>/activate
    - Given the product_id and condition this updates available = 1
7. PUT /inventory/<int:product_id>/condition/<string:condition>/deactivate
    - Given the product_id and condition this updates available = 0
8. PUT /inventory/<int:product_id>/condition/<string:condition>/restock
    - Given the product_id, condition and amount (body) this updates quantity += amount

9. DELETE /inventory/<int:product_id>/condition/<string:condition>
    - Given the product_id and condition this updates available = 0
"""

from flask import jsonify, request, url_for, make_response, abort
from flask_api import status
from service.model import Inventory
from service.error_handlers import *

from . import app

DEMO_MSG = "Inventory REST API Service"

################################################################################
# INDEX
################################################################################
@app.route("/")
def index():
    """ Root URL response """
    app.logger.info("Request for Root URL")
    return app.send_static_file('index.html')
    # return (
    #     jsonify(
    #         name=DEMO_MSG,
    #         version="1.0",
    #         paths=url_for("list_inventories", _external=True),
    #     ),
    #     status.HTTP_200_OK,
    # )

################################################################################
# GET
################################################################################
@app.route("/inventory", methods=["GET"])
def list_inventories():
    """
    Returns a list of all inventories in the inventory
    GET /inventory
    """
    app.logger.info("A GET request for ALL inventories")
    inventories = []
    params = request.args
    if len(params) > 0:
        pid = params.get("product_id")
        if pid:
            inventories = Inventory.find_by_product_id(pid)
        else:
            return bad_request("Invalid request parameters: missing (product_id)")
    else:
        inventories = Inventory.all()

    results = []
    for inv in inventories:
        json = inv.serialize()
        # if json['available'] == 1:
        results.append(json)

    if len(results) == 0:
        return not_found("Inventories were not found")
    app.logger.info("Returning {} inventories".format(len(results)))
    return make_response(jsonify(results), status.HTTP_200_OK)

@app.route("/inventory/<int:product_id>/condition/<string:condition>", methods=["GET"])
def get_inventory_by_pid_condition(product_id, condition):
    """
    Returns the inventory with the given product_id and condition
    GET /inventory/<int:product_id>/condition/<string:condition>
    """
    app.logger.info("A GET request for inventories with product_id {} and condition {}"\
                    .format(product_id, condition))
    inventory = Inventory.find(product_id, condition)
    # if (not inventory) or\
        # (inventory and inventory.serialize()['available'] == 0):
    if not inventory:
        return not_found("Inventory ({}, {})".format(product_id, condition))
    app.logger.info("Return inventory with product_id {} and condition {}"\
                    .format(product_id, condition))
    return make_response(jsonify(inventory.serialize()), status.HTTP_200_OK)

################################################################################
# POST
################################################################################
@app.route("/inventory", methods=["POST"])
def create_inventory():
    """
    Creates a new inventory in the Inventory DB based the data in the body
    POST /inventory
    """
    app.logger.info("Request to create an Inventory record")
    check_content_type("application/json")
    json = request.get_json()
    inventory = Inventory()
    inventory.deserialize(json)
    inventory.validate_data()

    if Inventory.find(json['product_id'], json['condition']):
        return create_conflict_error("The Record you're trying to create already exists!")

    inventory.create()
    location_url = url_for("get_inventory_by_pid_condition",\
        product_id=inventory.product_id, condition=inventory.condition, _external=True)
    app.logger.info("Inventory ({}, {}) created."\
                    .format(inventory.product_id, inventory.condition))
    return make_response(
        jsonify(inventory.serialize()), status.HTTP_201_CREATED, {"Location": location_url}
    )

################################################################################
# DELETE
################################################################################
@app.route("/inventory/<int:product_id>/condition/<string:condition>", methods=["DELETE"])
def delete_inventory(product_id, condition):
    """Deletes an inventory with the given product_id and condition"""
    app.logger.info("Request to delete inventory with key ({}, {})"\
                    .format(product_id, condition))
    inventory = Inventory.find(product_id, condition)
    if inventory:
        inventory.delete()
    app.logger.info("Inventory with product_id {} and condition {} deleted"
                    .format(product_id, condition))
    return make_response("", status.HTTP_204_NO_CONTENT)

################################################################################
# PUT
################################################################################
@app.route("/inventory/<int:product_id>/condition/<string:condition>", methods=["PUT"])
def update_inventory(product_id, condition):
    """
    Regular Update
    Updates the inventory with the given product_id and condition
    """
    app.logger.info("Request to update inventory with key ({}, {})"\
                    .format(product_id, condition))
    check_content_type("application/json")
    inventory = Inventory.find(product_id, condition)
    if not inventory:
        return not_found("Inventory with ({}, {})".format(product_id, condition))

    resp_old = inventory.serialize()
    resp_new = request.get_json()
    for key in resp_old.keys():
        if key in resp_new:
            resp_old[key] = resp_new[key]

    if inventory.quantity == 0:
        inventory.available = 0

    inventory.deserialize(resp_old)
    inventory.validate_data()
    inventory.update()
    app.logger.info("Inventory ({}, {}) updated.".format(product_id, condition))
    return make_response(jsonify(inventory.serialize()), status.HTTP_200_OK)

@app.route("/inventory/<int:product_id>/condition/<string:condition>/restock", methods=["PUT"])
def update_inventory_restock(product_id, condition):
    """- Given the product_id, condition and amount (body) this updates quantity += amount"""
    app.logger.info("Request to update inventory with key ({}, {})"\
                    .format(product_id, condition))

    # Checking for Content-Type
    check_content_type("application/json")

    # Checking for 'amount' keyword
    json = request.get_json()
    print(json.keys())
    if "amount" not in json.keys():
        return bad_request("Invalid data: Amount missing")

    # Checking for amount >= 0
    amount = json['amount']
    if amount<0:
        return forbidden("Invalid data: Amount <= 0")

    # If there is no matching inventory
    inventory = Inventory.find(product_id, condition)
    if not inventory:
        return not_found("Inventory with ({}, {})".format(product_id, condition))

    inventory.quantity += amount

    inventory.validate_data()
    inventory.update()
    app.logger.info("Inventory ({}, {}) updated.".format(product_id, condition))
    return make_response(jsonify(inventory.serialize()), status.HTTP_200_OK)

@app.route("/inventory/<int:product_id>/condition/<string:condition>/activate", methods=["PUT"])
def update_inventory_activate(product_id, condition):
    """Given the product_id and condition this updates available = 1"""
    app.logger.info("Request to update inventory with key ({}, {})"\
                    .format(product_id, condition))
    inventory = Inventory.find(product_id, condition)
    if not inventory:
        return not_found("Inventory with ({}, {})".format(product_id, condition))

    if inventory.quantity == 0:
        return forbidden("This product is currently out of stock and cannot be made available")
    inventory.available = 1

    inventory.validate_data()
    inventory.update()
    app.logger.info("Inventory ({}, {}) updated.".format(product_id, condition))
    return make_response(jsonify(inventory.serialize()), status.HTTP_200_OK)

@app.route("/inventory/<int:product_id>/condition/<string:condition>/deactivate", methods=["PUT"])
def update_inventory_deactivate(product_id, condition):
    """Given the product_id and condition this updates available = 0"""
    app.logger.info("Request to update inventory with key ({}, {})"\
                    .format(product_id, condition))
    inventory = Inventory.find(product_id, condition)
    if not inventory:
        return not_found("Inventory with ({}, {})".format(product_id, condition))

    inventory.available = 0
    inventory.validate_data()
    inventory.update()
    app.logger.info("Inventory ({}, {}) updated.".format(product_id, condition))
    return make_response(jsonify(inventory.serialize()), status.HTTP_200_OK)

################################################################################
#  U T I L I T Y   F U N C T I O N S
################################################################################
def init_db():
    """ Initialies the SQLAlchemy app """
    # global app
    Inventory.init_db(app)

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers["Content-Type"] == content_type:
        return
    app.logger.error("Invalid Content-Type: {}".format(request.headers["Content-Type"]))
    abort(415, "Content-Type must be {}".format(content_type))
