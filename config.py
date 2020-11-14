import os
import logging
from service import keys

# Get configuration from environment
DATABASE_URI = os.getenv(
    keys.KEY_DB_URI,
    keys.DATABASE_URI_LOCAL
)

# Configure SQLAlchemy
SQLALCHEMY_DATABASE_URI = DATABASE_URI
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Secret for session management
SECRET_KEY = os.getenv(keys.KET_SECRET, "sup3r-s3cr3t")
LOGGING_LEVEL = logging.INFO
