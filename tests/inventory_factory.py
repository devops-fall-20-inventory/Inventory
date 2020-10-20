"""
Test Factory to make fake objects for testing
"""
import factory
import factory.fuzzy as fuzzy
import service.model as models
from service.model import Inventory

test_data_file = "data_to_test.csv"

""" Creates fake inventories that you don't have to feed """
class InventoryFactory(factory.Factory):

    class Meta:
        model = Inventory

    product_id = factory.Sequence(lambda n: n)
    condition = fuzzy.FuzzyChoice(choices=models.CONDITIONS)
    quantity = fuzzy.FuzzyInteger(models.QTY_LOW,models.QTY_HIGH,models.QTY_STEP)
    restock_level = fuzzy.FuzzyInteger(models.QTY_LOW,models.RESTOCK_LVL,models.QTY_STEP)
    available = fuzzy.FuzzyChoice(choices=[models.AVAILABLE_TRUE, models.AVAILABLE_FALSE])

    ######################################################################
    ## Helper
    ######################################################################
    @staticmethod
    def get_data(type=models.ATTR_DEFAULT):
        """
        This extracts command line arguments
        """
        if len(sys.argv)<model.MAX_ATTR+1:
            return None,None,None,None,None
        elif type==models.ATTR_DEFAULT or len(sys.argv)>models.MAX_ATTR:
            pid = sys.argv[models.ATTR_PRODUCT_ID]
            cnd = sys.argv[models.ATTR_CONDITION]
            qty = sys.argv[models.ATTR_QUANTITY]
            lvl = sys.argv[models.ATTR_RESTOCK_LEVEL]
            avl = sys.argv[models.ATTR_AVAILABLE]
            return pid,cnd,qty,lvl,avl
        else:
            sys.argv[type]

    @staticmethod
    def read_test_data():
        """
        Read data for test cases into test_data
        """
        data = []
        global test_data_file
        try:
            fr = open("/vagrant/tests/data_to_test.csv",'r')
            line = fr.readline()
            # row  = line.strip().split(',')
            # if row[0]:
                # data.append(row)
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
