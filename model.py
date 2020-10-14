"""
Models for Inventory
All of the models are stored in this module
"""
import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass


class Inventory(db.Model):
    """
    Class that represents an Inventory
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    restock_level = db.Column(db.Integer)
    condition = db.Column(db.String(100))
    available = db.Column(db.String(100))

    def __repr__(self):
        return "<<product_id %d id=[%d]>" % (self.product_id, self.id)

    def create(self):
        """
        Creates an Inventory record to the database
        """
        logger.info("Creating %d", self.product_id)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def save(self):
        """
        Updates an Inventory record to the database
        """
        logger.info("Saving %d", self.product_id)
        db.session.commit()

    def delete(self):
        """ Removes an Inventory record from the data store """
        logger.info("Deleting %d", self.product_id)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes an Inventory record into a dictionary """
        return {
            "id": self.id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "restock_level": self.restock_level,
            "condition": self.condition,
            "available": self.available
        }

    def deserialize(self, data):
        """
        Deserializes an Inventory record from a dictionary
        Args:
            data (dict): A dictionary containing the resource data
        """
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

    @classmethod
    def all(cls):
        """ Returns all of the Inventory records in the database """
        logger.info("Processing all Inventory records")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds an Inventory record by it's ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_or_404(cls, by_id):
        """ Find an Inventory record  by it's id """
        logger.info("Processing lookup or 404 for id %s ...", by_id)
        return cls.query.get_or_404(by_id)

    @classmethod
    def find_by_product_id(cls, product_id):
        """ Returns the Inventory record with the given product_id
        Args:
            product_id (Integer): the product_id of the Inventory record you want to match
        """
        logger.info("Processing name query for %s ...", product_id)
        return cls.query.filter(cls.product_id == product_id)