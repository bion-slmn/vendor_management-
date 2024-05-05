# VENDOR MANAGEMENT SYSTEM
![Untitled-design-9](https://github.com/bion-slmn/vendor_management-/assets/122830539/82824574-89f3-4097-a859-47f5fb2e2a56)


This vendor managment system is built with python django and Linux
This system will handle vendor proﬁles, track purchase orders, and calculate vendor performance metrics

## USAGE
### Install required libraries
```
pip install -r requirements.txt
```
### Start redis server and django server
Navigate to vendor_management
On linux
```
cd vendor_management
```
```
sudo service redis-server start
python3 manage.py runserver
```

### System registration
User has to regiseter inorder to be given permission to access other API endpoint
To register as user in the app use the end point

### POST /api/user/register/
Example
```
curl -X POST localhost:8000/api/user/register/  -H "Content-Type: application/json" -d '{"username": "bon", "password": "firefox123"}' 
```

### Getting Token and Logining in:
Token is given when the user logs in, user the end point 
### POST /api/user/login/ 
```
curl -X POST localhost:8000/api/user/login/  -H "Content-Type: application/json" -d '{"username": "bon", "password": "firefox123"}'

Returns
"token": "3dc4723334deaa24c28863f977b1073462f25aca" 
```

### Vendor profile management APIS

### POST /api/vendors/: 
  Create a newvendor. 

### GET /api/vendors/?page_size=any_number&page=any_number:

Fetch a paginated list of vendors, with options to specify the page size and page number.
default is page = 1 and page_size=10

> Example: This example returns only the first page and the first 10 vendors

```
   curl  http://localhost:8000/api/vendor/    -H "Content-Type: application/json"   -H "Authorization: Token  3dc4723334deaa24c28863f977b1073462f25aca"
```
```
   Returns data showing information on next page, previous page  as shown below

   {
  "data": [
    {
      "id": 1,
      "vendor_code": "7FA1923A14",
      "name": "bion",
      "contact_details": "0701036054",
      "address": "kakamega",
      "on_time_delivery_rate": 0.0,
      "quality_rating_avg": 0.0,
      "average_response_time": -71872.70573766666,
      "fulfillment_rate": 0.3333333333333333
    }
  ],
  "next_page": null,
  "page": 1,
  "page_size": 1,
  "prev_page": null,
  "total_pages": 1
}

```
### GET /api/vendors/{vendor_id}/: 
  Retrieve a speciﬁc vendor's details. 
### PUT /api/vendors/{vendor_id}/: 
   Update a vendor's details. 
###  DELETE /api/vendors/{vendor_id}/: 
   Delete a vendor

##   Purchase Order Tracking
API Endpoints for purchase order: 
### POST /api/purchase_orders/
Create a purchase order. 
 
### GET /api/purchase_orders/?page_size=<any_number>&page=<any_number>&vendor_id=vendor_id 
    Fetch a paginated list of purchase orders with an option to ﬁlterby vendor and 
    options to specify the page size and page number 
    default is page = 1 and page_size=10
    if no vendor_id is passed, all the puurchase order will be fetched in bacthes of 10
    ```
    curl  http://localhost:8000/api/purchase_orders/    -H "Content-Type: application/json"   -H "Authorization: Token  3dc4723334deaa24c28863f977b1073462f25aca"
    ```
```  
    Returns data with page information as shown
    {
  "data": [
    {
      "id": 2,
      "po_number": "73635DF01C",
      "order_date": "2024-05-04T13:28:05.454946+03:00",
      "delivery_date": "2024-05-03T15:00:00+03:00",
      "items": {
        "item1": "description1",
        "item2": "description2"
      },
      "quantity": 105,
      "status": "Canceled",
      "quality_rating": 55.0,
      "issue_date": "2024-05-04T13:28:05.454958+03:00",
      "acknowledgment_date": "2024-05-03T03:00:00+03:00",
      "vendor": 1
    },
    {
      "id": 3,
      "po_number": "B9BD04F7B9",
      "order_date": "2024-05-02T07:52:18.683278+03:00",
      "delivery_date": "2024-05-03T15:00:00+03:00",
      "items": {
        "item1": "description1",
        "item2": "description2"
      },
      "quantity": 105,
      "status": "Completed",
      "quality_rating": 3.5,
      "issue_date": "2024-05-02T07:52:18.683291+03:00",
      "acknowledgment_date": "2024-05-01T15:00:00+03:00",
      "vendor": 1
    },
    {
      "id": 4,
      "po_number": "40DFD04690",
      "order_date": "2024-05-01T23:33:13.978738+03:00",
      "delivery_date": "2024-05-03T15:00:00+03:00",
      "items": {
        "item1": "description1",
        "item2": "description2"
      },
      "quantity": 10,
      "status": "P",
      "quality_rating": 4.5,
      "issue_date": "2024-05-01T23:33:13.978964+03:00",
      "acknowledgment_date": "2024-05-01T15:00:00+03:00",
      "vendor": 1
    }
  ],
  "next_page": null,
  "page": 1,
  "page_size": 3,
  "prev_page": null,
  "total_pages": 1
}

```

### GET /api/purchase_orders/{po_id}/ 
 Retrieve details of a speciﬁc purchase order. 
### PUT /api/purchase_orders/{po_id}/ 
  Update a purchase order. 
###  DELETE /api/purchase_orders/{po_id}/ 
  Delete a purchase order.

##  Vendor Performance Endpoint 
### GET /api/vendors/{vendor_id}/performance 
   Get the performance metric of a vendor 
