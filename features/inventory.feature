Feature: "Inventory" service backend
    As an e-Commerce "Admin"
    I need a RESTful "Inventory" service
    So that I can keep track of all my "Products"

####################################################################################################
Background: Sample database records
    Given the following inventories
        | product_id    | condition | quantity  | restock_level | available |
        | 963           | new       | 5         | 1             | 1         |
        | 573           | used      | 6         | 2             | 1         |
        | 208           | open box  | 0         | 0             | 0         |
        | 208           | used      | 0         | 0             | 0         |
        | 211           | used      | 0         | 0             | 0         |

Scenario: Inventory server is running
    When I visit the "Home Page"
    And I press the "Clear" button
    Then I should see "Inventory REST API Service" in the title
    And I should not see "404 Not Found"

####################################################################################################
# POST
Scenario: Create an Inventory
    When I visit the "Home Page"
    And I press the "Clear" button
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
    And I press the "Search" button
    Then I must see "1" in the results
    And I must see "new" in the results
    And I must see "5" in the results

    When I press the "Clear" button
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
    And I press the "Search" button
    Then I must see "2" in the results
    And I must see "new" in the results
    And I must see "1" in the results

####################################################################################################
# GET
Scenario: Retrieve an Inventory Record
    When I visit the "Home Page"
    And I press the "Clear" button
    And I set the "Product_id" to "211"
    And I select "Used" in the "Condition" dropdown
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "0" in the "Quantity" field
    And I should see "0" in the "Restock_level" field
    And I should see "False" in the "Available" dropdown

Scenario: Search for all Inventory Records
    When I visit the "Home Page"
    And I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    And I must see "963" in the results
    And I must see "573" in the results
    And I must see "208" in the results
    And I must see "211" in the results

Scenario: Search for a collection of inventories (with a request parameter)
    When I visit the "Home Page"
    And I press the "Clear" button
    And I select "Used" in the "Condition" dropdown
    And I press the "Search" button
    Then I must see "573" in the results
    Then I must see "208" in the results
    Then I must see "211" in the results
    Then I must not see "963" in the results

    When I visit the "Home Page"
    And I press the "Clear" button
    And I set the "Quantity" to "6"
    And I press the "Search" button
    Then I must see "573" in the results
    Then I must not see "963" in the results
    Then I must not see "208" in the results
    Then I must not see "211" in the results

    When I visit the "Home Page"
    And I press the "Clear" button
    And I set the "Product_id" to "208"
    And I press the "Search" button
    Then I must see "208" in the results
    Then I must see "used" in the results
    Then I must see "open box" in the results
    Then I must not see "963" in the results
    Then I must not see "573" in the results
    Then I must not see "211" in the results

    When I visit the "Home Page"
    And I press the "Clear" button
    And I select "True" in the "Available" dropdown
    And I press the "Search" button
    Then I must see "963" in the results
    Then I must see "573" in the results
    Then I must not see "208" in the results
    Then I must not see "211" in the results

    When I visit the "Home Page"
    And I press the "Clear" button
    And I select "False" in the "Available" dropdown
    And I press the "Search" button
    Then I must not see "963" in the results
    Then I must not see "573" in the results
    Then I must see "208" in the results
    Then I must see "211" in the results

####################################################################################################
# PUT
Scenario: Update an Inventory
    When I visit the "Home Page"
    And I press the "Clear" button
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
    And I press the "Search" button
    Then I must see "573" in the results
    And I must see "7" in the results
    And I must see "3" in the results
    And I must see "used" in the results
    And I must see "0" in the results

Scenario: Restock an Inventory
    When I visit the "Home Page"
    And I press the "Clear" button
    And I set the "Product_id" to "208"
    And I select "Open Box" in the "Condition" dropdown
    And I set the "Quantity" to "10"
    And I press the "Restock" button
    Then I should see the message "Success"

    When I copy the "Product_id" field
    And I press the "Clear" button
    And I paste the "Product_id" field
    And I press the "Search" button
    Then I must see "208" in the results
    And I must see "10" in the results

Scenario: Activate an Inventory
    When I visit the "Home Page"
    And I press the "Clear" button
    And I set the "Product_id" to "208"
    And I select "Used" in the "Condition" dropdown

    When I press the "Activate" button
    Then I should see the message "Success"

    When I copy the "Product_id" field
    And I press the "Clear" button
    And I paste the "Product_id" field
    And I press the "Search" button
    Then I must see "208" in the results
    And I must see "1" in the results

Scenario: Deactivate an Inventory
    When I visit the "Home Page"
    And I press the "Clear" button
    And I set the "Product_id" to "963"
    And I select "New" in the "Condition" dropdown

    When I press the "Deactivate" button
    Then I should see the message "Success"

    When I copy the "Product_id" field
    And I press the "Clear" button
    And I paste the "Product_id" field
    And I press the "Search" button
    Then I must see "963" in the results
    And I must see "0" in the results
    
####################################################################################################
# DELETE
Scenario: Delete an Inventory
    When I visit the "Home Page"
    And I press the "Clear" button
    And I set the "Product_id" to "573"
    And I select "Used" in the "Condition" dropdown
    And I press the "Delete" button
    Then I should see the message "Inventory has been Deleted!"

    When I press the "Search" button
    Then I must not see "573" in the results
