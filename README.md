# Inventory

[![Build Status](https://travis-ci.org/devops-fall-20-inventory/inventories.svg?branch=master)](https://travis-ci.org/devops-fall-20-inventory/inventories)
[![codecov](https://codecov.io/gh/devops-fall-20-inventory/inventories/branch/master/graph/badge.svg?token=WHT72OFUGH)](https://codecov.io/gh/devops-fall-20-inventory/inventories)

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/)

[![GitHub issues](https://img.shields.io/github/issues/devops-fall-20-inventory/inventories)](https://github.com/devops-fall-20-inventory/inventories/issues)
[![GitHub closed issues](https://img.shields.io/github/issues-closed/devops-fall-20-inventory/inventories?color=g)](https://github.com/devops-fall-20-inventory/inventories/issues?q=is%3Aissue+is%3Aclosed)

[![GitHub commits](https://img.shields.io/github/commit-activity/m/devops-fall-20-inventory/inventories)](https://github.com/devops-fall-20-inventory/inventories/commits)
[![GitHub last commit](https://img.shields.io/github/last-commit/devops-fall-20-inventory/inventories?color=blue)](https://github.com/devops-fall-20-inventory/inventories/commit/master)

## Description
This repository contains all the work of the Inventory Squad as part of the Fall '20 DevOps under [John Rofrano](https://github.com/rofrano).

The inventory resource keeps track of how many of each product we have in our warehouse. At a minimum it will reference a product and the quantity on hand. Inventory also tracks restock levels and the condition of the item (i.e., new, open box, used). Restock levels will help you know when to order more products. Being able to query products by their condition (e.g., new, used) is very useful.

## Squad

1. [Arahant Ashok Kumar](https://github.com/arahant) - Product Owner
2. [Arun Muthu](https://github.com/arungithub9)
3. [Hardik Rokad](https://github.com/hardikr586)
4. [Jiazhou Liu](https://github.com/602071349) - Agile Coach
5. [Kainat Naeem](https://github.com/kainattnaeem)

## Getting Started

### Database Schema

| Column | Data type | Condition |
| --- | --- | --- |
| `product_id` | `<integer>` | `product_id > 0` |
| `condition` | `<string>` | `<new/used/open box>` |
| `quantity` | `<integer>` | `quantity > 0` |
| `restock_level` | `<integer>` | `restock_level > 0` |
| `available` | `<integer>` | `available == 0/1` |

### API endpoints

| Method | URI | Description | Content-Type | Sample Payload |
| --- | --- | ------ | --- | ------- |
| `POST` | `https://nyu-inventory-service-f20.us-south.cf.appdomain.cloud/inventory` | Given the data body this creates an inventory record in the DB | application/json | <code>{<br>&nbsp;&nbsp;"product_id": 321,<br>&nbsp;&nbsp;"condition": "new",<br>&nbsp;&nbsp;"available": 1,<br>&nbsp;&nbsp;"quantity": 2,<br>&nbsp;&nbsp;"restock_level": 1<br>&nbsp;}<code> |
| `GET` | `https://nyu-inventory-service-f20.us-south.cf.appdomain.cloud/inventory` | Returns a collection of all inventories in the DB | N/A | N/A |
| `GET` | `https://nyu-inventory-service-f20.us-south.cf.appdomain.cloud/inventory?product_id=<int>` | Returns a collection of all inventories matching `product_id` | N/A | N/A |
| `GET` | `https://nyu-inventory-service-f20.us-south.cf.appdomain.cloud/inventory/<int:product_id>/condition/<string:condition>` | Returns the inventory record with the given `product_id` and `condition` | N/A | N/A |
| `PUT` | `https://nyu-inventory-service-f20.us-south.cf.appdomain.cloud/inventory/<int:product_id>/condition/<string:condition>` | Updates the inventory record with the given `product_id` and `condition` | application/json | <code>{<br>&nbsp;&nbsp;"available": 1,<br>&nbsp;&nbsp;"quantity": 2,<br>&nbsp;&nbsp;"restock_level": 1<br>&nbsp;}<code> |
| `PUT` | `https://nyu-inventory-service-f20.us-south.cf.appdomain.cloud/inventory/<int:product_id>/condition/<string:condition>/activate` | Given the `product_id` and `condition` this updates `available = 1` | N/A | N/A |
| `PUT` | `https://nyu-inventory-service-f20.us-south.cf.appdomain.cloud/inventory/<int:product_id>/condition/<string:condition>/deactivate` | Given the `product_id` and `condition` this updates `available = 0` | N/A | N/A |
| `PUT` | `https://nyu-inventory-service-f20.us-south.cf.appdomain.cloud/inventory/<int:product_id>/condition/<string:condition>/restock` | Given the `product_id`, `condition` and `amount` (body) this updates `quantity += amount` | application/json | `{"amount": 2}` |
| `DELETE` | `/inventory/<int:product_id>/condition/<string:condition>` | Given the `product_id` and `condition` this updates `available = 0` | N/A | N/A |


### Testing and Running locally

To run and test the code, you can use the following command:
```
git clone https://github.com/devops-fall-20-inventory/inventories.git
cd inventories
vagrant up
vagrant ssh
cd /vagrant
nosetests
pylint service
FLASK_APP=service:app flask run -h 0.0.0.0
```

1. You can type `nosetests` under `/vagrant` to check different test cases and the overall coverage. The coverage is displated by default.
2. PyLint should return a score more than 9.
3. Then you can test the APIs in the browser from you host machine, or on Postman (recommended).
