"""
Test Factory to make fake objects for testing
"""
import sys
import factory
import factory.fuzzy as fuzzy
from service import keys
from service.model import Inventory

test_data_file = "data_to_test.csv"

""" Creates fake inventories that you don't have to feed """
class InventoryFactory(factory.Factory):

    class Meta:
        model = Inventory

    product_id = factory.Sequence(lambda n: n)
    condition = fuzzy.FuzzyChoice(choices=keys.CONDITIONS)
    quantity = fuzzy.FuzzyInteger(keys.QTY_LOW,keys.QTY_HIGH,keys.QTY_STEP)
    restock_level = fuzzy.FuzzyInteger(keys.QTY_LOW,keys.RESTOCK_LVL,keys.QTY_STEP)
    available = fuzzy.FuzzyChoice(choices=[keys.AVAILABLE_TRUE, keys.AVAILABLE_FALSE])

    ######################################################################
    ## Helper
    ######################################################################
    @staticmethod
    def get_data(type=keys.ATTR_DEFAULT):
        """
        This extracts command line arguments
        """
        if len(sys.argv)<keys.MAX_ATTR+1:
            return None,None,None,None,None
        if type==keys.ATTR_DEFAULT or len(sys.argv)>keys.MAX_ATTR:
            pid = sys.argv[keys.ATTR_PRODUCT_ID]
            cnd = sys.argv[keys.ATTR_CONDITION]
            qty = sys.argv[keys.ATTR_QUANTITY]
            lvl = sys.argv[keys.ATTR_RESTOCK_LEVEL]
            avl = sys.argv[keys.ATTR_AVAILABLE]
            return pid,cnd,qty,lvl,avl
        sys.argv[type]

    @staticmethod
    def read_test_data():
        """
        Read data for test cases into test_data
        """
        data = []
        global test_data_file
        try:
            fr = open("./tests/data_to_test.csv",'r')
            line = fr.readline()
            while line:
                line = fr.readline()
                row  = line.strip().split(',')
                if row[0]:
                    data.append(row)
            fr.close()
        except IOError as err:
            print(err)
        finally:
            return data

if __name__ == "__main__":
    for _ in range(10):
        inventory = InventoryFactory()
