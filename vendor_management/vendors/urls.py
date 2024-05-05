'''
This module regiister endpoints to view fuctions
'''

from django.urls import path
from . import views

urlpatterns = [
    # list all vendors or create vendors
    path('', views.create_or_list_vendor, name='create_or_list_vendor'),
    # update, delete or get  a vendor with a given id
    path(
        '<int:vendor_id>/',
        views.get_or_update_vendor,
        name='get_or_update_vendor'),
    # view performance
    path(
        '<int:vendor_id>/performance',
        views.view_performance,
        name='view_performance'),
]
