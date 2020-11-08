from os import getenv
import logging
import json
import requests
from behave import *
from compare import expect, ensure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions

logger  = logging.getLogger('inventory-bdd')
####################################################################################################
# Scenario: Inventory server is running
####################################################################################################
@given('the following inventories')
def step_impl(context):
    """ Delete all Inventories and load new ones """
    headers = {'Content-Type': 'application/json'}

    # list all of the inventories and delete them one by one
    context.resp = requests.get(context.base_url + '/inventory', headers=headers)
    if context.resp.status_code == 200:
        for pet in context.resp.json():
            url = "{}/inventory/{}/condition/{}"\
                .format(context.base_url, str(pet["product_id"]), str(pet["condition"]))
            context.resp = requests.delete(url, headers=headers)
            expect(context.resp.status_code).to_equal(204)
        logger.debug('DB cleared')
    resp = requests.get(context.base_url + '/inventory', headers=headers)
    expect(resp.status_code).to_equal(404)

    # load the database with new pets
    create_url = context.base_url + '/inventory'
    acceptable_status_codes = [201, 409]
    for row in context.table:
        data = {
            "product_id": row['product_id'],
            "condition": row['condition'],
            "quantity": row['quantity'],
            "restock_level": row['restock_level'],
            "available": row['available']
        }
        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        expect(acceptable_status_codes).to_contain(context.resp.status_code)
    logger.debug('DB (re)populated')


@when('I visit the "Home page"')
def step_impl(context):
    context.driver.get(context.base_url)


@then('I should see "{message}" in the title')
def step_impl(context, message):
    expect(context.driver.title).to_contain(message)


@then('I should not see "{message}"')
def step_impl(context, message):
    error_msg = "I should not see '{}' in '{}'".format(message, context.resp.text)
    ensure(message in context.resp.text, False, error_msg)
    

####################################################################################################
# Scenario: Create an Inventory
####################################################################################################
@when('I set the "Product_id" to "1"')
def step_impl(context):
    raise NotImplementedError('STEP: When I set the "Product_id" to "1"')


@when('I set the "Quantity" to "5"')
def step_impl(context):
    raise NotImplementedError('STEP: When I set the "Quantity" to "5"')


@when('I set the "Restock_level" to "0"')
def step_impl(context):
    raise NotImplementedError('STEP: When I set the "Restock_level" to "0"')


@when('I select "New" in the "Condition" dropdown')
def step_impl(context):
    raise NotImplementedError('STEP: When I select "New" in the "Condition" dropdown')


@when('I select "True" in the "Available" dropdown')
def step_impl(context):
    raise NotImplementedError('STEP: When I select "True" in the "Available" dropdown')


@when('I press the "Create" button')
def step_impl(context):
    raise NotImplementedError('STEP: When I press the "Create" button')


@then('I should see the message "Success"')
def step_impl(context):
    raise NotImplementedError('STEP: Then I should see the message "Success"')


@when('I copy the "Product_id" field')
def step_impl(context):
    raise NotImplementedError('STEP: When I copy the "Product_id" field')


@when('I press the "Clear" button')
def step_impl(context):
    raise NotImplementedError('STEP: When I press the "Clear" button')


@then('the "Product_id" field should be empty')
def step_impl(context):
    raise NotImplementedError('STEP: Then the "Product_id" field should be empty')


@then('the "Quantity" field should be empty')
def step_impl(context):
    raise NotImplementedError('STEP: Then the "Quantity" field should be empty')


@then('the "Restock_level" field should be empty')
def step_impl(context):
    raise NotImplementedError('STEP: Then the "Restock_level" field should be empty')


@when('I press the "Product_id" field')
def step_impl(context):
    raise NotImplementedError('STEP: When I press the "Product_id" field')


@when('I press the "Retrieve" button')
def step_impl(context):
    raise NotImplementedError('STEP: When I press the "Retrieve" button')


@then('I should see "1" in the "Product_id" field')
def step_impl(context):
    raise NotImplementedError('STEP: Then I should see "1" in the "Product_id" field')


@then('I should see "New" in the "Condition" dropdown')
def step_impl(context):
    raise NotImplementedError('STEP: Then I should see "New" in the "Condition" dropdown')


@then('I should see "5" in the "Quantity" field')
def step_impl(context):
    raise NotImplementedError('STEP: Then I should see "5" in the "Quantity" field')


@then('I should see "0" in the "Restock_level" field')
def step_impl(context):
    raise NotImplementedError('STEP: Then I should see "0" in the "Restock_level" field')


@then('I should see "True" in the "Available" dropdown')
def step_impl(context):
    raise NotImplementedError('STEP: Then I should see "True" in the "Available" dropdown')


####################################################################################################
# Scenario: Get all Inventories
####################################################################################################

####################################################################################################
# Scenario: Get a specific Inventory
####################################################################################################

####################################################################################################
# Scenario: Get a collection of Inventories with a Request parameter
####################################################################################################

####################################################################################################
# Scenario: Delete an Inventory
####################################################################################################

####################################################################################################
# Scenario: Update an Inventory
####################################################################################################

####################################################################################################
# Scenario: Update an Inventory's stock
####################################################################################################

####################################################################################################
# Scenario: Activate an Inventory
####################################################################################################

####################################################################################################
# Scenario: Deactivate an Inventory
####################################################################################################
