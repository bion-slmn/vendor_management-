from django.test import TestCase
from django.utils import timezone
from purchase.models import PurchaseOrder
from vendors.models import Vendor, HistoricalPerformance
import uuid
import pytz
from datetime import datetime


class PurchaseOrderModelBacklogicTest(TestCase):
    '''
    test the back logic in the signals that occurs after saving
    '''

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

    def test_HistoricalPerformance_created(self):
        """
        test that HistoricalPerformance is created on purchase order

        """
        self.assertIsNotNone(self.vendor.historicalperformance_set.all())
        self.assertEqual(len(self.vendor.historicalperformance_set.all()), 1)
        #
        self.assertEqual(self.vendor.on_time_delivery_rate, 0.0)
        self.assertEqual(self.vendor.fulfillment_rate, 0.0)
        self.assertEqual(self.vendor.average_response_time, 0.0)
        self.assertEqual(self.vendor.quality_rating_avg, 0.0)

    def test_deliverytime_updated(self):
        """
        test that the delivery time is updated
        """
        PurchaseOrder.objects.create(
            vendor=self.vendor,
            delivery_date=timezone.now(),
            items={"item1": 10},
            quantity=10,
            status='Completed',
            acknowledgment_date="2024-03-01 16:53:24.012367+00:00")
        PurchaseOrder.objects.create(
            vendor=self.vendor,
            delivery_date=timezone.now(),
            items={
                "item1": 10},
            quantity=10,
            status='Completed',
            acknowledgment_date=datetime(
                2024,
                11,
                20,
                20,
                8,
                7,
                127325,
                tzinfo=pytz.UTC))
        PurchaseOrder.objects.create(
            vendor=self.vendor,
            delivery_date=timezone.now(),
            items={"item1": 10},
            quantity=10,
            status='Completed',
            acknowledgment_date="2024-05-01 16:53:24.012367+00:00")

        self.assertEqual(self.vendor.on_time_delivery_rate, 0.67)
        self.assertEqual(len(self.vendor.historicalperformance_set.all()), 4)
        self.po.status = 'Completed'
        self.po.save()
        history = self.vendor.historicalperformance_set.all().order_by(
            '-date').first()
        self.assertEqual(self.vendor.on_time_delivery_rate, 0.5)
        self.assertEqual(history.on_time_delivery_rate, 0.5)

    def test_calculate_quality_rating(self):
        """Test that the vendor's quality rating is calculated correctly."""
        self.po.quality_rating = 4.5
        self.po.status = PurchaseOrder.COMPLETED
        self.po.save()
        self.vendor.refresh_from_db()
        self.assertEqual(self.vendor.quality_rating_avg, 4.5)
        history = self.vendor.historicalperformance_set.all().order_by(
            '-date').first()
        self.assertEqual(history.quality_rating_avg, 4.5)

        PurchaseOrder.objects.create(
            vendor=self.vendor,
            delivery_date=timezone.now(),
            items={"item1": 10},
            quantity=10,
            status='Completed',
            quality_rating=6.5,)

        self.assertEqual(self.vendor.quality_rating_avg, 5.5)
        history = self.vendor.historicalperformance_set.all().order_by(
            '-date').first()
        self.assertEqual(history.quality_rating_avg, 5.5)
        PurchaseOrder.objects.create(
            vendor=self.vendor,
            delivery_date=timezone.now(),
            items={"item1": 10},
            quantity=10,
            status='Canceled')
        self.assertEqual(self.vendor.quality_rating_avg, 5.5)
        history = self.vendor.historicalperformance_set.all().order_by(
            '-date').first()
        self.assertEqual(history.quality_rating_avg, 5.5)

    def test_calculate_average_response_time(self):
        """Test that the vendor's average response time
        is calculated correctly."""
        self.po.acknowledgment_date = datetime(
            2024, 5, 4, 22, 53, 24, 12367, tzinfo=timezone.utc)
        self.po.save()
        self.vendor.refresh_from_db()
        avg_ = (
            self.po.acknowledgment_date -
            self.po.issue_date).total_seconds()
        self.assertEqual(self.vendor.average_response_time, avg_)
        history = self.vendor.historicalperformance_set.all().order_by(
            '-date').first()
        self.assertEqual(history.average_response_time, avg_)

        # when acknowledgment_date is None
        self.po.acknowledgment_date = None
        self.po.save()
        self.vendor.refresh_from_db()
        self.assertEqual(self.vendor.average_response_time, avg_)
        history = self.vendor.historicalperformance_set.all().order_by(
            '-date').first()
        self.assertEqual(history.average_response_time, avg_)

    def test_calculate_fulfillment_rate(self):
        """Test that the vendor's fulfillment rate is calculated correctly."""
        # when status is completed
        self.po.status = PurchaseOrder.COMPLETED
        self.po.save()
        self.vendor.refresh_from_db()
        self.assertGreater(self.vendor.fulfillment_rate, 0.0)
        self.assertEqual(self.vendor.fulfillment_rate, 1.0)
        history = self.vendor.historicalperformance_set.all().order_by(
            '-date').first()
        self.assertEqual(history.fulfillment_rate, 1.0)

        # when status is not complete or cancoeld
        PurchaseOrder.objects.create(
            vendor=self.vendor,
            delivery_date=timezone.now(),
            items={"item1": 10},
            quantity=10,
            status='qwqwq')
        self.assertGreater(self.vendor.fulfillment_rate, 0.0)
        self.assertEqual(self.vendor.fulfillment_rate, 1.0)
        history = self.vendor.historicalperformance_set.all().order_by(
            '-date').first()
        self.assertEqual(history.fulfillment_rate, 1.0)

        # when status is canceled
        PurchaseOrder.objects.create(
            vendor=self.vendor,
            delivery_date=timezone.now(),
            items={"item1": 10},
            quantity=10,
            status='Canceled')
        self.assertGreater(self.vendor.fulfillment_rate, 0.0)
        self.assertEqual(self.vendor.fulfillment_rate, 0.33)
        history = self.vendor.historicalperformance_set.all().order_by(
            '-date').first()
        self.assertEqual(history.fulfillment_rate, 0.33)

    def test_historical_performance_creation(self):
        """Test that a HistoricalPerformance record is
        created when a PurchaseOrder is updated."""
        self.po.status = PurchaseOrder.COMPLETED
        self.po.save()
        historical_performance = HistoricalPerformance.objects.filter(
            vendor=self.vendor).first()
        self.assertIsNotNone(historical_performance)
        self.assertEqual(historical_performance.vendor, self.vendor)
