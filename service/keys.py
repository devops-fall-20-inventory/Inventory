"""
The generic variables for ALL the programs
"""

# __init__.py
DATABASE_URI_LOCAL = "postgres://postgres:postgres@localhost:5432/postgres"
KEY_DB_URI="DATABASE_URI"
KEY_SQL_ALC="SQLALCHEMY_DATABASE_URI"
KET_SECRET="SECRET_KEY"

# service.py
DEMO_MSG = "Inventory REST API Service"

# routes.py
KEY_DB_NAME='inventory'
KEY_PID='product_id'
KEY_CND='condition'
KEY_QTY='quantity'
KEY_LVL='restock_level'
KEY_AVL='available'
KEY_AMT='amount'
KEY_CONTENT_TYPE_JSON="application/json"
KEY_API_HEADER = 'X-Api-Key'
KEY_API = 'API_KEY'
INV_TITLE = "Inventory REST API Service"
INV_DESCR = "This is an Inventory E-Commerce server."
INV_LABEL = "Inventory shop operations"

# model.py
CONDITIONS = ["new", "used", "open box"]
AVAILABLE_TRUE = 1
AVAILABLE_FALSE = 0
QTY_LOW = 0
QTY_HIGH = 50
QTY_STEP = 1
RESTOCK_LVL = 50
MAX_ATTR = 5

ATTR_DEFAULT = 0
ATTR_PRODUCT_ID = 1
ATTR_CONDITION = 2
ATTR_QUANTITY = 3
ATTR_RESTOCK_LEVEL = 4
ATTR_AVAILABLE = 5
