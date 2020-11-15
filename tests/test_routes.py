"""
Inventory API Service Test Suite
Test cases can be run with the following:
"""
import os
import sys
from unittest import TestCase
from flask_api import status

from service import app, routes, keys
from service.model import Inventory, DB
from .inventory_factory import InventoryFactory

DATABASE_URI = os.getenv(keys.KEY_DB_URI, keys.DATABASE_URI_LOCAL)

class InventoryAPITest(TestCase):
    """
    ######################################################################
    Inventory Routes Tests
    ######################################################################
    """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        app.debug = True
        app.testing = True
        api_key = routes.generate_apikey()
        app.config[keys.KEY_API] = api_key
        app.config[keys.KEY_SQL_ALC] = DATABASE_URI
        routes.init_db()

    @classmethod
    def tearDownClass(cls):
        """ Run once after all tests """
        DB.session.close()

    def setUp(self):
        """ Runs before each test """
        self.app = app.test_client()
        self.headers = {
            'X-Api-Key': app.config[keys.KEY_API]
        }
        DB.drop_all()  # clean up the last tests
        DB.create_all()  # create new tables

    def tearDown(self):
        DB.session.remove()
        DB.drop_all()

######################################################################
#  T E S T   C A S E S
######################################################################
    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # self.assertIn(key.INV_TITLE, str(resp.data))

    def _create_inventories(self, count):
        """ Factory method to create inventory products in bulk """
        inventories = []
        for _ in range(count):
            test_inventory = InventoryFactory()
            resp = self.app.post(
                "/api/inventory", json=test_inventory.serialize(),
                content_type=keys.KEY_CONTENT_TYPE_JSON
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Created inventory record"
            )
            new_inventory = resp.get_json()
            test_inventory.product_id = new_inventory[keys.KEY_PID]
            inventories.append(test_inventory)
        return inventories

    ##################################################################
    # Testing POST
    def test_create_inventory(self):
        """ Create a new inventory """
        test_inventory = InventoryFactory()
        resp = self.app.post(
            "/api/inventory", json=test_inventory.serialize(), content_type=keys.KEY_CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertTrue(location is not None)

        # Check the data is correct
        new_inventory = resp.get_json()
        self.assertTrue(new_inventory is not None)
        self.assertEqual(new_inventory[keys.KEY_PID],
            test_inventory.serialize()[keys.KEY_PID], "Product ID does not match")
        self.assertEqual(new_inventory[keys.KEY_QTY],
            test_inventory.serialize()[keys.KEY_QTY], "Quantity does not match")
        self.assertEqual(new_inventory[keys.KEY_LVL],
            test_inventory.serialize()[keys.KEY_LVL], "Restock level does not match")
        self.assertEqual(new_inventory[keys.KEY_AVL],
            test_inventory.serialize()[keys.KEY_AVL], "Availability does not match")
        self.assertEqual(new_inventory[keys.KEY_CND],
            test_inventory.serialize()[keys.KEY_CND], "Conditions do not match")

        # Check that the location header was correct
        resp = self.app.get(location, content_type=keys.KEY_CONTENT_TYPE_JSON)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_inventory = resp.get_json()
        self.assertTrue(new_inventory is not None)
        self.assertEqual(new_inventory[keys.KEY_PID],
            test_inventory.serialize()[keys.KEY_PID], "Product ID does not match")
        self.assertEqual(new_inventory[keys.KEY_QTY],
            test_inventory.serialize()[keys.KEY_QTY], "Quantity does not match")
        self.assertEqual(new_inventory[keys.KEY_LVL],
            test_inventory.serialize()[keys.KEY_LVL], "Restock level does not match")
        self.assertEqual(new_inventory[keys.KEY_AVL],
            test_inventory.serialize()[keys.KEY_AVL], "Availability does not match")
        self.assertEqual(new_inventory[keys.KEY_CND],
            test_inventory.serialize()[keys.KEY_CND], "Conditions do not match")

    def test_create_inventory_bad_req(self):
        """ Create a new inventory WITHOUT condition """
        test_inventory = InventoryFactory()
        json = test_inventory.serialize()
        json.pop(keys.KEY_CND)
        resp = self.app.post(
            "/api/inventory", data=json, content_type=keys.KEY_CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_inventory_dup(self):
        """ Create a DUPLICATE inventory record """
        test_inventory = InventoryFactory()
        json = test_inventory.serialize()
        resp = self.app.post(
            "/api/inventory", json=json, content_type=keys.KEY_CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        resp = self.app.post(
            "/api/inventory", json=json, content_type=keys.KEY_CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    ##################################################################
    # Testing GET
    def test_list_inventory(self):
        """Get the entire inventory list"""
        N = 10
        inventories = self._create_inventories(N)
        resp = self.app.get("/api/inventory")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_list_inventory_not_found(self):
        """Get the entire inventory list"""
        N = 10
        resp = self.app.get("/api/inventory")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_inventory_not_found(self):
        """Get a product inventory that's not available"""
        resp = self.app.get("/api/inventory?product_id=0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_inventory_by_pid(self):
        """Get inventory details by [product_id]"""
        inventories = self._create_inventories(10)
        for inv in inventories:
            test_pid = inv.product_id
            resp = self.app.get("/api/inventory?product_id={}".format(test_pid))
            self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_inventory_by_pid_2(self):
        """Get inventory details by [product_id] 2"""
        test_inventory = self._create_inventories(1)[0]
        pid = test_inventory.product_id
        resp = self.app.get("/api/inventory?product_id={}".format(pid+3))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_inventory_by_pid_condition(self):
        """Get inventory details by [product_id, condition]"""
        test_inventory = self._create_inventories(1)[0]
        pid = test_inventory.product_id
        cnd = test_inventory.condition
        resp = self.app.get("/api/inventory/{}/condition/{}".format(pid, cnd))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data[keys.KEY_PID], pid)
        self.assertEqual(data[keys.KEY_CND], cnd)

    def test_get_inventory_by_pid_condition_404(self):
        """Get inventory details by [product_id, condition] 404"""
        test_inventory = self._create_inventories(1)[0]
        resp = self.app.get("/api/inventory/{}/condition/{}".format(999, "new"),\
                            content_type=keys.KEY_CONTENT_TYPE_JSON)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    ##################################################################
    # Testing DELETE
    def test_delete_inventory(self):
        """Delete a product from the inventory"""
        test_inventory = self._create_inventories(1)[0]
        resp = self.app.delete(
            "/api/inventory/{}/condition/{}".format(test_inventory.product_id,
                    test_inventory.condition), content_type=keys.KEY_CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    ##################################################################
    # Testing PUT
    def test_update_inventory(self):
        """Update an existing product in Inventory - 1"""
        test_inventory = InventoryFactory()
        resp = self.app.post(
            "/api/inventory", json=test_inventory.serialize(), content_type=keys.KEY_CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        qty = 30
        new_inventory = resp.get_json()
        new_inventory[keys.KEY_QTY] = qty
        resp = self.app.put(
            "/api/inventory/{}/condition/{}".format(new_inventory[keys.KEY_PID],
            new_inventory[keys.KEY_CND]),
            json=new_inventory,
            content_type=keys.KEY_CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_inventory = resp.get_json()
        self.assertEqual(updated_inventory[keys.KEY_QTY], qty)

    def test_update_inventory_2(self):
        """Update an existing product in Inventory - 2"""
        test_inventory = InventoryFactory()
        resp = self.app.post(
            "/api/inventory", json=test_inventory.serialize(), content_type=keys.KEY_CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        new_inventory = resp.get_json()
        new_inventory[keys.KEY_QTY] = 30
        resp = self.app.put(
            "/api/inventory/{}/condition/{}".format(new_inventory[keys.KEY_PID]+4,
            new_inventory[keys.KEY_CND]),
            json=new_inventory,
            content_type=keys.KEY_CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_inventory_activate(self):
        """Activate an existing Inventory"""
        quantities = [0,1]
        for qty in quantities:
            test_inventory = InventoryFactory()
            test_inventory.quantity = qty
            resp = self.app.post(
                "/api/inventory", json=test_inventory.serialize(),
                content_type=keys.KEY_CONTENT_TYPE_JSON
            )
            new_inventory = resp.get_json()
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
            resp = self.app.put(
                "/api/inventory/{}/condition/{}/activate".format(new_inventory[keys.KEY_PID],
                new_inventory[keys.KEY_CND])
            )
            self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_update_inventory_deactivate(self):
        """Deactivate an existing Inventory"""
        test_inventory = InventoryFactory()
        resp = self.app.post(
            "/api/inventory", json=test_inventory.serialize(), content_type=keys.KEY_CONTENT_TYPE_JSON
        )
        new_inventory = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        resp = self.app.put(
            "/api/inventory/{}/condition/{}/deactivate".format(new_inventory[keys.KEY_PID],
            new_inventory[keys.KEY_CND])
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_update_inventory_restock(self):
        """Restock an inventory's Quantity"""
        test_inventory = InventoryFactory()
        resp = self.app.post(
            "/api/inventory", json=test_inventory.serialize(), content_type=keys.KEY_CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        new_inventory = resp.get_json()
        body = {}
        amounts = [-1,0,1,2,3]
        for a in amounts:
            key = keys.KEY_AMT
            if a >= 2:
                key = keys.KEY_AMT+'y'
                if keys.KEY_AMT in body:
                    del body[keys.KEY_AMT]
            body[key] = a
            resp = self.app.put(
                "/api/inventory/{}/condition/{}/restock".format(new_inventory[keys.KEY_PID],
                new_inventory[keys.KEY_CND]),
                json=body,
                content_type=keys.KEY_CONTENT_TYPE_JSON,
            )



            if a <= 0 or key != keys.KEY_AMT:
                self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            else:
                self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_updates_not_found(self):
        """Testing Updates NOT found"""
        pid = 9999
        cnd = "new"
        resp = self.app.put(
                "/api/inventory/{}/condition/{}".format(pid, cnd),
                json={},
                content_type=keys.KEY_CONTENT_TYPE_JSON,
            )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        resp = self.app.put(
                "/api/inventory/{}/condition/{}/restock".format(pid, cnd),
                json={keys.KEY_AMT:0},
                content_type=keys.KEY_CONTENT_TYPE_JSON,
            )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        resp = self.app.put(
                "/api/inventory/{}/condition/{}/activate".format(pid, cnd),
            )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        resp = self.app.put(
                "/api/inventory/{}/condition/{}/deactivate".format(pid, cnd),
            )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
