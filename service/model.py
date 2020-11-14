"""
Models for Inventory
All of the models are stored in this module
"""
import logging
from flask_sqlalchemy import SQLAlchemy, sqlalchemy
from service import keys
LOGGER = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
DB = SQLAlchemy()

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

class DBError(Exception):
    """ Used for an DB connectivity errors """

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
            self.product_id = data[keys.KEY_PID]
            self.quantity = data[keys.KEY_QTY]
            self.restock_level = data[keys.KEY_LVL]
            self.condition = data[keys.KEY_CND]
            self.available = data[keys.KEY_AVL]
        except KeyError as error:
            raise DataValidationError("Invalid Inventory record: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError("Invalid Inventory record: body contained bad or no data")
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        try:
            LOGGER.info("Initializing database")
            cls.app = app
            # This is where we initialize SQLAlchemy from the Flask app
            DB.init_app(app)
            app.app_context().push()
            DB.create_all()  # make our sqlalchemy tables
        except sqlalchemy.exc.ArgumentError as err:
            raise DBError("Invalid DB connection: {}".format(err))
        except sqlalchemy.exc.OperationalError as err:
            raise DBError("Invalid DB connection: {}".format(err))
        except sqlalchemy.exc.InvalidRequestError as err:
            raise DBError("Invalid DB connection: {}".format(err))

    ######################################################################
    def validate_data(self):
        """
        VALIDATING DATA FORMATS
        """
        args = []

        res_pid = self.validate_data_product_id()
        if not res_pid:
            args.append("Product ID")

        res_cnd = self.validate_data_condition()
        if not res_cnd:
            args.append("Condition")

        res_qty = self.validate_data_quantity()
        if not res_qty:
            args.append("Quantity")

        res_lvl = self.validate_data_restock_level()
        if not res_lvl:
            args.append("Restock Level")

        res_avl = self.validate_data_available()
        if not res_avl:
            args.append("Available")

        if not (res_pid and res_cnd and res_qty and res_lvl and res_avl):
            msg = "Error in data: {}".format(args)
            raise DataValidationError(msg)
        return True

    def validate_data_product_id(self):
        """
        Validating Product ID format
        """
        pid = self.product_id
        if isinstance(pid, str):
            return pid.isdigit() and int(pid) >= 0
        return isinstance(pid, int) and pid >= 0

    def validate_data_condition(self):
        """
        validating Condition format
        """
        cnd = self.condition
        return isinstance(cnd, str) and cnd in keys.CONDITIONS

    def validate_data_quantity(self):
        """
        Validating Quantity format
        """
        qty = self.quantity
        if isinstance(qty, str):
            return qty.isdigit() and (keys.QTY_LOW <= int(qty) <= keys.QTY_HIGH)
        return isinstance(qty, int) and (keys.QTY_LOW <= qty <= keys.QTY_HIGH)

    def validate_data_restock_level(self):
        """
        Validating Restock level format
        """
        lvl = self.restock_level
        if isinstance(lvl, str):
            return lvl.isdigit() and (keys.QTY_LOW <= int(lvl) <= keys.RESTOCK_LVL)
        return isinstance(lvl, int) and (keys.QTY_LOW <= lvl <= keys.RESTOCK_LVL)

    def validate_data_available(self):
        """
        Validating Available format
        """
        avl = self.available
        if isinstance(avl, str):
            return avl.isdigit() and int(avl) in [keys.AVAILABLE_TRUE, keys.AVAILABLE_FALSE]
        return isinstance(avl, int) and avl in [keys.AVAILABLE_TRUE, keys.AVAILABLE_FALSE]

    ######################################################################
    def create(self):
        """
        Creates an Inventory record to the database
        """
        LOGGER.info("Creating {}".format(self.product_id))
        DB.session.add(self)
        DB.session.commit()

    ######################################################################
    def update(self):
        """
        Updates an Inventory record to the database
        """
        LOGGER.info("Updating {}".format(self.product_id))
        DB.session.commit()

    ######################################################################
    def delete(self):
        """ Removes an Inventory record from the data store """
        LOGGER.info("Deleting {}".format(self.product_id))
        DB.session.delete(self)
        DB.session.commit()

    ######################################################################
    @classmethod
    def all(cls):
        """ Returns all of the Inventory records in the database """
        LOGGER.info("Processing GET all Inventory records")
        return cls.query.all()

    #
    @classmethod
    def find(cls, pid, condition):
        """ Finds an Inventory record by its product_id and condition """
        LOGGER.info("Processing GET for product_id {} and condition {}".format(pid, condition))
        return cls.query.get((pid, condition))

    #
    @classmethod
    def find_or_404(cls, pid, condition):
        """ Find an Inventory record by its product_id and condition """
        LOGGER.info("Processing GET or 404 for product_id {} and condition {}"\
                    .format(pid, condition))
        return cls.query.get_or_404((pid, condition))

    #
    @classmethod
    def find_by_product_id(cls, product_id):
        """ Returns the Inventory record with the given product_id
        Args:
            product_id (Integer): the product_id of the Inventory record you want to match
        """
        LOGGER.info("Processing GET query for {}...".format(product_id))
        return cls.query.filter(cls.product_id == product_id)
