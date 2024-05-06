from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from vendors.models import Vendor
from vendors.serializer import VendorSerializer
import json


class VendorAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.post(
            reverse('user-registration'),
            data=json.dumps({'username': 'bon', 'password': 'firefox123'}),
            content_type='application/json'
        )

        response = self.client.post(
            reverse('user-login'),
            data=json.dumps({'username': 'bon', 'password': 'firefox123'}),
            content_type='application/json'
        )
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        self.vendor_data = {
            "name": "Test Vendor",
            "address": "123 Test Street",
            "contact_details": 701056056,
        }
        self.vendor = Vendor.objects.create(**self.vendor_data)

    def test_create_vendor(self):
        response = self.client.post(
            reverse('create_or_list_vendor'),
            self.vendor_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, 'Vendor created sucesfully')

    def test_create_vendor_wrong_data(self):
        data = {
            "address": "123 Test Street",
            "contact_details": 701056056,
        }
        response = self.client.post(reverse('create_or_list_vendor'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_vendors(self):
        response = self.client.get(reverse('create_or_list_vendor'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('data')), 1)
        self.assertEqual(response.data.get('page_size'), 1)
        self.assertEqual(response.data.get('next_page'), None)
        self.assertEqual(response.data.get('page'), 1)
        self.assertEqual(response.data.get('prev_page'), None)

    def test_list_vendors_pagination(self):
        response = self.client.post(
            reverse('create_or_list_vendor'),
            self.vendor_data)
        response = self.client.get(reverse('create_or_list_vendor'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('data')), 1)
        self.assertEqual(response.data.get('page_size'), 1)
        self.assertEqual(response.data.get('next_page'), None)
        self.assertEqual(response.data.get('page'), 1)
        self.assertEqual(response.data.get('prev_page'), None)

    def test_update_vendor(self):
        new_data = {
            "name": "Updated Vendor",
        }
        response = self.client.put(
            reverse(
                'get_or_update_vendor',
                kwargs={
                    'vendor_id': self.vendor.id}),
            new_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.vendor.refresh_from_db()
        self.assertEqual(self.vendor.name, "Updated Vendor")

    def test_update_vendor_wrong_id(self):
        '''
        passing a wrong id will result in a 404
        '''
        new_data = {
            "not an attribute": "Updated Vendor",
        }
        response = self.client.put(
            reverse(
                'get_or_update_vendor',
                kwargs={
                    'vendor_id': 13}),
            new_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_vendor_wrong_data(self):
        '''
        if a wrong field is passed, the system just igores it, no errors
        '''
        new_data = {
            "not an attribute": "Updated Vendor",
        }
        response = self.client.put(
            reverse(
                'get_or_update_vendor',
                kwargs={
                    'vendor_id': self.vendor.id}),
            new_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.vendor.refresh_from_db()
        self.assertNotIn("not an attribute", self.vendor.__dict__)

    def test_delete_vendor(self):
        response = self.client.delete(
            reverse(
                'get_or_update_vendor', kwargs={
                    'vendor_id': self.vendor.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Vendor.objects.count(), 0)

    def test_delete_vendor_wrong_id(self):
        '''
        Passing non existant id
        '''
        response = self.client.delete(
            reverse(
                'get_or_update_vendor',
                kwargs={
                    'vendor_id': 22}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_vendor(self):
        # Make a GET request to the endpoint
        response = self.client.get(
            reverse(
                'get_or_update_vendor',
                kwargs={
                    'vendor_id': self.vendor.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.vendor.id)

    def test_retrieve_vendor_wrong_id(self):
        '''
        passsing wrong id
        '''
        response = self.client.get(
            reverse(
                'get_or_update_vendor',
                kwargs={
                    'vendor_id': 55}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_view_performance(self):

        response = self.client.get(
            reverse(
                'view_performance', kwargs={
                    'vendor_id': self.vendor.id}))
        # Assert that the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assert that the response data contains the expected performance data
        self.assertEqual(response.data['vendor_id'], self.vendor.id)
        self.assertEqual(response.data['on_time_delivery_rate'], 0)
        self.assertEqual(response.data['quality_rating_avg'], 0)
        self.assertEqual(response.data['average_response_time'], 0)
        self.assertEqual(response.data['fulfillment_rate'], 0)

    def test_view_performance(self):

        response = self.client.get(
            reverse(
                'view_performance',
                kwargs={
                    'vendor_id': 333}))
        # Assert that the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
