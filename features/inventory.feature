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
    Then I should see "1" in the "Product_id" field
    And I should see "New" in the "Condition" dropdown
    And I should see "5" in the "Quantity" field
    And I should see "0" in the "Restock_level" field
    And I should see "False" in the "Available" dropdown

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

Scenario: Get all Inventory Records' Details
    Given the following inventories
        | product_id    | condition | quantity  | restock_level | available |
        | 963           | new       | 5         | 2             | 1         |

    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I must see "963" in the results
    And I must see "new" in the results
    And I must see "5" in the results
    And I must see "2" in the results
    And I must see "1" in the results 

Scenario: Get a specific Inventory Record's Details with Request parameter
    When I visit the "Home Page"
    And I set the "Product_id" to "573"
    And I select "Used" in the "Condition" dropdown
    And I press the "Search" button    
    Then I should see the message "Success"
    And I should see "Used" in the "Condition" dropdown
    And I should see "6" in the "Quantity" field
    And I should see "2" in the "Restock_level" field
    And I should see "True" in the "Available" dropdown
    And I must see "573" in the results
    And I must see "used" in the results
    And I must see "6" in the results
    And I must see "2" in the results
    And I must see "1" in the results


Scenario: Get a collection of Inventories with a Request parameter
    Given the following inventories
        | product_id    | condition | quantity  | restock_level | available |
        | 963           | new       | 5         | 1             | 1         |
        | 573           | used      | 6         | 2             | 1         |
        | 208           | open box  | 0         | 0             | 0         |
        | 963           | used      | 2         | 1             | 1         |
    When I visit the "Home Page"
    And I set the "Product_id" to "963"
    And I press the "Search" button
    Then I must see "963" in the results
    And I must see "new" in the results
    And I must see "used" in the results

    When I visit the "Home Page"
    And I set the "Product_id" to "963321"
    And I press the "Search" button
    Then I should see the message "There are no records in the Database. You have requested this URI [/api/inventory] but did you mean /api/inventory or /api/inventory//condition/ or /api/inventory//condition//restock ?"

Scenario: Update an Inventory
    When I visit the "Home Page"
    And I set the "Product_id" to "573"
    And I set the "Quantity" to "7"
    And I set the "Restock_level" to "3"
    And I select "Used" in the "Condition" dropdown
    And I select "False" in the "Available" dropdown
    And I press the "Update" button
    Then I should see the message "Success"

    When I copy the "Product_id" field
    And I press the "Clear" button
    And I paste the "Product_id" field
    And I select "Used" in the "Condition" dropdown
    And I press the "Retrieve" button
    Then I should see "573" in the "Product_id" field
    And I should see "7" in the "Quantity" field
    And I should see "3" in the "Restock_level" field
    And I should see "Used" in the "Condition" dropdown
    And I should see "False" in the "Available" dropdown

Scenario: Restock an Inventory
    When I visit the "Home Page"
    And I set the "Product_id" to "208"
    And I set the "Quantity" to "10"
    And I select "Open Box" in the "Condition" dropdown
    And I press the "Restock" button
    Then I should see the message "Success"

    When I copy the "Product_id" field
    And I press the "Clear" button
    And I paste the "Product_id" field
    And I select "Open Box" in the "Condition" dropdown
    And I press the "Retrieve" button
    Then I should see "10" in the "Quantity" field


Scenario: Activate an Inventory

    When I visit the "Home Page"
    And I set the "Product_id" to "10"
    And I set the "Quantity" to "1"
    And I set the "Restock_level" to "0"
    And I select "New" in the "Condition" dropdown
    And I select "False" in the "Available" dropdown
    And I press the "Create" button
    Then I should see the message "Success"

    When I change the "Available" dropdown to "True"
    And I press the "Activate" button
    Then I should see the message "Success"

    When I copy the "Product_id" field
    And I press the "Clear" button
    And I paste the "Product_id" field
    And I select "New" in the "Condition" dropdown
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
    And I press the "Deactivate" button
    Then I should see the message "Success"

    When I copy the "Product_id" field
    And I press the "Clear" button
    And I paste the "Product_id" field
    And I select "New" in the "Condition" dropdown
    And I press the "Retrieve" button
    Then I should see "963" in the "Product_id" field
    And I should see "False" in the "Available" dropdown

Scenario: Delete an Inventory
    When I visit the "Home Page"
    And I set the "Product_id" to "573"
    And I select "Used" in the "Condition" dropdown
    And I press the "Delete" button
    Then I should see the message "Inventory has been Deleted!"
    When I press the "Search" button
    Then I must not see "573" in the results

    When I set the "Product_id" to "208"
    And I press the "Search" button
    Then I should see "208" in the "Product_id" field
    And I should see "Open Box" in the "Condition" dropdown
    When I press the "Delete" button
    Then I should see the message "Inventory has been Deleted!"

    When I visit the "Home Page"
    And I set the "Product_id" to "98292"
    And I select "Used" in the "Condition" dropdown
    And I press the "Delete" button
    Then I should see the message "Inventory has been Deleted!"
