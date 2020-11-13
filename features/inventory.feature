Feature: "Inventory" service backend
    As an e-Commerce "Admin"
    I need a RESTful "Inventory" service
    So that I can keep track of all my "Products"

Background: Sample database records
    Given the following inventories
        | product_id    | condition | quantity  | restock_level | available |
        | 963           | new       | 5         | 1             | 1         |
        | 573           | used      | 6         | 2             | 1         |
        | 208           | open box  | 0         | 0             | 0         |

Scenario: Inventory server is running
    When I visit the "Home Page"
    Then I should see "Inventory REST API Service" in the title
    And I should not see "404 Not Found"

Scenario: Create an Inventory
    When I visit the "Home Page"
    And I set the "Product_id" to "1"
    And I set the "Quantity" to "5"
    And I set the "Restock_level" to "0"
    And I select "New" in the "Condition" dropdown
    And I select "True" in the "Available" dropdown
    And I press the "Create" button
    Then I should see the message "Success"

    When I copy the "Product_id" field
    And I press the "Clear" button
    Then the "Product_id" field should be empty
    Then the "Quantity" field should be empty
    Then the "Restock_level" field should be empty

    When I paste the "Product_id" field
    And I select "New" in the "Condition" dropdown
    And I press the "Retrieve" button
    Then I should see "1" in the "Product_id" field
    And I should see "New" in the "Condition" dropdown
    And I should see "5" in the "Quantity" field
    And I should see "0" in the "Restock_level" field
    And I should see "True" in the "Available" dropdown

    When I visit the "Home Page"
    And I set the "Product_id" to "2"
    And I set the "Quantity" to "1"
    And I set the "Restock_level" to "0"
    And I select "New" in the "Condition" dropdown
    And I select "False" in the "Available" dropdown
    And I press the "Create" button
    Then I should see the message "Success"

    When I copy the "Product_id" field
    And I press the "Clear" button
    Then the "Product_id" field should be empty
    Then the "Quantity" field should be empty
    Then the "Restock_level" field should be empty

    When I paste the "Product_id" field
    And I select "New" in the "Condition" dropdown
    And I press the "Retrieve" button
    Then I should see "2" in the "Product_id" field
    And I should see "New" in the "Condition" dropdown
    And I should see "1" in the "Quantity" field
    And I should see "0" in the "Restock_level" field
    And I should see "False" in the "Available" dropdown


Scenario: Get all Inventories

Scenario: Get a specific Inventory

Scenario: Get a collection of Inventories with a Request parameter

Scenario: Delete an Inventory

Scenario: Update an Inventory

Scenario: Update an Inventory's stock

Scenario: Activate an Inventory

    When I visit the "Home Page"
    And I set the "Product_id" to "10"
    And I set the "Quantity" to "0"
    And I set the "Restock_level" to "0"
    And I select "New" in the "Condition" dropdown
    And I select "False" in the "Available" dropdown
    And I press the "Create" button
    Then I should see the message "Success"

    When I change the "Available" dropdown to "True"
    And I press the "Update" button
    Then I should see the message "Success"

    When I copy the "Product_id" field
    And I select "New" in the "Condition" dropdown
    And I press the "Clear" button
    And I paste the "Product_id" field
    And I press the "Retrieve" button
    Then I should see "10" in the "Product_id" field
    And I should see "True" in the "Available" dropdown


Scenario: Deactivate an Inventory

    When I visit the "Home Page"
    And I set the "Product_id" to "963"
    And I select "New" in the "Condition" dropdown
    And I press the "Search" button
    Then I should see "963" in the "Product_id" field
    And I should see "True" in the "Available" dropdown

    When I select "False" in the "Available" dropdown
    And I press the "Update" button
    Then I should see the message "Success"

    When I copy the "Product_id" field
    And I press the "Clear" button
    And I paste the "Product_id" field
    And I select "New" in the "Condition" dropdown
    And I press the "Retrieve" button
    Then I should see "963" in the "Product_id" field
    And I should see "False" in the "Available" dropdown
