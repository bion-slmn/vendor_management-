 curl -X POST localhost:8000/api/vendor/ -H "Content-Type: application/json" -d '{"name": "bon", "contact_details": "53333333", "address": "kakamega"}'
bion@Giantinmakin:~/projects/vendor_management-$ curl localhost:8000/api/vendor/
{"Vendors":[{"id":1,"name":"bon","contact_details":"53333333","address":"kakamega","vendor_code":"482C35458D","on_time_delivery_rate":0.0,"quality_rating_avg":0.0,"average_response_time":0.0,"fulfillment_rate":0.0}]}

curl -X POST localhost:8000/api/vendor/ -H "Content-Type: application/json" -d '{"name": "bon", "contact_details": "53333333"}'
{"address":["This field is required."]}

 curl -X PUT localhost:8000/api/vendor/1/ -H "Content-Type: application/json" -d '{"name": "bion", "contact_details": "0701036054"}'

 curl -X DELETE localhost:8000/api/vendor/1/ -H "Content-Type: application/json" -d '{"name": "bion", "contact
_details": "0701036054"}'
 
 curl -X POST localhost:8000/api/purchase_orders/2/acknowledge/  -H "Content-Type:application/json" -d '{"acknowledgment_date": "2024-05-03"}'