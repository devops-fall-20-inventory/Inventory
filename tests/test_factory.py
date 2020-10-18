"""
Test Factory to make fake objects for testing
"""
import factory
import factory.fuzzy as fuzzy
import service.model as models
from service.model import Inventory

""" Creates fake inventories that you don't have to feed """
class InventoryFactory(factory.Factory):

    class Meta:
        model = Inventory

    product_id = factory.Sequence(lambda n: n)
    condition = fuzzy.FuzzyChoice(choices=["new", "used", "open box"])
    quantity = fuzzy.FuzzyInteger(models.QTY_LOW,models.QTY_HIGH,models.QTY_STEP)
    restock_level = fuzzy.FuzzyInteger(models.QTY_LOW,models.RESTOCK_LVL,models.QTY_STEP)
    available = fuzzy.FuzzyChoice(choices=[models.AVAILABLE_TRUE, models.AVAILABLE_FALSE])

if __name__ == "__main__":
    for _ in range(10):
        inventory = InventoryFactory()
        print(inventory.serialize())
        print(inventory.deserialize())
        print(inventory.create())
