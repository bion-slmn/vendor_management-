from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.utils import timezone
from datetime import datetime
from vendors.models import Vendor, HistoricalPerformance


class VendorModelTest(TestCase):
    def setUp(self):
        """Set up non-modified objects used by all test methods."""
        self.vendor = Vendor.objects.create(
            name="Test Vendor",
            contact_details="test@example.com",
            address="123 Test Street",
        )

    def test_vendor_creation(self):
        """Test the creation of a vendor."""
        vendor = self.vendor
        self.assertEqual(vendor.name, "Test Vendor")
        self.assertEqual(vendor.contact_details, "test@example.com")
        self.assertEqual(vendor.address, "123 Test Street")
        # Assuming vendor_code is auto-generated
        self.assertNotEqual(vendor.vendor_code, "Test Vendor")

    def test_vendor_code_is_unique(self):
        """Test that the vendor_code field is unique."""
        code = self.vendor.vendor_code
        with self.assertRaises(IntegrityError):
            Vendor.objects.create(
                name="Another Vendor",
                contact_details="another@example.com",
                address="456 Another Street",
                vendor_code=code,
            )

    def test_vendor_code_is_auto_generated(self):
        """Test that the vendor_code field is auto-generated."""
        vendor = Vendor.objects.create(
            name="Auto Vendor",
            contact_details="auto@example.com",
            address="789 Auto Street",
        )
        self.assertNotEqual(vendor.vendor_code, self.vendor.vendor_code)
        self.assertNotEqual(vendor.vendor_code, "")

    def test_default_values(self):
        """Test that the default values
        for the model fields are set correctly."""
        self.assertEqual(self.vendor.on_time_delivery_rate, 0.0)
        self.assertEqual(self.vendor.quality_rating_avg, 0.0)
        self.assertEqual(self.vendor.average_response_time, 0.0)
        self.assertEqual(self.vendor.fulfillment_rate, 0.0)

    def test_on_time_delivery_rate_isNumber(self):
        """Test that the vendor_code field is not editable."""
        with self.assertRaises(ValueError):
            self.vendor.vendor_code = "New Code"
            self.vendor.on_time_delivery_rate = 'dddd'
            self.vendor.save()

    def test_quality_rating_avg_isnNumber(self):
        """Test that the average response is a number"""
        with self.assertRaises(ValueError):
            self.vendor.quality_rating_avg = 'dddd'
            self.vendor.save()

    def test_av_response_is_a_number(self):
        """Test that the average response is a number"""
        with self.assertRaises(ValueError):
            self.vendor.average_response_time = 'dddd'
            self.vendor.save()

    def test_fullfilment_rate(self):
        """Test that the average response is a number"""
        with self.assertRaises(ValueError):
            self.vendor.fulfillment_rate = 'dddd'
            self.vendor.save()


class HistoricalPerformanceModelTest(TestCase):
    def setUp(self):
        """Set up non-modified objects used by all test methods."""
        self.vendor = Vendor.objects.create(
            name="Test Vendor",
            contact_details="test@example.com",
            address="123 Test Street",
        )
        self.performance = HistoricalPerformance.objects.create(
            vendor=self.vendor,
            on_time_delivery_rate=0.9,
            quality_rating_avg=4.5,
            average_response_time=1.5,
            fulfillment_rate=0.85,
        )

    def test_historical_performance_creation(self):
        """Test the creation of a historical performance record."""
        performance = self.performance
        self.assertEqual(performance.on_time_delivery_rate, 0.9)
        self.assertEqual(performance.quality_rating_avg, 4.5)
        self.assertEqual(performance.average_response_time, 1.5)
        self.assertEqual(performance.fulfillment_rate, 0.85)
        self.assertIsInstance(performance.date, datetime)

    def test_string_representation(self):
        """Test the string representation of the historical
        performance record."""
        expected_string = "Historical Performance for {} on {}".format(
            self.vendor.name, self.performance.date)
        self.assertEqual(str(self.performance), expected_string)

    def test_default_values(self):
        """Test that the default values for the model
        fields are set correctly."""
        performance = HistoricalPerformance.objects.create(vendor=self.vendor)
        self.assertEqual(performance.on_time_delivery_rate, 0.9)
        self.assertEqual(performance.quality_rating_avg, 4.5)
        self.assertEqual(performance.average_response_time, 1.5)
        self.assertEqual(performance.fulfillment_rate, 0.85)

    def test_date_auto_now(self):
        """Test that the date field is automatically set to the
            current date and time."""
        self.assertAlmostEqual(
            self.performance.date,
            timezone.now(),
            delta=timezone.timedelta(
                seconds=1))

    def test_on_time_delivery_rate_isNumber(self):
        """Test that the vendor_code field is not editable."""
        with self.assertRaises(ValueError):
            self.performance.on_time_delivery_rate = 'dddd'
            self.performance.save()

    def test_quality_rating_avg_isnNumber(self):
        """Test that the average response is a number"""
        with self.assertRaises(ValueError):
            self.performance.quality_rating_avg = 'dddd'
            self.performance.save()

    def test_av_response_is_a_number(self):
        """Test that the average response is a number"""
        with self.assertRaises(ValueError):
            self.performance.average_response_time = 'dddd'
            self.performance.save()

    def test_fullfilment_rate(self):
        """Test that the average response is a number"""
        with self.assertRaises(ValueError):
            self.performance.fulfillment_rate = 'dddd'
            self.performance.save()

    def test_vendor_foreign_key(self):
        '''
        test that the vendor is  foreign key
        '''
        self.assertTrue(
            self.performance in self.vendor.historicalperformance_set.all())
        self.assertEqual(self.vendor, self.performance.vendor)
