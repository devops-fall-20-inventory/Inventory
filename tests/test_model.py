"""
Test cases for Inventory Model

"""
import os
import sys
import csv
import logging
import unittest
from service import app
import service.model as model
from service.model import Inventory, DataValidationError, db
from .inventory_factory import InventoryFactory

DATABASE_URI = os.getenv("DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres")

################################################################################
#  Inventory Model test cases
################################################################################
class InventoryTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """ These run once before Test suite """
        app.debug = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI

    @classmethod
    def tearDownClass(cls):
        """ These run once after Test suite """
        pass

    def setUp(self):
        Inventory.init_db(app)
        db.drop_all()  # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_repr(self):
        """ Test Inventory __repr__ """
        pid = 1234567
        inventory = Inventory(product_id=pid)
        msg = inventory.__repr__()

    ######################################################################
    ## Utility
    ######################################################################
    #
    def test_serialize(self):
        """ Test serialization of a Inventory """
        # pid = 1234567
        # cnd = "new"
        # qty = 4
        # lvl = 3
        # avl = 1
        data = InventoryFactory.read_test_data()
        self.assertIsNot(data, None)
        self.assertTrue(len(data)>0)
        for row in data:
            if len(row)<model.MAX_ATTR:
                continue
            self.call_serialize(int(row[0]),row[1],int(row[2]),int(row[3]),int(row[4]),int(row[5]))

    def call_serialize(self,pid,cnd,qty,lvl,avl,err):
        inventory = Inventory(product_id=pid, condition=cnd, quantity=qty, restock_level=lvl, available=avl)
        if err==1:
            self.assertRaises(DataValidationError, inventory.validate_data)
        data = inventory.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("product_id", data)
        self.assertEqual(data["product_id"], pid)
        self.assertIn("condition", data)
        self.assertEqual(data["condition"], cnd)
        self.assertIn("quantity", data)
        self.assertEqual(data["quantity"], qty)
        self.assertIn("restock_level", data)
        self.assertEqual(data["restock_level"], lvl)
        self.assertIn("available", data)
        self.assertEqual(data["available"], avl)

    #
    def test_deserialize(self):
        """ Test deserialization of a Inventory """
        data = InventoryFactory.read_test_data()
        self.assertIsNot(data, None)
        self.assertTrue(len(data)>0)
        for row in data:
            if len(row)<model.MAX_ATTR:
                continue
            self.call_deserialize(int(row[0]),row[1],int(row[2]),int(row[3]),int(row[4]),int(row[5]))

    def call_deserialize(self,pid,cnd,qty,lvl,avl,err):
        data = {
            "product_id"    : pid,
            "condition"     : cnd,
            "quantity"      : qty,
            "restock_level" : lvl,
            "available"     : avl
        }
        inventory = Inventory()
        inventory.deserialize(data)
        self.assertNotEqual(inventory, None)
        self.assertEqual(inventory.product_id, pid)
        self.assertEqual(inventory.condition, cnd)
        self.assertEqual(inventory.quantity, qty)
        self.assertEqual(inventory.restock_level, lvl)
        self.assertEqual(inventory.available, avl)

    def test_deserialize_bad_data(self):
        """ Test deserialization of bad data """
        data = "this is not a dictionary"
        inventory = Inventory()
        self.assertRaises(DataValidationError, inventory.deserialize, data)
        data = {}
        self.assertRaises(DataValidationError, inventory.deserialize, data)

    def test_validate_data(self):
        """ Testing validate_data_xxx """
        self.call_validate_data(1234567,"new",4,3,1,True)
        self.call_validate_data(-1234567,"new1",-1,-1,-1,False)

    def call_validate_data(self,pid,cnd,qty,lvl,avl,res):
        inventory = Inventory(product_id=pid, condition=cnd, quantity=qty, restock_level=lvl, available=avl)
        self.assertTrue(inventory != None)
        res_pid = inventory.validate_data_product_id()
        self.assertEqual(res_pid,res)
        res_cnd = inventory.validate_data_condition()
        self.assertEqual(res_cnd,res)
        res_qty = inventory.validate_data_quantity()
        self.assertEqual(res_qty,res)
        res_lvl = inventory.validate_data_restock_level()
        self.assertEqual(res_lvl,res)
        res_avl = inventory.validate_data_available()
        self.assertEqual(res_avl,res)
        try:
            err = inventory.validate_data()
        except DataValidationError as err:
            print(err)

    def read_test_data(self):
        """
        Read data for test cases into test_data
        """
        data = InventoryFactory.read_test_data()
        self.assertIsNot(data, None)
        self.assertTrue(len(data)>0)
        for row in data:
            print(row)

    ######################################################################
    ## Database
    ######################################################################
    # 
    def test_create(self):
        """ Create a inventory and assert that it exists """
        data = InventoryFactory.read_test_data()
        self.assertIsNot(data, None)
        self.assertTrue(len(data)>0)
        for row in data:
            if len(row)<model.MAX_ATTR:
                continue
            self.call_create(int(row[0]),row[1],int(row[2]),int(row[3]),int(row[4]),int(row[5]))

    def call_create(self,pid,cnd,qty,lvl,avl,err):
        inventory = Inventory(product_id=pid, condition=cnd, quantity=qty, restock_level=lvl, available=avl)
        if err==1:
            self.assertRaises(DataValidationError, inventory.validate_data)
        inventory.create()
        self.assertTrue(inventory != None)
        self.assertEqual(inventory.product_id, pid)
        self.assertEqual(inventory.condition, cnd)
        self.assertEqual(inventory.quantity, qty)
        self.assertEqual(inventory.restock_level, lvl)
        self.assertEqual(inventory.available, avl)

    #
    def test_update(self):
        """Update an Inventory"""
        inventory = Inventory(product_id=123456, condition="new", quantity=1, restock_level=10, available=1)
        inventory.create()
        inventory.product_id = 1234567
        inventory.update()
        inventories = Inventory.all()
        self.assertEqual(len(inventories), 1)
        self.assertEqual(inventories[0].product_id, 1234567)

    #
    def test_delete(self):
        """Delete an Inventory"""
        inventory = Inventory(product_id=123456, condition="new", quantity=1, restock_level=10, available=1)
        inventory.create()
        self.assertEqual(len(Inventory.all()), 1)
        inventory.delete()
        self.assertEqual(len(Inventory.all()), 0)

    #
    def test_find(self):
        """Find an Inventory by product_id and condition"""
        Inventory(product_id=123456, condition="new", quantity=1, restock_level=10, available=1).create()
        inventory = Inventory(product_id=1234567, condition="new", quantity=1, restock_level=10, available=0)
        inventory.create()
        result = Inventory.find(inventory.product_id, inventory.condition)
        self.assertIsNot(result, None)
        self.assertEqual(result.product_id, 1234567)
        self.assertEqual(result.condition, "new")
        self.assertEqual(result.quantity, 1)
        self.assertEqual(result.restock_level, 10)
        self.assertEqual(result.available, 0)

    #
    def test_find_or_404(self):
        Inventory(product_id=123456, condition="new", quantity=1, restock_level=10, available=1).create()
        inventory = Inventory(product_id=1234567, condition="new", quantity=1, restock_level=10, available=0)
        inventory.create()
        result = Inventory.find_or_404(inventory.product_id, inventory.condition)
        self.assertIsNot(result, None)
        self.assertEqual(result.product_id, 1234567)
        self.assertEqual(result.condition, "new")
        self.assertEqual(result.quantity, 1)
        self.assertEqual(result.restock_level, 10)
        self.assertEqual(result.available, 0)

    #
    def test_find_by_product_id(self):
        Inventory(product_id=123456, condition="new", quantity=1, restock_level=10, available=1).create()
        Inventory(product_id=1234567, condition="used", quantity=2, restock_level=20, available=0).create()
        inventories = Inventory.find_by_product_id(1234567)
        self.assertEqual(inventories[0].product_id, 1234567)
        self.assertEqual(inventories[0].condition, "used")
        self.assertEqual(inventories[0].quantity, 2)
        self.assertEqual(inventories[0].restock_level, 20)
        self.assertEqual(inventories[0].available, 0)

######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    unittest.main()
