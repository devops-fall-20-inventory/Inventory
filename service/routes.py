"""
Inventory Service

Paths:
------
GET /inventory
    - Returns a list of all inventories in the inventory
GET /inventory/<int:product_id>/condition/<string:condition>
    - Returns the inventory record with the given product_id and condition

POST /inventory
    - Given the data body this creates an inventory record in the DB

PUT /inventory/<int:product_id>/condition/<string:condition>
    - Updates the inventory record with the given product_id and condition
PUT /inventory/<int:product_id>/condition/<string:condition>/activate
    - Given the product_id and condition this updates available = 1
PUT /inventory/<int:product_id>/condition/<string:condition>/deactivate
    - Given the product_id and condition this updates available = 0
PUT /inventory/<int:product_id>/condition/<string:condition>/restock
    - Given the product_id, condition and amount (body) this updates quantity += amount

DELETE /inventory/<int:product_id>/condition/<string:condition>
    - Given the product_id and condition this updates available = 0
"""

import uuid
from functools import wraps
from flask import request, render_template
from flask_api import status
from flask_restplus import Api, Resource, fields, reqparse

from service import keys
from service.model import Inventory
from . import app

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-Api-Key'
    }
}

####################################################################################################
# Configure Swagger
####################################################################################################
api = Api(app,
          version='1.0.0',
          title=keys.INV_TITLE,
          description=keys.INV_DESCR,
          default=keys.KEY_DB_NAME,
          default_label=keys.INV_LABEL,
          doc='/apidocs',
          authorizations=authorizations,
          prefix='/api'
         )

# Define the model so that the docs reflect what can be sent
inventory_model = api.model('Inventory', {
    keys.KEY_PID: fields.Integer(readOnly=True,
                    description='The unique id assigned internally by service'),
    keys.KEY_CND: fields.String(required=True,
                    description='Condition of the product ["new", "used", "open box"]'),
    keys.KEY_QTY: fields.Integer(required=True,
                    description='The Quantity of Inventory item'),
    keys.KEY_LVL: fields.Integer(required=True,
                    description='The level below which restock this item is triggered'),
    keys.KEY_AVL: fields.Integer(required=True,
                    description='Is the Inventory avaialble for purchase?')
})

restock_model = api.model('Inventory', {
    keys.KEY_AMT: fields.Integer(required=True,
                    description='The Amount to add to the existing Quantity'),
})

# query string arguments
inventory_args = reqparse.RequestParser()
inventory_args.add_argument(keys.KEY_PID, type=int,
                    required=False, help='List Inventory by Product ID')

####################################################################################################
# Authorization
####################################################################################################

# Decorator
def token_required(f):
    """ The authorization decorator implementation """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if keys.KEY_API_HEADER in request.headers:
            token = request.headers[keys.KEY_API_HEADER]
        if app.config.get(keys.KEY_API) and app.config[keys.KEY_API] == token:
            return f(*args, **kwargs)
        return {'message': 'Invalid or missing token'}, status.HTTP_401_UNAUTHORIZED
    return decorated

# Function to generate a random API key
def generate_apikey():
    """ Helper function used when testing API keys """
    return uuid.uuid4().hex

####################################################################################################
#  U T I L I T Y   F U N C T I O N S
####################################################################################################
@app.before_first_request
def init_db(dbname=keys.KEY_DB_NAME):
    """ Initlaize the model """
    Inventory.init_db(dbname)

####################################################################################################
# INDEX
####################################################################################################
@app.route("/")
def index():
    """ Root URL response """
    app.logger.info("Request for Root URL")
    return render_template('index.html')

####################################################################################################
#  PATH: /inventory
####################################################################################################
@api.route('/inventory', strict_slashes=False)
class InventoryBase(Resource):
    """
    GET     /inventory - Return all Inventories
    CREATE  /inventory - Create a new Inventory
    """
    #------------------------------------------------------------------
    # LIST ALL INVENTORIES
    #------------------------------------------------------------------
    @api.doc('list_inventories')
    @api.expect(inventory_args, validate=True)
    @api.marshal_list_with(inventory_model)
    def get(self):
        """ Returns all of the Inventories """
        app.logger.info("A GET request for ALL inventories")
        inventories = []
        params = inventory_args.parse_args()
        if params[keys.KEY_PID]:
            pid = params[keys.KEY_PID]
            app.logger.info('Filtering by category: %s', params[keys.KEY_PID])
            inventories = Inventory.find_by_product_id(pid)
        else:
            inventories = Inventory.all()

        results = [inv.serialize() for inv in inventories]
        if len(results) == 0:
            api.abort(status.HTTP_404_NOT_FOUND ,"There are no records in the Database")
        app.logger.info("Returning {} inventories".format(len(results)))
        return results, status.HTTP_200_OK

    #------------------------------------------------------------------
    # ADD A NEW INVENTORY
    #------------------------------------------------------------------
    @api.doc('create_inventory', security='apikey')
    @api.expect(inventory_model)
    @api.response(status.HTTP_400_BAD_REQUEST, 'The posted data was not valid')
    @api.response(status.HTTP_201_CREATED, 'Inventory created successfully')
    @api.marshal_with(inventory_model, code=status.HTTP_201_CREATED)
    @token_required
    def post(self):
        """
        Creates a Inventory
        This endpoint will create a Inventory based the data in the body that is posted
        """

        app.logger.info("Request to create an Inventory record")
        inventory = Inventory()
        inventory.deserialize(api.payload)
        inventory.validate_data()

        if Inventory.find(api.payload[keys.KEY_PID], api.payload[keys.KEY_CND]):
            api.abort(status.HTTP_409_CONFLICT,
                    "Inventory with ({}, {})".format(inventory.product_id, inventory.condition))

        inventory.create()
        location_url = api.url_for(InventoryResource, product_id=inventory.product_id,
            condition=inventory.condition, _external=True)
        app.logger.info("Inventory ({}, {}) created."\
                        .format(inventory.product_id, inventory.condition))
        return inventory.serialize(), status.HTTP_201_CREATED, {'Location': location_url}

####################################################################################################
#  PATH: /inventory/{product_id}/condition/{condition}
####################################################################################################
@api.route('/inventory/<int:product_id>/condition/<string:condition>')
@api.param('product_id, condition', 'The Inventory identifiers')
class InventoryResource(Resource):
    """
    GET     /inventory/<int:product_id>/condition/<string:condition> - Return an Inventory
    PUT     /inventory/<int:product_id>/condition/<string:condition> - Update an Inventory
    DELETE  /inventory/<int:product_id>/condition/<string:condition> - Delete an Inventory
    """

    #------------------------------------------------------------------
    # RETRIEVE AN INVENTORY
    #------------------------------------------------------------------
    @api.doc('get_inventory')
    @api.response(status.HTTP_404_NOT_FOUND, 'Inventory not found')
    @api.marshal_with(inventory_model)
    def get(self, product_id, condition):
        """
        Retrieve a single Inventory

        This endpoint will return a Inventory based on it's id
        """
        app.logger.info("A GET request for inventories with product_id {} and condition {}"\
                        .format(product_id, condition))
        inventory = Inventory.find(product_id, condition)
        if not inventory:
            api.abort(status.HTTP_404_NOT_FOUND,
                "Inventory ({}, {}) NOT FOUND".format(product_id, condition))
        app.logger.info("Return inventory with product_id {} and condition {}"\
                        .format(product_id, condition))
        return inventory.serialize(), status.HTTP_200_OK

    #------------------------------------------------------------------
    # UPDATE AN (EXISTING) INVENTORY
    #------------------------------------------------------------------
    @api.doc('update_inventory', security='apikey')
    @api.response(status.HTTP_404_NOT_FOUND, 'Inventory not found')
    @api.response(status.HTTP_400_BAD_REQUEST, 'The posted Inventory data was not valid')
    @api.expect(inventory_model)
    @api.marshal_with(inventory_model)
    @token_required
    def put(self, product_id, condition):
        """
        Update an Inventory
        This endpoint will update a Inventory based the body that is posted
        """
        app.logger.info("Request to update inventory with key ({}, {})"\
                        .format(product_id, condition))

        inventory = Inventory.find(product_id, condition)
        if not inventory:
            api.abort(status.HTTP_404_NOT_FOUND,
                    "Inventory with ({}, {})".format(product_id, condition))

        resp_old = inventory.serialize()
        resp_new = api.payload
        for key in resp_old.keys():
            if key in resp_new:
                resp_old[key] = resp_new[key]
        inventory.deserialize(resp_old)
        inventory.validate_data()
        inventory.update()
        app.logger.info("Inventory ({}, {}) updated.".format(product_id, condition))
        return inventory.serialize(), status.HTTP_200_OK

    #------------------------------------------------------------------
    # DELETE AN INVENTORY
    #------------------------------------------------------------------
    @api.doc('delete_inventory', security='apikey')
    @api.response(status.HTTP_204_NO_CONTENT, 'Inventory deleted')
    @token_required
    def delete(self, product_id, condition):
        """
        Delete a Inventory

        This endpoint will delete a Inventory based the id specified in the path
        """
        app.logger.info("Request to delete inventory with key ({}, {})"\
                        .format(product_id, condition))
        inventory = Inventory.find(product_id, condition)
        if inventory:
            inventory.delete()
        app.logger.info("Inventory with product_id {} and condition {} deleted"
                        .format(product_id, condition))
        return '', status.HTTP_204_NO_CONTENT

####################################################################################################
#  PATH: /inventory/{product_id}/condition/{condition}/restock
####################################################################################################
@api.route('/inventory/<int:product_id>/condition/<string:condition>/restock')
@api.param('product_id, condition', 'The Inventory identifiers')
class InventoryResourceRestock(Resource):
    """
    PUT     /inventory/<int:product_id>/condition/<string:condition>/restock - Restock an Inventory
    """
    #------------------------------------------------------------------
    # RESTOCK AN (EXISTING) INVENTORY's QUANTITY
    #------------------------------------------------------------------
    @api.doc('update_inventory', security='apikey')
    @api.response(status.HTTP_404_NOT_FOUND, 'Inventory not found')
    @api.response(status.HTTP_400_BAD_REQUEST, 'The posted body was invalid. Please check again.')
    @api.expect(restock_model)
    @api.marshal_with(inventory_model)
    @token_required
    def put(self, product_id, condition):
        """
        Restock an Inventory's Quantity
        """
        app.logger.info("Request to update inventory with key ({}, {})"\
                        .format(product_id, condition))

        # Check if the record exists
        inventory = Inventory.find(product_id, condition)
        if not inventory:
            api.abort(status.HTTP_404_NOT_FOUND,
                "Inventory with ({}, {})".format(product_id, condition))

        # Checking for keys.KEY_AMT keyword
        json = request.get_json()
        json = api.payload
        if "amount" not in json.keys():
            api.abort(status.HTTP_400_BAD_REQUEST, "Invalid data: Amount missing")

        # Checking for amount >= 0
        amount = json[keys.KEY_AMT]
        if amount<0:
            api.abort(status.HTTP_400_BAD_REQUEST, "Invalid data: Amount <= 0")

        inventory.quantity += amount
        inventory.validate_data()
        inventory.update()
        app.logger.info("Inventory ({}, {}) restocked.".format(product_id, condition))
        return inventory.serialize(), status.HTTP_200_OK

####################################################################################################
#  PATH: /inventory/{product_id}/condition/{condition}/activate
####################################################################################################
@api.route('/inventory/<int:product_id>/condition/<string:condition>/activate')
@api.param('product_id, condition', 'The Inventory identifiers')
class InventoryResourceActivate(Resource):
    """
    PUT     /inventory/<int:product_id>/condition/<string:condition>/restock - Restock an Inventory
    """
    #------------------------------------------------------------------
    # RESTOCK AN (EXISTING) INVENTORY's QUANTITY
    #------------------------------------------------------------------
    @api.doc('update_inventory', security='apikey')
    @api.response(status.HTTP_404_NOT_FOUND, 'Inventory not found')
    @api.marshal_with(inventory_model)
    @token_required
    def put(self, product_id, condition):
        """
        Restock an Inventory's Quantity
        """
        app.logger.info("Request to update inventory with key ({}, {})"\
                        .format(product_id, condition))

        # Check if the record exists
        inventory = Inventory.find(product_id, condition)
        if not inventory:
            api.abort(status.HTTP_404_NOT_FOUND,
                "Inventory with ({}, {})".format(product_id, condition))

        inventory.available = 1
        inventory.validate_data()
        inventory.update()
        app.logger.info("Inventory ({}, {}) restocked.".format(product_id, condition))
        return inventory.serialize(), status.HTTP_200_OK

####################################################################################################
#  PATH: /inventory/{product_id}/condition/{condition}/deactivate
####################################################################################################
@api.route('/inventory/<int:product_id>/condition/<string:condition>/deactivate')
@api.param('product_id, condition', 'The Inventory identifiers')
class InventoryResourceDeactivate(Resource):
    """
    PUT     /inventory/<int:product_id>/condition/<string:condition>/restock - Restock an Inventory
    """
    #------------------------------------------------------------------
    # RESTOCK AN (EXISTING) INVENTORY's QUANTITY
    #------------------------------------------------------------------
    @api.doc('update_inventory', security='apikey')
    @api.response(status.HTTP_404_NOT_FOUND, 'Inventory not found')
    @api.marshal_with(inventory_model)
    @token_required
    def put(self, product_id, condition):
        """
        Restock an Inventory's Quantity
        """
        app.logger.info("Request to update inventory with key ({}, {})"\
                        .format(product_id, condition))

        # Check if the record exists
        inventory = Inventory.find(product_id, condition)
        if not inventory:
            api.abort(status.HTTP_404_NOT_FOUND,
                "Inventory with ({}, {})".format(product_id, condition))

        inventory.available = 0
        inventory.validate_data()
        inventory.update()
        app.logger.info("Inventory ({}, {}) restocked.".format(product_id, condition))
        return inventory.serialize(), status.HTTP_200_OK
