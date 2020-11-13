"""
Inventory Error Handlers Test Suite
1. 400
2.
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch

from werkzeug import test
from werkzeug.wrappers import Response
from flask_api import status
from service import app, service, error_handlers
from service.service import app, init_db
from service.model import Inventory, DataValidationError, DB, DBError
from service.error_handlers import method_not_supported, internal_server_error
from .inventory_factory import InventoryFactory

DATABASE_URI = os.getenv("DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres")

class InventoryErrTest(TestCase):
    """
    ######################################################################
    Inventory Error Handlers Tests
    ######################################################################
    """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        app.debug = False
        app.testing = True
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        init_db()

    @classmethod
    def tearDownClass(cls):
        """ Run once after all tests """
        DB.session.close()

    def setUp(self):
        """ Runs before each test """
        DB.drop_all()  # clean up the last tests
        DB.create_all()  # create new tables
        self.app = app.test_client()

    def tearDown(self):
        DB.session.remove()
        DB.drop_all()

######################################################################
#  T E S T   C A S E S
######################################################################

    def test_405(self):
        """Testing HTTP_405_METHOD_NOT_ALLOWED error"""
        return method_not_supported("Testing 405")

    @patch('service.service.create_inventory')
    def test_415(self, mock_415):
        """Testing HTTP_415_UNSUPPORTED_MEDIA_TYPE error"""
        resp = self.app.post("/inventory", json="", content_type="text")
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_500(self):
        """Testing HTTP_500_INTERNAL_SERVER_ERROR error"""
        try:
            r = 1/0
        except Exception:
            return internal_server_error("Testing 500")
