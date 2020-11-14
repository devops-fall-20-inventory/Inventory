"""
Inventory Error Handlers Test Suite
1. 400
2.
"""
import os
import sys
from unittest import TestCase
from flask_api import status

sys.path.append("..")
from service.model import DB
from service import app, routes, keys
from service.error_handlers import method_not_supported, internal_server_error

DATABASE_URI = os.getenv(keys.KEY_DB_URI, keys.DATABASE_URI_LOCAL)

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
        app.config[keys.KEY_SQL_ALC] = DATABASE_URI
        routes.init_db()

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

    def test_415(self):
        """Testing HTTP_415_UNSUPPORTED_MEDIA_TYPE error"""
        resp = self.app.post("/inventory", json="", content_type="text")
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_500(self):
        """Testing HTTP_500_INTERNAL_SERVER_ERROR error"""
        try:
            1/0
        except Exception:
            return internal_server_error("Testing 500")
