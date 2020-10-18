"""
Inventory Service

Paths:

------

GET /inventory - Returns a list of all inventories in the inventory
GET /inventory/{product_id} - Returns the inventory record with the given product_id
POST /inventory - Creates a new inventory record in the inventory
PUT /inventory/{product_id} - Updates the inventory record with the given product_id
DELETE /inventory/{product_id} - Deletes an inventory record with the given product_id
"""

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from flask_api import status  # HTTP Status Codes
from werkzeug.exceptions import NotFound
from flask_sqlalchemy import SQLAlchemy
from service.model import Inventory, DataValidationError

# Import Flask application
from . import app

DEMO_MSG = "Inventory Demo REST API Service"

################################################################################
# Error Handlers
################################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    return bad_request(error)

@app.errorhandler(status.HTTP_400_BAD_REQUEST)
def bad_request(error):
    """ Handles bad reuests with 400_BAD_REQUEST """
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(
            status=status.HTTP_400_BAD_REQUEST, error="Bad Request", message=message
        ),
        status.HTTP_400_BAD_REQUEST,
    )

@app.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """ Handles resources not found with 404_NOT_FOUND """
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(status=status.HTTP_404_NOT_FOUND, error="Not Found", message=message),
        status.HTTP_404_NOT_FOUND,
    )

@app.errorhandler(status.HTTP_405_METHOD_NOT_ALLOWED)
def method_not_supported(error):
    """ Handles unsuppoted HTTP methods with 405_METHOD_NOT_SUPPORTED """
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
            error="Method not Allowed",
            message=message,
        ),
        status.HTTP_405_METHOD_NOT_ALLOWED,
    )

@app.errorhandler(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
def mediatype_not_supported(error):
    """ Handles unsuppoted media requests with 415_UNSUPPORTED_MEDIA_TYPE """
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(
            status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            error="Unsupported media type",
            message=message,
        ),
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
    )

@app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """ Handles unexpected server error with 500_SERVER_ERROR """
    message = str(error)
    app.logger.error(message)
    return (
        jsonify(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="Internal Server Error",
            message=message,
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

################################################################################
# GET INDEX
################################################################################
@app.route("/")
def index():
    """ Root URL response """
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name=DEMO_MSG,
            version="1.0",
            paths=url_for("list_inventories", _external=True),
        ),
        status.HTTP_200_OK,
    )

################################################################################
# LIST ALL RECORDS
################################################################################
@app.route("/inventory", methods=["GET"])
def list_inventories():
    """Returns a list of all inventories in the inventory"""
    app.logger.info("Request for all inventories")
    inventories = Inventory.all()
    results = [inventory.serialize() for inventory in inventories]

    app.logger.info("Returning %d inventories", len(results))
    return make_response(jsonify(results), status.HTTP_200_OK)

################################################################################
# RETRIEVE A RECORD
################################################################################
@app.route("/inventory/<int:product_id>/<string:condition>", methods=["GET"])
def get_inventory(product_id, condition):
    """Returns the inventory with the given product_id and condition"""
    app.logger.info("Request for inventory with product_id %d and condition %s", product_id, condition)
    inventory = Inventory.find(product_id, condition)
    if not inventory:
        raise NotFound("Inventory with product_id {} and condition {} was not found".format(product_id, condition))

    app.logger.info("Return inventory with product_id: %d and condition %s", product_id, condition)
    return make_response(jsonify(inventory.serialize()), status.HTTP_200_OK)

################################################################################
# RETRIEVE RECORDS OF A PRODUCT ID
################################################################################
@app.route("/inventory/<int:product_id>", methods=["GET"])
def get_inventory_by_pid(product_id):
    """Returns the inventories with the given product_id"""
    app.logger.info("Request for inventories with product_id %d", product_id)
    inventories = Inventory.find_by_product_id(product_id)
    if not inventories:
        raise NotFound("Inventories with product_id {} were not found".format(product_id))
    results = [inventory.serialize() for inventory in inventories]

    app.logger.info("Return %d inventories with product_id: %d", len(results), product_id)
    return make_response(jsonify(results), status.HTTP_200_OK)

################################################################################
# CREATE A NEW RECORD
################################################################################
@app.route("/inventory", methods=["POST"])
def create_inventory():
    """
    Creates a new inventory in the Inventory DB
    Based the data in the body that is posted
    """
    app.logger.info("Request to create an Inventory record")
    check_content_type("application/json")
    inventory = Inventory()
    inventory.deserialize(request.get_json())
    inventory.create()
    message = inventory.serialize()
    location_url = url_for("get_inventory", product_id=inventory.product_id, condition=inventory.condition, _external=True)

    app.logger.info("Inventory with Product ID [%d] created.", inventory.product_id)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )


################################################################################
# UPDATE AN EXISTING RECORD
################################################################################
@app.route("/inventory/<int:product_id>/<string:condition>", methods=["PUT"])
def update_inventory(product_id, condition):
    """Updates the inventory with the given product_id and condition"""
    app.logger.info("Request to update inventory with product_id: %d and condition: %s", product_id, condition)
    check_content_type("application/json")
    inventory = Inventory.find(product_id, condition)
    if not inventory:
        raise NotFound("Inventory with product_id {} and condition {} was not found.".format(product_id, condition))
    inventory.deserialize(request.get_json())
    inventory.update()

    app.logger.info("Inventory with product_id %d and condition %s updated.", product_id, condition)
    return make_response(jsonify(inventory.serialize()), status.HTTP_200_OK)


################################################################################
# DELETE A RECORD
################################################################################
@app.route("/inventory/<int:product_id>/<string:condition>", methods=["DELETE"])
def delete_inventory(product_id, condition):
    """Deletes an inventory with the given product_id and condition"""
    app.logger.info("Request to delete inventory with product_id %d and condition %s", product_id, condition)
    inventory = Inventory.find(product_id, condition)
    if inventory:
        inventory.delete()

    app.logger.info("Inventory with product_id %d and condition %s deleted", product_id, condition)
    return make_response("", status.HTTP_204_NO_CONTENT)

################################################################################
#  U T I L I T Y   F U N C T I O N S
################################################################################
def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Inventory.init_db(app)

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers["Content-Type"] == content_type:
        return
    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(415, "Content-Type must be {}".format(content_type))
