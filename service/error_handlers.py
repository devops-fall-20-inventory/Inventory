"""
Error handlers

Handles all of the HTTP Error Codes as JSON
"""

from flask_api import status  # HTTP Status Codes
from flask import jsonify
from service.model import DataValidationError, DBError
from . import app

################################################################################
# Error Handlers
################################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    return bad_request(error)

@app.errorhandler(DBError)
def db_connection_error(error):
    """ Handles unsuccessful DB connectivity errors """
    return internal_server_error(error)

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

@app.errorhandler(status.HTTP_403_FORBIDDEN)
def forbidden(error):
    """
    Handles resources that cant be modified with 403 FORBIDDEN
    Eg : changes that result in stock level to be less than zero
    """
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(status=status.HTTP_403_FORBIDDEN, error="Forbidden", message=message),
        status.HTTP_403_FORBIDDEN,
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

@app.errorhandler(status.HTTP_409_CONFLICT)
def create_conflict_error(error):
    """ Handles CREATE conflicts error with HTTP_409_CONFLICT """
    message = str(error)
    app.logger.error(message)
    return (
        jsonify(
            status=status.HTTP_409_CONFLICT,
            error="Conflict 409 Error",
            message=message,
        ),
        status.HTTP_409_CONFLICT,
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
