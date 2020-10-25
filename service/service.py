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

# import os
# import sys
# import logging
from flask import jsonify, request, url_for, make_response, abort
from flask_api import status  # HTTP Status Codes
# from werkzeug.exceptions import NotFound
# from werkzeug.exceptions import BadRequest
# from flask_sqlalchemy import SQLAlchemy
# import service.model as model
from service.model import Inventory, DataValidationError

# Import Flask application
from . import APP

DEMO_MSG = "Inventory Demo REST API Service"
PERMISSION = True

################################################################################
# Error Handlers
################################################################################
@APP.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    return bad_request(error)

@APP.errorhandler(status.HTTP_400_BAD_REQUEST)
def bad_request(error):
    """ Handles bad reuests with 400_BAD_REQUEST """
    message = str(error)
    APP.logger.warning(message)
    return (
        jsonify(
            status=status.HTTP_400_BAD_REQUEST, error="Bad Request", message=message
        ),
        status.HTTP_400_BAD_REQUEST,
    )

@APP.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """ Handles resources not found with 404_NOT_FOUND """
    message = str(error)
    APP.logger.warning(message)
    return (
        jsonify(status=status.HTTP_404_NOT_FOUND, error="Not Found", message=message),
        status.HTTP_404_NOT_FOUND,
    )

@APP.errorhandler(status.HTTP_403_FORBIDDEN)
def forbidden(error):
    """
    Handles resources that cant be modified with 403 FORBIDDEN
    Eg : changes that result in stock level to be less than zero
    """
    message = str(error)
    APP.logger.warning(message)
    return (
        jsonify(status=status.HTTP_403_FORBIDDEN, error="Forbidden", message=message),
        status.HTTP_403_FORBIDDEN,
    )

@APP.errorhandler(status.HTTP_405_METHOD_NOT_ALLOWED)
def method_not_supported(error):
    """ Handles unsuppoted HTTP methods with 405_METHOD_NOT_SUPPORTED """
    message = str(error)
    APP.logger.warning(message)
    return (
        jsonify(
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
            error="Method not Allowed",
            message=message,
        ),
        status.HTTP_405_METHOD_NOT_ALLOWED,
    )

@APP.errorhandler(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
def mediatype_not_supported(error):
    """ Handles unsuppoted media requests with 415_UNSUPPORTED_MEDIA_TYPE """
    message = str(error)
    APP.logger.warning(message)
    return (
        jsonify(
            status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            error="Unsupported media type",
            message=message,
        ),
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
    )

@APP.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """ Handles unexpected server error with 500_SERVER_ERROR """
    message = str(error)
    APP.logger.error(message)
    return (
        jsonify(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="Internal Server Error",
            message=message,
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

@APP.errorhandler(status.HTTP_409_CONFLICT)
def create_conflict_error(error):
    """ Handles CREATE conflicts error with HTTP_409_CONFLICT """
    message = str(error)
    APP.logger.error(message)
    return (
        jsonify(
            status=status.HTTP_409_CONFLICT,
            error="Conflict 409 Error",
            message=message,
        ),
        status.HTTP_409_CONFLICT,
    )

################################################################################
# INDEX
################################################################################
@APP.route("/")
def index():
    """ Root URL response """
    APP.logger.info("Request for Root URL")
    return (
        jsonify(
            name=DEMO_MSG,
            version="1.0",
            paths=url_for("list_inventories", _external=True),
        ),
        status.HTTP_200_OK,
    )

################################################################################
# GET
################################################################################
@APP.route("/inventory", methods=["GET"])
def list_inventories():
    """
    Returns a list of all inventories in the inventory
    GET /inventory
    """
    APP.logger.info("A GET request for ALL inventories")
    inventories = []
    params = request.args
    if len(params) > 0:
        pid = params.get("product_id")
        if pid:
            inventories = Inventory.find_by_product_id(pid)
        else:
            return method_not_supported("Invalid request parameters: missing (product_id)")
    else:
        inventories = Inventory.all()

    results = []
    for inv in inventories:
        json = inv.serialize()
        if json['available'] == 1:
            results.append(json)

    if len(results) == 0:
        return not_found("Inventories were not found for this permission")
    APP.logger.info("Returning {} inventories for this permission type".format(len(results)))
    return make_response(jsonify(results), status.HTTP_200_OK)

@APP.route("/inventory/<int:product_id>/condition/<string:condition>", methods=["GET"])
def get_inventory_by_pid_condition(product_id, condition):
    """
    Returns the inventory with the given product_id and condition
    GET /inventory/<int:product_id>/condition/<string:condition>
    """
    APP.logger.info("A GET request for inventories with product_id {} and condition {}"\
                    .format(product_id, condition))
    inventory = Inventory.find(product_id, condition)
    if (not inventory) or\
        (inventory and PERMISSION is False and inventory.serialize()['available'] == 0):
        return not_found("Inventory ({}, {})".format(product_id, condition))
    APP.logger.info("Return inventory with product_id {} and condition {}"\
                    .format(product_id, condition))
    return make_response(jsonify([inventory.serialize()]), status.HTTP_200_OK)

################################################################################
# POST
################################################################################
@APP.route("/inventory", methods=["POST"])
def create_inventory():
    """
    Creates a new inventory in the Inventory DB based the data in the body
    POST /inventory
    """
    APP.logger.info("Request to create an Inventory record")
    check_content_type("application/json")
    if not PERMISSION:
        return bad_request("You do not have permissions to CREATE")
    json = request.get_json()
    inventory = Inventory()
    inventory.deserialize(json)
    inventory.validate_data()

    if Inventory.find(json['product_id'], json['condition']):
        return create_conflict_error("The Record you're trying to create already exists!")
    else:
        inventory.create()
        location_url = url_for("get_inventory_by_pid_condition",\
            product_id=inventory.product_id, condition=inventory.condition, _external=True)
        APP.logger.info("Inventory ({}, {}) created."\
                        .format(inventory.product_id, inventory.condition))
        return make_response(
            jsonify(inventory.serialize()), status.HTTP_201_CREATED, {"Location": location_url}
        )

################################################################################
# DELETE
################################################################################
@APP.route("/inventory/<int:product_id>/condition/<string:condition>", methods=["DELETE"])
def delete_inventory(product_id, condition):
    """Deletes an inventory with the given product_id and condition"""
    if not PERMISSION:
        return bad_request("You do not have permissions to DELETE")
    APP.logger.info("Request to delete inventory with key ({}, {})"\
                    .format(product_id, condition))
    inventory = Inventory.find(product_id, condition)
    if inventory:
        inventory.delete()
    APP.logger.info("Inventory with product_id {} and condition {} deleted"
                    .format(product_id, condition))
    return make_response("", status.HTTP_204_NO_CONTENT)

################################################################################
# PUT
################################################################################
@APP.route("/inventory/<int:product_id>/condition/<string:condition>", methods=["PUT"])
def update_inventory(product_id, condition):
    """
    Regular Update
    Updates the inventory with the given product_id and condition
    """
    if not PERMISSION:
        return bad_request("You do not have permissions to UPDATE")
    APP.logger.info("Request to update inventory with key ({}, {})"\
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
    APP.logger.info("Inventory ({}, {}) updated.".format(product_id, condition))
    return make_response(jsonify(inventory.serialize()), status.HTTP_200_OK)

@APP.route("/inventory/<int:product_id>/condition/<string:condition>/restock", methods=["PUT"])
def update_inventory_restock(product_id, condition):
    """- Given the product_id, condition and amount (body) this updates quantity += amount"""
    if not PERMISSION:
        return bad_request("You do not have permissions to RESTOCK")
    APP.logger.info("Request to update inventory with key ({}, {})"\
                    .format(product_id, condition))
    check_content_type("application/json")
    inventory = Inventory.find(product_id, condition)
    if not inventory:
        return not_found("Inventory with ({}, {})".format(product_id, condition))

    json = request.get_json()
    if "amount" not in json.keys():
        return bad_request("Invalid data: Amount missing")
    amount = json['amount']
    if inventory.quantity + amount > inventory.quantity:
        inventory.quantity += amount
    else:
        return forbidden("Invalid data: Amount <= 0")

    inventory.validate_data()
    inventory.update()
    APP.logger.info("Inventory ({}, {}) updated.".format(product_id, condition))
    return make_response(jsonify(inventory.serialize()), status.HTTP_200_OK)

@APP.route("/inventory/<int:product_id>/condition/<string:condition>/activate", methods=["PUT"])
def update_inventory_activate(product_id, condition):
    """Given the product_id and condition this updates available = 1"""
    if not PERMISSION:
        return bad_request("You do not have permissions to ACTIVATE")
    APP.logger.info("Request to update inventory with key ({}, {})"\
                    .format(product_id, condition))
    inventory = Inventory.find(product_id, condition)
    if not inventory:
        return not_found("Inventory with ({}, {})".format(product_id, condition))

    if inventory.quantity == 0:
        return forbidden("This product is currently out of stock and cannot be made available")
    else:
        inventory.available = 1

    inventory.validate_data()
    inventory.update()
    APP.logger.info("Inventory ({}, {}) updated.".format(product_id, condition))
    return make_response(jsonify(inventory.serialize()), status.HTTP_200_OK)

@APP.route("/inventory/<int:product_id>/condition/<string:condition>/deactivate", methods=["PUT"])
def update_inventory_deactivate(product_id, condition):
    """Given the product_id and condition this updates available = 0"""
    if not PERMISSION:
        return bad_request("You do not have permissions to DEACTIVATE")
    APP.logger.info("Request to update inventory with key ({}, {})"\
                    .format(product_id, condition))
    inventory = Inventory.find(product_id, condition)
    if not inventory:
        return not_found("Inventory with ({}, {})".format(product_id, condition))

    inventory.available = 0
    inventory.validate_data()
    inventory.update()
    APP.logger.info("Inventory ({}, {}) updated.".format(product_id, condition))
    return make_response(jsonify(inventory.serialize()), status.HTTP_200_OK)

################################################################################
#  U T I L I T Y   F U N C T I O N S
################################################################################
def init_db():
    """ Initialies the SQLAlchemy APP """
    # global APP
    Inventory.init_db(APP)

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers["Content-Type"] == content_type:
        return
    APP.logger.error("Invalid Content-Type: {}".format(request.headers["Content-Type"]))
    abort(415, "Content-Type must be {}".format(content_type))

def set_permissions(perm):
    """ Sets the Permission """
    global PERMISSION
    PERMISSION = perm
