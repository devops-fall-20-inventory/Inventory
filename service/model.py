"""
Models for Inventory
All of the models are stored in this module
"""
import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

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
    pass

######################################################################
#  Inventory Model class
################################################################################
class Inventory(db.Model):

    app = None

    # Table Schema
    product_id = db.Column(db.Integer, primary_key=True)
    condition = db.Column(db.String(100), primary_key=True)
    quantity = db.Column(db.Integer)
    restock_level = db.Column(db.Integer)
    available = db.Column(db.Integer)

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
            raise DataValidationError(
                "Invalid Inventory record: body of request contained" "bad or no data"
            )
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    ######################################################################
    # VALIDATING DATA FORMATS
    def validate_data(self):
        args = []

        err_pid = self.validate_data_product_id()
        if not err_pid:
            args.append(ATTR_PRODUCT_ID)

        err_cnd = self.validate_data_condition()
        if not err_cnd:
            args.append(ATTR_CONDITION)

        err_qty = self.validate_data_quantity()
        if not err_qty:
            args.append(ATTR_QUANTITY)

        err_lvl = self.validate_data_restock_level()
        if not err_lvl:
            args.append(ATTR_RESTOCK_LEVEL)

        err_avl = self.validate_data_available()
        if not err_avl:
            args.append(ATTR_AVAILABLE)

        if not (err_pid and err_cnd and err_qty and err_lvl and err_avl):
            msg = "Error in data arguments: ".format(args)
            raise DataValidationError(msg)
        return True

    # Validating Product ID format
    def validate_data_product_id(self):
        pid = self.product_id
        return type(pid) is int and pid>0

    # validating Condition format
    def validate_data_condition(self):
        cnd = self.condition
        return type(cnd) is str and cnd.lower() in CONDITIONS

    # Validating Quantity format
    def validate_data_quantity(self):
        qty = self.quantity
        return type(qty) is int and qty>0 and qty<=QTY_HIGH

    # Validating Restock level format
    def validate_data_restock_level(self):
        lvl = self.restock_level
        return type(lvl) is int and lvl>0 and lvl<=RESTOCK_LVL

    # Validating Available format
    def validate_data_available(self):
        avl = self.available
        return type(avl) is type(AVAILABLE_TRUE) and avl in [AVAILABLE_TRUE,AVAILABLE_FALSE]

    ######################################################################
    # CREATE
    def create(self):
        """
        Creates an Inventory record to the database
        """
        logger.info("Creating %d", self.product_id)
        db.session.add(self)
        db.session.commit()

    ######################################################################
    # UPDATE
    def update(self):
        """
        Updates an Inventory record to the database
        """
        logger.info("Saving %d", self.product_id)
        db.session.commit()

    ######################################################################
    # DELETE
    def delete(self):
        """ Removes an Inventory record from the data store """
        logger.info("Deleting %d", self.product_id)
        db.session.delete(self)
        db.session.commit()

    ######################################################################
    # READ
    @classmethod
    def all(cls):
        """ Returns all of the Inventory records in the database """
        logger.info("Processing all Inventory records")
        return cls.query.all()

    #
    @classmethod
    def find(cls, pid, condition):
        """ Finds an Inventory record by its product_id and condition """
        logger.info("Processing lookup for product_id %d and condition %s ", pid, condition)
        return cls.query.get((pid, condition))

    #
    @classmethod
    def find_or_404(cls, pid, condition):
        """ Find an Inventory record by its product_id and condition """
        logger.info("Processing lookup or 404 for product_id %d and condition %s", pid, condition)
        return cls.query.get_or_404((pid, condition))

    #
    @classmethod
    def find_by_product_id(cls, product_id):
        """ Returns the Inventory record with the given product_id
        Args:
            product_id (Integer): the product_id of the Inventory record you want to match
        """
        logger.info("Processing name query for %s ...", product_id)
        return cls.query.filter(cls.product_id == product_id)
