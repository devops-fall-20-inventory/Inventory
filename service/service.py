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
    return "Some information about the inventory service", status.HTTP_200_OK

################################################################################
# RETRIEVE A RECORD
################################################################################
@app.route("/inventory/<int:product_id>", methods=["GET"])
def get_inventory(product_id):
    """Returns the inventory with the given product_id"""
    return "Some information about the inventory service", status.HTTP_200_OK

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
    location_url = url_for("get_inventory", product_id=inventory.product_id, _external=True)

    app.logger.info("Inventory with Product ID [%s] created.", inventory.product_id)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )


################################################################################
# UPDATE AN EXISTING RECORD
################################################################################
@app.route("/inventory/<int:product_id>", methods=["PUT"])
def update_inventory(product_id):
    """Updates the inventory with the given product_id"""
    return "Some information about the inventory service", status.HTTP_200_OK

################################################################################
# DELETE A RECORD
################################################################################
@app.route("/inventory/<int:product_id>", methods=["DELETE"])
def delete_inventory(product_id):
    """Deletes a inventory with the given product_id"""
    return "Some information about the inventory service", status.HTTP_204_OK

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
