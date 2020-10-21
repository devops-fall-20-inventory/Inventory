"""
Package: APP

Package for the application model and services
This module also sets up the logging to be used with gunicorn
"""
import os
import logging
from flask import Flask

# Create Flask application
APP = Flask(__name__)
APP.config.from_object("config")

# Import the service After the Flask APP is created
from service import service, model

# Set up logging for production
print("Setting up logging for {}...".format(__name__))
APP.logger.propagate = False
if __name__ != "__main__":
    GUNICORN_LOGGER = logging.getLogger("gunicorn.error")
    if GUNICORN_LOGGER:
        APP.logger.handlers = GUNICORN_LOGGER.handlers
        APP.logger.setLevel(GUNICORN_LOGGER.level)
    APP.logger.info("Logging established")

APP.logger.info(70 * "*")
APP.logger.info("  I N V E N T O R Y   S T O R E   S E R V I C E  ".center(70, "*"))
APP.logger.info(70 * "*")

# make our sqlalchemy tables
service.init_db()

APP.logger.info("Service inititalized!")
