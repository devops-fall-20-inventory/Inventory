"""
Inventory API Service Test Suite
Test cases can be run with the following:
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch

from werkzeug import test
from werkzeug.wrappers import Response
from flask_api import status  # HTTP Status Codes
from service import APP, service
from service.service import APP, init_db
from service.model import Inventory, DataValidationError, DB
from .inventory_factory import InventoryFactory

DATABASE_URI = os.getenv("DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres")

class InventoryAPITest(TestCase):
    """ Inventory Services Tests """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        APP.debug = False
        APP.testing = True
        # Set up the test database
        APP.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI

    @classmethod
    def tearDownClass(cls):
        """ Run once after all tests """
        pass

    def setUp(self):
        """ Runs before each test """
        init_db()
        DB.drop_all()  # clean up the last tests
        DB.create_all()  # create new tables
        self.APP = APP.test_client()

    def tearDown(self):
        DB.session.remove()
        DB.drop_all()

######################################################################
#  T E S T   C A S E S
######################################################################

    def test_index(self):
        """ Test the Home Page """
        resp = self.APP.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], service.DEMO_MSG)

    def _create_inventories(self, count):
        """ Factory method to create inventory products in bulk """
        inventories = []
        for _ in range(count):
            test_inventory = InventoryFactory()
            resp = self.APP.post(
                "/inventory", json=test_inventory.serialize(), content_type="application/json"
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test inventory"
            )
            new_inventory = resp.get_json()
            test_inventory.product_id = new_inventory["product_id"]
            inventories.append(test_inventory)
        return inventories

    ##################################################################
    # Testing POST
    def test_create_inventory(self):
        """ Create a new inventory """
        test_inventory = InventoryFactory()
        resp = self.APP.post(
            "/inventory", json=test_inventory.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertTrue(location != None)

        # Check the data is correct
        new_inventory = resp.get_json()
        self.assertTrue(new_inventory != None)
        self.assertEqual(new_inventory["product_id"],
            test_inventory.serialize()['product_id'], "Product ID does not match")
        self.assertEqual(new_inventory["quantity"],
            test_inventory.serialize()['quantity'], "Quantity does not match")
        self.assertEqual(new_inventory["restock_level"],
            test_inventory.serialize()['restock_level'], "Restock level does not match")
        self.assertEqual(new_inventory["available"],
            test_inventory.serialize()['available'], "Availability does not match")
        self.assertEqual(new_inventory["condition"],
            test_inventory.serialize()['condition'], "Conditions do not match")

        # Check that the location header was correct
        resp = self.APP.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_inventory = resp.get_json()
        self.assertTrue(new_inventory != None)
        self.assertEqual(new_inventory["product_id"], test_inventory.serialize()['product_id'], "Product ID does not match")
        self.assertEqual(new_inventory["quantity"], test_inventory.serialize()['quantity'], "Quantity does not match")
        self.assertEqual(new_inventory["restock_level"], test_inventory.serialize()['restock_level'], "Restock level does not match")
        self.assertEqual(new_inventory["available"], test_inventory.serialize()['available'], "Availability does not match")
        self.assertEqual(new_inventory["condition"], test_inventory.serialize()['condition'], "Conditions do not match")

    ##################################################################
    # Testing GET
    def test_list_inventory(self):
        """Get the entire inventory list"""
        self._create_inventories(5)
        resp = self.APP.get("/inventory")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_get_inventory_not_found(self):
        """Get a product inventory that's not available"""
        resp = self.APP.get("/inventory/0/test")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_inventory_by_pid(self):
        """Get inventory details ONLY by product_id"""
        inventories = self._create_inventories(10)
        test_pid = inventories[0].product_id
        pid_inventories = [inventory for inventory in inventories if inventory.product_id == test_pid]
        resp = self.APP.get("/inventory/{}".format(test_pid), content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(pid_inventories))
        for inventory in data:
            self.assertEqual(inventory["product_id"], test_pid)

    def test_get_inventory_by_pid_2(self):
        """Get inventory details ONLY by product_id"""
        test_inventory = self._create_inventories(1)[0]
        # resp = self.APP.post(
        #     "/inventory", json=test_inventory.serialize(), content_type="application/json"
        # )
        # self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # new_inventory = resp.get_json()
        pid = test_inventory["product_id"]
        resp = self.APP.get("/inventory/{}".format(pid+3), content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_inventory_by_pid_condition(self):
        """Get a single inventory by {product_id, condition}"""
        test_inventory = self._create_inventories(1)[0]
        resp = self.APP.get(
            "/inventory/{}/condition/{}".format(
            test_inventory.product_id, test_inventory.condition),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["product_id"], test_inventory.product_id)
        self.assertEqual(data["condition"], test_inventory.condition)

    ##################################################################
    # Testing PUT
    def test_update_inventory(self):
        """Update an existing product in  Inventory"""
        test_inventory = InventoryFactory()
        resp = self.APP.post(
            "/inventory", json=test_inventory.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the pet
        new_inventory = resp.get_json()
        new_inventory["quantity"] = 9999
        resp = self.APP.put(
            "/inventory/{}/{}".format(new_inventory["product_id"], new_inventory["condition"]),
            json=new_inventory,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_inventory = resp.get_json()
        self.assertEqual(updated_inventory["quantity"], 9999)

    def test_update_inventory_2(self):
        """Update an existing product in  Inventory"""
        test_inventory = InventoryFactory()
        resp = self.APP.post(
            "/inventory", json=test_inventory.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the pet
        new_inventory = resp.get_json()
        new_inventory["quantity"] = 9999
        resp = self.APP.put(
            "/inventory/{}/{}".format(new_inventory["product_id"]+4, new_inventory["condition"]),
            json=new_inventory,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    #
    # def test_update_stock_quantity(self):
    #     """Update stock quantity for a given product in Inventory"""
    #     test_inventory = InventoryFactory()
    #     resp = self.APP.post(
    #         "/inventory", json=test_inventory.serialize(), content_type="application/json"
    #     )
    #     new_inventory = resp.get_json()
    #     self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
    #     resp = self.APP.put("/inventory/{}/{}/sub/{}".format(new_inventory["product_id"],new_inventory["condition"],new_inventory["quantity"]))
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)
    #
    # def test_update_stock_quantity_2(self):
    #     """Update stock quantity for a given product in Inventory"""
    #     test_inventory = InventoryFactory()
    #     resp = self.APP.post(
    #         "/inventory", json=test_inventory.serialize(), content_type="application/json"
    #     )
    #     new_inventory = resp.get_json()
    #     self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
    #     resp = self.APP.put("/inventory/{}/{}/sub/{}".format(new_inventory["product_id"],new_inventory["condition"],new_inventory["quantity"]+1))
    #     self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
    #
    # def test_update_stock_quantity_3(self):
    #     """Update stock quantity for a given product in Inventory"""
    #     test_inventory = InventoryFactory()
    #     resp = self.APP.post(
    #         "/inventory", json=test_inventory.serialize(), content_type="application/json"
    #     )
    #     new_inventory = resp.get_json()
    #     self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
    #     resp = self.APP.put("/inventory/{}/{}/add/{}".format(new_inventory["product_id"],new_inventory["condition"],new_inventory["quantity"]))
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)
    #
    # def test_update_stock_quantity_4(self):
    #     """Update stock quantity for a given product in Inventory"""
    #     test_inventory = InventoryFactory()
    #     resp = self.APP.post(
    #         "/inventory", json=test_inventory.serialize(), content_type="application/json"
    #     )
    #     new_inventory = resp.get_json()
    #     self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
    #     resp = self.APP.put("/inventory/{}/{}/sub/{}".format(new_inventory["product_id"],new_inventory["condition"],new_inventory["quantity"]-8))
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)
    #
    # def test_update_stock_quantity_5(self):
    #     """Update stock quantity for a given product in Inventory"""
    #     test_inventory = InventoryFactory()
    #     resp = self.APP.post(
    #         "/inventory", json=test_inventory.serialize(), content_type="application/json"
    #     )
    #     new_inventory = resp.get_json()
    #     self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
    #     resp = self.APP.put("/inventory/{}/{}/sub/0".format(new_inventory["product_id"],new_inventory["condition"]))
    #     self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
    #
    # def test_update_stock_quantity_6(self):
    #     """Update stock quantity for a given product in Inventory"""
    #     test_inventory = InventoryFactory()
    #     resp = self.APP.post(
    #         "/inventory", json=test_inventory.serialize(), content_type="application/json"
    #     )
    #     new_inventory = resp.get_json()
    #     self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
    #     resp = self.APP.put("/inventory/{}/{}/sub/0".format(new_inventory["product_id"],new_inventory["condition"]))
    #     self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
    #
    # def test_update_stock_quantity_7(self):
    #     """Update stock quantity for a given product in Inventory"""
    #     test_inventory = InventoryFactory()
    #     resp = self.APP.post(
    #         "/inventory", json=test_inventory.serialize(), content_type="application/json"
    #     )
    #     new_inventory = resp.get_json()
    #     self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
    #     resp = self.APP.put("/inventory/{}/{}/subh/5".format(new_inventory["product_id"],new_inventory["condition"]))
    #     self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
    #
    # def test_update_stock_quantity_8(self):
    #     """Update stock quantity for a given product in Inventory"""
    #     test_inventory = InventoryFactory()
    #     resp = self.APP.post(
    #         "/inventory", json=test_inventory.serialize(), content_type="application/json"
    #     )
    #     new_inventory = resp.get_json()
    #     self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
    #     resp = self.APP.put("/inventory/{}/{}/add/5".format(new_inventory["product_id"]+4,new_inventory["condition"]))
    #     self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
    #
    # def test_update_availability(self):
    #     """Update an existing product's availability in the inventory"""
    #     test_inventory = InventoryFactory()
    #     resp = self.APP.post(
    #         "/inventory", json=test_inventory.serialize(), content_type="application/json"
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
    #
    #     new_inventory = resp.get_json()
    #     new_inventory["available"] = 0
    #     resp = self.APP.put(
    #         "/inventory/{}/{}".format(new_inventory["product_id"], new_inventory["condition"]),
    #         json=new_inventory,
    #         content_type="application/json",
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)
    #     final_inventory = resp.get_json()
    #     self.assertEqual(final_inventory["available"], 0, "The available parameter is not what was expected")

    ##################################################################
    # Testing DELETE
    def test_delete_inventory(self):
        """Delete a product from the inventory"""
        test_inventory = self._create_inventories(1)[0]
        resp = self.APP.delete(
            "/inventory/{}/{}".format(test_inventory.product_id, test_inventory.condition), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.APP.get(
            "/inventory/{}/{}".format(test_inventory.product_id, test_inventory.condition), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    ##################################################################
    def test_wrong_content_type(self):
        """trigger wrong content type error"""
        test_inventory = InventoryFactory()
        resp = self.APP.post("/inventory", json=test_inventory.serialize(), content_type="text")
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    @patch('service.service.create_inventory')
    def test_bad_request(self, bad_request_mock):
        """ Bad Request error from Create Inventory """
        bad_request_mock.side_effect = DataValidationError()
        resp = self.APP.post('/inventory', json="",
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
