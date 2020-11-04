import os
import logging

# Get configuration from environment
# DATABASE_URI = "sqlite:///../db/development.db"
DATABASE_URI = os.getenv(
    "DATABASE_URI",
    "postgres://ajtoutzb:tDCcFv3UZ6PCbucbzCFFPOsFYAbaIman@echo.db.elephantsql.com:5432/ajtoutzb"
)

# Configure SQLAlchemy
SQLALCHEMY_DATABASE_URI = DATABASE_URI
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Secret for session management
SECRET_KEY = os.getenv("SECRET_KEY", "sup3r-s3cr3t")
LOGGING_LEVEL = logging.INFO
