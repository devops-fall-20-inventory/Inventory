"""
Package: app

Package for the application model and services
This module also sets up the logging to be used with gunicorn
"""
import os
import logging
from flask import Flask

# Create Flask application
app = Flask(__name__)
app.config.from_object("config")

# Import the service After the Flask app is created
from service import service, model

# Set up logging for production
print("Setting up logging for {}...".format(__name__))
app.logger.propagate = False
if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    if gunicorn_logger:
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)
    app.logger.info("Logging established")

app.logger.info(70 * "*")
app.logger.info("  I N V E N T O R Y   S T O R E   S E R V I C E  ".center(70, "*"))
app.logger.info(70 * "*")

# make our sqlalchemy tables
service.init_db()

app.logger.info("Service inititalized!")
