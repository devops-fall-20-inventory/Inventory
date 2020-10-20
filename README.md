# Inventory 

## Description
This repository contains all the work of the Inventory Squad as part of the Fall '20 DevOps under [John Rofrano](https://github.com/rofrano).

The inventory resource keeps track of how many of each product we have in our warehouse. At a minimum it will reference a product and the quantity on hand. Inventory also tracks restock levels and the condition of the item (i.e., new, open box, used). Restock levels will help you know when to order more products. Being able to query products by their condition (e.g., new, used) is very useful.

## Squad

1. [Arahant Ashok Kumar](https://github.com/arahant) - Product Owner
2. [Arun Muthu](https://github.com/arungithub9)
3. [Hardik Rokad](https://github.com/hardikr586) 
4. [Jiazhou Liu](https://github.com/602071349) - Agile Coach
5. [Kainat Naeem](https://github.com/kainattnaeem)

## Version History

1. Initial Repository Setup
2. application runs locally

## Getting Started

### Interfaces
    Returns a list of all inventories in the inventory
    GET /inventory

    Returns the inventory with the given product_id and condition
    GET /inventory/<int:product_id>/<string:condition>

    Returns the inventories with the given product_id
    GET /inventory/<int:product_id>

    Creates a new inventory in the Inventory DB
    based on the JSON data in the request body 
    POST /inventory

    Updates the inventory with the given product_id and condition
    based on the JSON data in the request body 
    PUT /inventory/<int:product_id>/<string:condition>

    Deletes an inventory with the given product_id and condition
    DELETE /inventory/<int:product_id>/<string:condition>

    Sample JSON data format:
	{
	  "product_id":1234567,
          "quantity":1,
          "restock_level":10,
          "condition":"new",
          "available":1
        }
### Test and Running
   To run and test the code, you can use the following command:
	vagrant up
        vagrant ssh
        cd /vagrant
        FLASK_APP=service:app flask run -h 0.0.0.0
   Then you can test the application in the browser from you host machine, or
   you can use Postman for sending http requests.

   You can also type nosetests under /vagrant to check different test cases and the overall coverage.
    
    

    

