"""
Models for Inventory
All of the models are stored in this module
"""
import logging
from flask_sqlalchemy import SQLAlchemy

LOGGER = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
DB = SQLAlchemy()

# Constants
CONDITIONS = ["new", "used", "open box"]
AVAILABLE_TRUE = 1
AVAILABLE_FALSE = 0
QTY_LOW = 0
QTY_HIGH = 50
QTY_STEP = 1
RESTOCK_LVL = 5
MAX_ATTR = 5

ATTR_DEFAULT = 0
ATTR_PRODUCT_ID = 1
ATTR_CONDITION = 2
ATTR_QUANTITY = 3
ATTR_RESTOCK_LEVEL = 4
ATTR_AVAILABLE = 5

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

################################################################################
class Inventory(DB.Model):
    """
    Inventory Model class
    """
    app = None

    # Table Schema
    product_id = DB.Column(DB.Integer, primary_key=True)
    condition = DB.Column(DB.String(100), primary_key=True)
    quantity = DB.Column(DB.Integer)
    restock_level = DB.Column(DB.Integer)
    available = DB.Column(DB.Integer)

    def __repr__(self):
        return "<<product_id %d>" % (self.product_id)

    ######################################################################
    # UTILITY
    def serialize(self):
        """ Serializes an Inventory record into a dictionary """
        return {
            "product_id": self.product_id,
            "quantity": self.quantity,
            "restock_level": self.restock_level,
            "condition": self.condition,
            "available": self.available
        }

    # Args: data (dict): A dictionary containing the resource data
    def deserialize(self, data):
        """ Deserializes an Inventory record from a dictionary """
        try:
            self.product_id = data["product_id"]
            self.quantity = data["quantity"]
            self.restock_level = data["restock_level"]
            self.condition = data["condition"]
            self.available = data["available"]
        except KeyError as error:
            raise DataValidationError("Invalid Inventory record: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError("Invalid Inventory record: body contained bad or no data")
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        LOGGER.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        DB.init_app(app)
        app.app_context().push()
        DB.create_all()  # make our sqlalchemy tables

    ######################################################################
    def validate_data(self):
        """
        VALIDATING DATA FORMATS
        """
        args = []

        res_pid = self.validate_data_product_id()
        if not res_pid:
            args.append(ATTR_PRODUCT_ID)

        res_cnd = self.validate_data_condition()
        if not res_cnd:
            args.append(ATTR_CONDITION)

        res_qty = self.validate_data_quantity()
        if not res_qty:
            args.append(ATTR_QUANTITY)

        res_lvl = self.validate_data_restock_level()
        if not res_lvl:
            args.append(ATTR_RESTOCK_LEVEL)

        res_avl = self.validate_data_available()
        if not res_avl:
            args.append(ATTR_AVAILABLE)

        if not (res_pid and res_cnd and res_qty and res_lvl and res_avl):
            msg = "Error in data arguments: {}".format(args)
            raise DataValidationError(msg)
        return True

    def validate_data_product_id(self):
        """
        Validating Product ID format
        """
        pid = self.product_id
        return isinstance(pid, int) and pid > 0

    def validate_data_condition(self):
        """
        validating Condition format
        """
        cnd = self.condition
        return isinstance(cnd, str) and cnd.lower() in CONDITIONS

    def validate_data_quantity(self):
        """
        Validating Quantity format
        """
        qty = self.quantity
        return isinstance(qty, int) and (qty > 0 and qty <= QTY_HIGH)

    def validate_data_restock_level(self):
        """
        Validating Restock level format
        """
        lvl = self.restock_level
        return isinstance(lvl, int) and (lvl > 0 and lvl <= RESTOCK_LVL)

    def validate_data_available(self):
        """
        Validating Available format
        """
        avl = self.available
        return isinstance(avl, type(AVAILABLE_TRUE)) and avl in [AVAILABLE_TRUE, AVAILABLE_FALSE]

    ######################################################################
    def create(self):
        """
        Creates an Inventory record to the database
        """
        LOGGER.info("Creating %d", self.product_id)
        DB.session.add(self)
        DB.session.commit()

    ######################################################################
    def update(self):
        """
        Updates an Inventory record to the database
        """
        LOGGER.info("Saving %d", self.product_id)
        DB.session.commit()

    ######################################################################
    def delete(self):
        """ Removes an Inventory record from the data store """
        LOGGER.info("Deleting %d", self.product_id)
        DB.session.delete(self)
        DB.session.commit()

    ######################################################################
    @classmethod
    def all(cls):
        """ Returns all of the Inventory records in the database """
        LOGGER.info("Processing all Inventory records")
        return cls.query.all()

    #
    @classmethod
    def find(cls, pid, condition):
        """ Finds an Inventory record by its product_id and condition """
        LOGGER.info("Processing lookup for product_id %d and condition %s ", pid, condition)
        return cls.query.get((pid, condition))

    #
    @classmethod
    def find_or_404(cls, pid, condition):
        """ Find an Inventory record by its product_id and condition """
        LOGGER.info("Processing lookup or 404 for product_id %d and condition %s", pid, condition)
        return cls.query.get_or_404((pid, condition))

    #
    @classmethod
    def find_by_product_id(cls, product_id):
        """ Returns the Inventory record with the given product_id
        Args:
            product_id (Integer): the product_id of the Inventory record you want to match
        """
        LOGGER.info("Processing name query for %s ...", product_id)
        return cls.query.filter(cls.product_id == product_id)
