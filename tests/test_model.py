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

DATABASE_URI = os.getenv("DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres")
test_data = []
test_data_file = "data_to_test.csv"

################################################################################
#  Inventory Model test cases
################################################################################
class InventoryTest(unittest.TestCase):

    ######################################################################
    ## Utility
    ######################################################################
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

    def test_inventory_serialize(self):
        """ Test serialization of a Inventory """
        # pid,cnd,qty,lvl,avl = InventoryTest.get_data()
        global test_data
        global test_data_file
        if test_data and len(test_data)==0:
            test_data = InventoryTest.read_test_data(test_data_file)
        for row in test_data:
            if not row or len(row)<model.MAX_ATTR:
                continue;
            pid = row[0]
            cnd = row[1]
            qty = row[2]
            lvl = row[3]
            avl = row[4]
            self.assertRaises(DataValidationError, Inventory.validate_data, pid,cnd,qty,lvl,avl)
            inventory = Inventory(product_id=pid, condition=cnd, quantity=qty, restock_level=lvl, available=avl)
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

    def test_inventory_deserialize(self):
        """ Test deserialization of a Inventory """
        # pid,cnd,qty,lvl,avl = InventoryTest.get_data()
        global test_data
        global test_data_file
        if test_data and len(test_data)==0:
            test_data = InventoryTest.read_test_data(test_data_file)
        for row in test_data:
            if not row or len(row)<model.MAX_ATTR:
                continue;
            pid = row[0]
            cnd = row[1]
            qty = row[2]
            lvl = row[3]
            avl = row[4]
            self.assertRaises(DataValidationError, Inventory.validate_data, pid,cnd,qty,lvl,avl)
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

    def test_inventory_deserialize_bad_data(self):
        """ Test deserialization of bad data """
        data = "this is not a dictionary"
        inventory = Inventory()
        self.assertRaises(DataValidationError, inventory.deserialize, data)

    ######################################################################
    ## Database
    ######################################################################
    def test_inventory_create(self):
        """ Create a inventory and assert that it exists """
        # pid,cnd,qty,lvl,avl = InventoryTest.get_data()
        global test_data
        global test_data_file
        if test_data and len(test_data)==0:
            test_data = InventoryTest.read_test_data(test_data_file)
        for row in test_data:
            if not row or len(row)<model.MAX_ATTR:
                continue;
            pid = row[0]
            cnd = row[1]
            qty = row[2]
            lvl = row[3]
            avl = row[4]
            self.assertRaises(DataValidationError, Inventory.validate_data, pid,cnd,qty,lvl,avl)
            inventory = Inventory(product_id=pid, condition=cnd, quantity=qty, restock_level=lvl, available=avl)
            inventory.create()
            self.assertTrue(inventory != None)
            self.assertEqual(inventory.product_id, pid)
            self.assertEqual(inventory.condition, cnd)
            self.assertEqual(inventory.quantity, qty)
            self.assertEqual(inventory.restock_level, lvl)
            self.assertEqual(inventory.available, avl)

    ######################################################################
    ## Helper
    ######################################################################
    @staticmethod
    def get_data(type=model.ATTR_DEFAULT):
        if len(sys.argv)<model.MAX_ATTR+1:
            return None,None,None,None,None
        elif type==model.ATTR_DEFAULT or len(sys.argv)>model.MAX_ATTR:
            pid = sys.argv[model.ATTR_PRODUCT_ID]
            cnd = sys.argv[model.ATTR_CONDITION]
            qty = sys.argv[model.ATTR_QUANTITY]
            lvl = sys.argv[model.ATTR_RESTOCK_LEVEL]
            avl = sys.argv[model.ATTR_AVAILABLE]
            return pid,cnd,qty,lvl,avl
        else:
            sys.argv[type]

    # Reading test cases from file
    @staticmethod
    def read_test_data(file=test_data_file):
        """
        Read data for test cases into test_data
        """
        data = []
        try:
            fr = open(file,'r')
            line = fr.readline()
            row  = line.strip().split(',')
            data.append(row)
            while line:
                line = fr.readline()
                row  = line.strip().split(',')
                data.append(row)
            fr.close()
            return data
        except IOError as err:
            print(err)
        finally:
            return data

    @staticmethod
    def get_product_data():
        with open(test_data_file, delimiter=',') as csvfile:
            reader = csv.DictReader(csvfile)
            print(reader)

######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    unittest.main()
