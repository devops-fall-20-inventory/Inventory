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

ID_PREFIX = "inventory_"
BTN_SUFFIX = "-btn"
FLASH_MSG_ID = "flash_message"
ATTR_VALUE = "value"
WAIT_SECONDS = int(getenv('WAIT_SECONDS', '60'))
BASE_URL = getenv('BASE_URL', 'http://localhost:5000')

####################################################################################################
# Scenario: Inventory server is running
####################################################################################################
@given('the following inventories')
def step_impl(context):
    """ Delete all Inventories and load new ones """
    headers = {'Content-Type': 'application/json'}

    # list all of the inventories and delete them one by one
    context.resp = requests.get(context.base_url + '/api/inventory')
    if context.resp.status_code == 200:
        for pet in context.resp.json():
            url = "{}/api/inventory/{}/condition/{}"\
                .format(context.base_url, str(pet["product_id"]), str(pet["condition"]))
            context.resp = requests.delete(url)
            expect(context.resp.status_code).to_equal(204)
        resp = requests.get(context.base_url + '/api/inventory')
        expect(resp.status_code).to_equal(404)

    # load the database with new pets
    create_url = context.base_url + '/api/inventory'
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

@when('I set the "{element_name}" to "{element_value}"')
def step_impl(context, element_name, element_value):
    element_id = ID_PREFIX + element_name.lower()
    element = context.driver.find_element_by_id(element_id)
    element.clear()
    element.send_keys(element_value)


@when('I select "{element_value}" in the "{element_name}" dropdown')
def step_impl(context, element_value, element_name):
    element_id = ID_PREFIX + element_name.lower()
    element = Select(context.driver.find_element_by_id(element_id))
    element.select_by_visible_text(element_value)


@when('I press the "{element_button}" button')
def step_impl(context, element_button):
    button_id = element_button.lower() + BTN_SUFFIX
    context.driver.find_element_by_id(button_id).click()


@then('I should see the message "{message}"')
def step_impl(context, message):
    # element = context.driver.find_element_by_id('flash_message')
    # expect(element.text).to_contain(message)
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, FLASH_MSG_ID),
            message
        )
    )
    expect(found).to_be(True)

####################################################################################################

@when('I copy the "{element_name}" field')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower()
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute(ATTR_VALUE)
    logging.info('Clipboard contains: %s', context.clipboard)


@then('the "{element_name}" field should be empty')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower()
    element = context.driver.find_element_by_id(element_id)
    expect(element.get_attribute(ATTR_VALUE)).to_be(u'')

####################################################################################################

@when('I paste the "{element_name}" field')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower()
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)


@then('I should see "{element_value}" in the "{element_name}" field')
def step_impl(context, element_value, element_name):
    element_id = ID_PREFIX + element_name.lower()
    # element = context.driver.find_element_by_id(element_id)
    # expect(element.get_attribute(ATTR_VALUE)).to_equal(element_value)
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id),
            element_value
        )
    )
    expect(found).to_be(True)


@then('I should see "{element_value}" in the "{element_name}" dropdown')
def step_impl(context, element_value, element_name):
    element_id = ID_PREFIX + element_name.lower()
    element = Select(context.driver.find_element_by_id(element_id))
    expect(element.first_selected_option.text).to_equal(element_value)


####################################################################################################
# Scenario: Get all Inventories
####################################################################################################
@then('I must see "{element_name}" in the results')
def step_impl(context, element_name):
    # element = context.driver.find_element_by_id('search_results')
    # expect(element.text).to_contain(name)
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'search_results'),
            element_name
        )
    )
    expect(found).to_be(True)
####################################################################################################
# Scenario: Get a specific Inventory
####################################################################################################

####################################################################################################
# Scenario: Get a collection of Inventories with a Request parameter
####################################################################################################

####################################################################################################
# Scenario: Delete an Inventory
####################################################################################################
@then('I must not see "{element_name}" in the results')
def step_impl(context, element_name):
    element = context.driver.find_element_by_id('search_results')
    error_msg = "I should not see '%s' in '%s'" % (element_name, element.text)
    ensure(element_name in element.text, False, error_msg)


####################################################################################################
# Scenario: Update an Inventory
####################################################################################################

####################################################################################################
# Scenario: Update an Inventory's stock
####################################################################################################

####################################################################################################
# Scenario: Activate an Inventory
####################################################################################################
@when('I change the "{element_name}" dropdown to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = ID_PREFIX + element_name.lower()
    # element = context.driver.find_element_by_id(element_id)
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    #element.clear()
    element = Select(element)
    element.select_by_visible_text(text_string)

@then('I should see "{name}" with availability set to "{available}" in the results')
def step_impl(context, name, available):
    # element = context.driver.find_element_by_id('search_results')
    # expect(element.text).to_contain(name)
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'search_results'),
            name
        ) and
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'search_results'),
            available
        )
    )
    expect(found).to_be(True)

@then('I should not see "{name}" with availability set to "{available}" in the results')
def step_impl(context, name, available):
    element = context.driver.find_element_by_id('search_results')
    error_msg = "I should not see '%s' in '%s' with availability set to '%s'" % (name, element.text, available)
    ensure((name in element.text and available in element.text), False, error_msg)

####################################################################################################
# Scenario: Deactivate an Inventory
####################################################################################################
