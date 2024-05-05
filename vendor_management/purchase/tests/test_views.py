from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from django.utils import timezone
from rest_framework.test import APIClient
from datetime import timedelta
from purchase.models import PurchaseOrder, Vendor
from purchase.serializer import PurchaseOrderSerializer
import json


class PurchaseOrderAPITestCase(TestCase):
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
        # Create a sample vendor object
        self.vendor_data = {
            "name": "Test Vendor",
            "address": "123 Test Street",
            "contact_details": 701056056,
        }
        self.vendor = Vendor.objects.create(**self.vendor_data)
        # Create some sample purchase orders for the vendor
        self.purchase_order_data = {
            "po_number": 'wewe',
            "vendor": self.vendor,
            "order_date": "2023-05-01T10:00:00Z",
            "delivery_date": "2023-05-15T10:00:00Z",
            "items": '{"item1": 10}',
            "quantity": 10,
            "status": "PENDING",
            "quality_rating": 4.5,
            "issue_date": "2023-05-01T10:00:00Z",
        }
        self.purchase_order = PurchaseOrder.objects.create(
            **self.purchase_order_data)

    def test_create_or_list_purchase(self):
        # Test listing purchase orders
        response = self.client.get(reverse('create_or_list_purchase'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        # print(response.data)

    def test_creation_po(self):
        # Test creating a new purchase order
        new_order_data = {
            "po_number": 'testing',
            "vendor": self.vendor.id,
            "order_date": "2023-05-01T10:00:00Z",
            "delivery_date": "2023-05-15T10:00:00Z",
            "items": '{"item1": 10}',
            "quantity": 10,
            "status": "Pending",
            "quality_rating": 4.5,
            "issue_date": "2023-05-01T10:00:00Z",
            "acknowledgment_date": "2023-05-02T10:00:00Z",
        }
        response = self.client.post(
            reverse('create_or_list_purchase'),
            new_order_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        all_orders = self.vendor.purchaseorder_set.all()
        self.assertEqual(len(all_orders), 2)
        orders = all_orders.order_by('-order_date').first()
        self.assertNotEqual(orders.po_number, 'testing')
        self.assertEqual(orders.items, {"item1": 10})
        self.assertEqual(orders.quantity, 10)

    def test_creation_po_wrong_id(self):
        new_order_data = {
            "po_number": 'testing',
            "vendor": 34343434,
            "order_date": "2023-05-01T10:00:00Z",
            "delivery_date": "2023-05-15T10:00:00Z",
            "items": '{"item1": 10}',
            "quantity": 10,
            "status": "Pending",
            "quality_rating": 4.5,
            "issue_date": "2023-05-01T10:00:00Z",
            "acknowledgment_date": "2023-05-02T10:00:00Z",
        }
        response = self.client.post(
            reverse('create_or_list_purchase'),
            new_order_data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        all_orders = self.vendor.purchaseorder_set.all()
        self.assertEqual(len(all_orders), 1)

    def test_creation_po_wrong_status(self):
        new_order_data = {
            "po_number": 'testing',
            "vendor": 1,
            "order_date": "2023-05-01T10:00:00Z",
            "delivery_date": "2023-05-15T10:00:00Z",
            "items": '{"item1": 10}',
            "quantity": 10,
            "status": "Home",
            "quality_rating": 4.5,
            "issue_date": "2023-05-01T10:00:00Z",
            "acknowledgment_date": "2023-05-02T10:00:00Z",
        }
        response = self.client.post(
            reverse('create_or_list_purchase'),
            new_order_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        all_orders = self.vendor.purchaseorder_set.all()
        self.assertEqual(len(all_orders), 1)

    def test_get_purchase_order(self):
        # Test retrieving a purchase order
        response = self.client.get(
            reverse(
                'get_or_update_purchase_order',
                kwargs={
                    'purchase_order_id': 1}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('po_number'), 'wewe')

    def test_update_purchase_order(self):
        # Test updating a purchase order
        self.assertEqual(self.purchase_order.quantity, 10)
        updated_data = {'quantity': 555}
        response = self.client.put(
            reverse(
                'get_or_update_purchase_order', kwargs={
                    'purchase_order_id': 1}),
            data=updated_data,
            format='json'  # Specify the format as JSON
        )
        self.purchase_order.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.purchase_order.quantity, 555)
        self.assertEqual(response.data, 'Order updated successfully')

    def test_update_purchase_order_wrong_data(self):
        # Test updating a purchase order
        self.assertEqual(self.purchase_order.quantity, 10)
        updated_data = {'status': 'Not a status'}
        response = self.client.put(
            reverse(
                'get_or_update_purchase_order', kwargs={
                    'purchase_order_id': 1}),
            data=updated_data,
            format='json'  # Specify the format as JSON
        )
        self.purchase_order.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_PO(self):
        response = self.client.delete(
            reverse(
                'get_or_update_purchase_order', kwargs={
                    'purchase_order_id': self.purchase_order.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(PurchaseOrder.objects.count(), 0)

    def test_delete_vendor_wrong_id(self):
        '''
        Passing non existant id
        '''
        response = self.client.delete(
            reverse(
                'get_or_update_purchase_order',
                kwargs={
                    'purchase_order_id': 22}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_acknowledgment_completed(self):
        # Test updating the status of a purchase order
        new_acknowledgment_date = timezone.now().replace(microsecond=0)
        response = self.client.post(
            reverse(
                'update_acknowlegment', kwargs={
                    'purchase_order_id': 1}), {
                'status': "Completed"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.purchase_order.refresh_from_db()
        self.assertEqual(self.purchase_order.status, "Completed")
        self.assertAlmostEqual(
            self.purchase_order.acknowledgment_date,
            new_acknowledgment_date,
            delta=timedelta(
                seconds=1))

    def test_update_acknowledgment__canceled(self):
        # Test updating the acknowledgment date of a purchase order
        new_acknowledgment_date = timezone.now()
        response = self.client.post(
            reverse(
                'update_acknowlegment', kwargs={
                    'purchase_order_id': 1}), {
                'status': "Canceled"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.purchase_order.refresh_from_db()
        self.assertEqual(self.purchase_order.status, "Canceled")
        self.assertAlmostEqual(
            self.purchase_order.acknowledgment_date,
            new_acknowledgment_date,
            delta=timedelta(
                seconds=1))

    def test_update_acknowledgment_unknown_status(self):
        # Test updating the acknowledgment date of a purchase order
        new_acknowledgment_date = timezone.now().replace(microsecond=0)
        response = self.client.post(
            reverse(
                'update_acknowlegment', kwargs={
                    'purchase_order_id': 1}), {
                'status': 'UNKNOWN'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.purchase_order.refresh_from_db()
        self.assertEqual(self.purchase_order.status, "PENDING")

    def test_update_acknowledgment_no_status(self):
        # Test updating the acknowledgment date of a purchase order
        new_acknowledgment_date = timezone.now()
        response = self.client.post(
            reverse(
                'update_acknowlegment',
                kwargs={
                    'purchase_order_id': 1}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_acknowledgment_wrong_id(self):
        # Test updating the acknowledgment date of a purchase order
        new_acknowledgment_date = timezone.now()
        response = self.client.post(
            reverse(
                'update_acknowlegment', kwargs={
                    'purchase_order_id': 10}), {
                'acknowledgment_date': -23234234})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
