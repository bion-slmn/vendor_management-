'''
This module regiister endpoints to view fuctions
'''

from django.urls import path
from . import views

urlpatterns = [
    # list all vendors or create purchaseOrder
    path('', views.create_or_list_purchase, name='create_or_list_purchase'),
    # update, delete or get  a vendor with a given id
    path('<int:purchase_order_id>/',
         views.get_or_update_purchase_order,
         name='get_or_update_purchase_order'),
    path(
        '<int:purchase_order_id>/acknowledge/',
        views.update_acknowlegment,
        name='update_acknowlegment')

]
