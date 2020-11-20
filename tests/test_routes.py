"""
Inventory API Service Test Suite
Test cases can be run with the following:
"""
import os
import sys
import logging
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

    def test_create_errors(self):
        """ Testing Create Error: [DataValidationError] """
        data = {
            keys.KEY_PID: 666,
            keys.KEY_CND: "hellow",
            keys.KEY_QTY: 1,
            keys.KEY_LVL: 1,
            keys.KEY_AVL: 1
        }
        resp = self.app.post(
            "/api/inventory", json=data, content_type=keys.KEY_CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

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
        resp = self.app.get("/api/inventory")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.get_json()), 0)

    def test_get_inventory_by_product_id(self):
        """Get inventory details by [product_id]"""
        N = 10
        count = 0
        inventories = self._create_inventories(N)
        for inv in inventories:
            resp = self.app.get("/api/inventory?product_id={}".format(inv.product_id))
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            count += len(resp.get_json())
        self.assertEqual(count, N)

    def test_get_inventory_by_product_id_not_found(self):
        """Get inventory details by [product_id]: NOT FOUND"""
        resp = self.app.get("/api/inventory?product_id=0")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.get_json()), 0)

        test_inventory = self._create_inventories(1)[0]
        resp = self.app.get("/api/inventory?product_id={}".format(test_inventory.product_id+3))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.get_json()), 0)

    def test_get_inventory_by_condition(self):
        """Get inventory details by [condition]"""
        count_new = 0
        count_used = 0
        count_open = 0
        inventories = self._create_inventories(10)
        for inv in inventories:
            if inv.condition == "new":
                count_new += 1
            elif inv.condition == "used":
                count_used += 1
            elif inv.condition == "open box":
                count_open += 1

        resp = self.app.get("/api/inventory?condition=new")
        if resp.status_code == status.HTTP_200_OK:
            count = len(resp.get_json())
            self.assertEqual(count, count_new)

        resp = self.app.get("/api/inventory?condition=used")
        if resp.status_code == status.HTTP_200_OK:
            count = len(resp.get_json())
            self.assertEqual(count, count_used)

        resp = self.app.get("/api/inventory?condition=open box")
        if resp.status_code == status.HTTP_200_OK:
            count = len(resp.get_json())
            self.assertEqual(count, count_open)

    def test_get_inventory_by_quantity(self):
        """Get inventory details by [quantity]"""
        N = 10
        count = 0
        inventories = self._create_inventories(N)
        quantities = [inv.quantity for inv in inventories]
        mn = min(quantities)
        resp = self.app.get("/api/inventory?quantity={}".format(mn))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        count = len(resp.get_json())
        self.assertEqual(count, N)

    def test_get_inventory_by_available(self):
        """Get inventory details by [available]"""
        N = 10
        n_0 = 0
        n_1 = 0
        count_0 = 0
        count_1 = 0
        inventories = self._create_inventories(N)
        for inv in inventories:
            if inv.available == 0:
                n_0 += 1
            elif inv.available == 1:
                n_1 += 1
        self.assertEqual(n_0+n_1, N)

        resp = self.app.get("/api/inventory?available=0")
        if resp.status_code == status.HTTP_200_OK:
            count_0 = len(resp.get_json())
            self.assertEqual(count_0, n_0)
            
        resp = self.app.get("/api/inventory?available=1")
        if resp.status_code == status.HTTP_200_OK:
            count_1 = len(resp.get_json())
            self.assertEqual(count_1, n_1)

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

    def test_get_inventory_by_pid_condition_not_found(self):
        """Get inventory details by [product_id, condition]: NOT FOUND"""
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

    def test_update_errors(self):
        """ Testing Update Error: [DataValidationError] """
        test_inventory = InventoryFactory()
        resp = self.app.post(
            "/api/inventory", json=test_inventory.serialize(), content_type=keys.KEY_CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = {
            keys.KEY_PID: test_inventory.product_id,
            keys.KEY_CND: test_inventory.condition,
            keys.KEY_QTY: "-12",
            keys.KEY_LVL: 1,
            keys.KEY_AVL: 1
        }
        resp = self.app.put(
                "/api/inventory/{}/condition/{}".format(test_inventory.product_id, test_inventory.condition),
                json=data,
                content_type=keys.KEY_CONTENT_TYPE_JSON,
            )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            keys.KEY_AMT: "-helo"
        }
        resp = self.app.put(
                "/api/inventory/{}/condition/{}/restock".format(test_inventory.product_id, test_inventory.condition),
                json=data,
                content_type=keys.KEY_CONTENT_TYPE_JSON,
            )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
