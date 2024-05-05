from django.test import TestCase
from django.utils import timezone
from purchase.models import PurchaseOrder
from vendors.models import Vendor, HistoricalPerformance
import uuid


class PurchaseOrderModelTest(TestCase):
    def setUp(self):
        """Set up non-modified objects used by all test methods."""
        self.vendor = Vendor.objects.create(
            name="Test Vendor",
            contact_details="test@example.com",
            address="123 Test Street",
        )
        self.po_number = str(uuid.uuid4()).replace("-", "")[:10].upper()
        self.po = PurchaseOrder.objects.create(
            po_number=self.po_number,
            vendor=self.vendor,
            delivery_date=timezone.now(),
            items={"item1": 10},
            quantity=10,
            status=PurchaseOrder.PENDING,
        )

    def test_purchase_order_creation(self):
        """Test the creation of a purchase order."""
        po = self.po
        self.assertEqual(po.vendor, self.vendor)
        self.assertEqual(po.status, PurchaseOrder.PENDING)
        self.assertEqual(po.quantity, 10)
        self.assertEqual(po.items, {"item1": 10})

    def test_po_number_auto_generation(self):
        """Test that the po_number field is auto-generated if not provided."""
        po = PurchaseOrder.objects.create(
            vendor=self.vendor,
            delivery_date=timezone.now(),
            items={"item2": 5},
            quantity=5,
            status=PurchaseOrder.PENDING,
        )
        self.assertNotEqual(po.po_number, self.po_number)
        self.assertNotEqual(po.po_number, "")

    def test_acknowledgment_date_upon_completion(self):
        """Test that the acknowledgment_date is set upon completion."""
        self.po.status = PurchaseOrder.COMPLETED
        self.po.save()
        self.po.refresh_from_db()
        self.assertIsNotNone(self.po.acknowledgment_date)

    def test_acknowledgment_date_upon_caneeled(self):
        """Test that the acknowledgment_date is set upon canceled."""
        self.po.status = PurchaseOrder.CANCELED
        self.po.save()
        self.po.refresh_from_db()
        self.assertIsNotNone(self.po.acknowledgment_date)

    def test_acknowledgment_date_not_set_on_pending(self):
        """Test that the acknowledgment_date is not set on pending orders."""
        self.assertIsNone(self.po.acknowledgment_date)

    def test_string_representation(self):
        """Test the string representation of the purchase order."""
        expected_string = f"Purchase Order #{self.po_number}"
        self.assertEqual(str(self.po), expected_string)

    def test_status_choices(self):
        '''
        testing another choice other than the pending, completed, canceled
        '''
        # with self.assertRaises(ValueError):
        self.po.status = 'ALMOST'
        self.po.save()
        self.po.refresh_from_db()

    def test_vendor_foreign_key(self):
        '''
        test that the vendor is  foreign key
        '''
        self.assertTrue(self.po in self.vendor.purchaseorder_set.all())
        self.assertEqual(self.vendor, self.po.vendor)
