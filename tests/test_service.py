"""
Inventory API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from flask_api import status  # HTTP Status Codes
from service import app
import service.service as service
from service.service import app, init_db
from service.model import Inventory, DataValidationError, db
from .inventory_factory import InventoryFactory

DATABASE_URI = os.getenv("DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres")

######################################################################
#  T E S T   C A S E S
######################################################################
class InventoryAPITest(TestCase):
    """ Inventory REST API Services Tests """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        app.debug = False
        app.testing = True
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI

    @classmethod
    def tearDownClass(cls):
        """ Run once after all tests """
        pass

    def setUp(self):
        """ Runs before each test """
        init_db()
        db.drop_all()  # clean up the last tests
        db.create_all()  # create new tables
        self.app = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

######################################################################
#  T E S T   C A S E S
######################################################################

    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], service.DEMO_MSG)

    def test_create_inventory(self):
        """ Create a new inventory """
        test_inventory = InventoryFactory()
        resp = self.app.post(
            "/inventory", json=test_inventory.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertTrue(location != None)

        # Check the data is correct
        new_inventory = resp.get_json()
        self.assertTrue(new_inventory != None)
        self.assertEqual(new_inventory["quantity"], test_inventory.serialize()['quantity'], "Quantity does not match")
        self.assertEqual(new_inventory["restock_level"], test_inventory.serialize()['restock_level'], "Restock level does not match")
        self.assertEqual(new_inventory["available"], test_inventory.serialize()['available'], "Availability does not match")
        self.assertEqual(new_inventory["condition"], test_inventory.serialize()['condition'], "Conditions do not match")

        # Check that the location header was correct
        resp = self.app.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_inventory = resp.get_json()
        if new_inventory != None:
            self.assertTrue(new_inventory != None)
            self.assertEqual(new_inventory["quantity"], test_inventory.serialize()['quantity'], "Quantity does not match")
            self.assertEqual(new_inventory["restock_level"], test_inventory.serialize()['restock_level'], "Restock level does not match")
            self.assertEqual(new_inventory["available"], test_inventory.serialize()['available'], "Availability does not match")
            self.assertEqual(new_inventory["condition"], test_inventory.serialize()['condition'], "Conditions do not match")

    # -
    def _create_inventories(self, count):
        """ Factory method to create inventories in bulk """
        inventories = []
        for _ in range(count):
            test_inventory = InventoryFactory()
            resp = self.app.post(
                "/inventory", json=test_inventory.serialize(), content_type="application/json"
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test inventory"
            )
            new_inventory = resp.get_json()
            test_inventory.product_id = new_inventory["product_id"]
            inventories.append(test_inventory)
        return inventories
