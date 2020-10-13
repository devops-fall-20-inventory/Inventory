"""
Test cases for Inventory Model

"""
import logging
import unittest
import os
from service.models import YourResourceModel, DataValidationError, db

######################################################################
#  Inventory Model test cases
######################################################################
class TestYourResourceModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        pass

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        pass

    def setUp(self):
        """ This runs before each test """
        pass

    def tearDown(self):
        """ This runs after each test """
        pass

######################################################################
#  P L A C E   T E S T   C A S E S   H E R E
######################################################################

    def test_XXXX(self):
        """ Test something """
        self.assertTrue(True)
