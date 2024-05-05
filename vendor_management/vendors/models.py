'''
defines models for vendor
'''
from django.db import models
import uuid


class Vendor(models.Model):
    '''
    Represents a vendor entity.

    Attributes:
        name (str): The name of the vendor.
        contact_details (str): The contact information of the vendor. (unique)
        address (str): The physical address of the vendor.
        vendor_code (str): A unique identifier for the vendor.
            (auto-generated, unique)
        on_time_delivery_rate (float): The percentage of on-time deliveries.
            (default: 0.0)
        quality_rating_avg (float): The average rating of quality.
            (default: 0.0)
        average_response_time (float): The average time taken to
            acknowledge purchase orders. (default: 0.0)
        fulfillment_rate (float): The percentage of purchase orders
            fulfilled successfully. (default: 0.0)

    Note:
        The 'vendor_code' attribute is auto-generated and cannot be edited.
    '''
    name = models.CharField(max_length=70)
    contact_details = models.TextField()
    address = models.TextField()
    vendor_code = models.CharField(max_length=100, unique=True, editable=False)
    on_time_delivery_rate = models.FloatField(default=0.0)
    quality_rating_avg = models.FloatField(default=0.0)
    average_response_time = models.FloatField(default=0.0)
    fulfillment_rate = models.FloatField(default=0.0)

    def __str__(self):
        '''
        Returns a string representation of the vendor.

        Returns:
            str: The string representation of the vendor.
        '''
        return self.name

    def save(self, *args, **kwargs):
        '''
    Save the Vendor instance.

    If the 'vendor_code' field is not set, generate a unique identifier
        and set it as the 'vendor_code'.
    Then, save the Vendor instance to the database.

    Parameters:
        *args: Additional positional arguments to
            pass to the parent class's save method.
        **kwargs: Additional keyword arguments to pass
            to the parent class's save method.

    Example:
        To save a Vendor instance:
        ```python
        vendor_instance = Vendor(name='Example Vendor',
            contact='example@example.com')
        vendor_instance.save()
        ```
    '''
        if not self.vendor_code:
            self.vendor_code = str(uuid.uuid4()).replace("-", "")[:10].upper()
        super(Vendor, self).save(*args, **kwargs)


class HistoricalPerformance(models.Model):
    '''
    Model to optionally store historical data on vendor performance
        for trend analysis.

    Attributes:
        vendor (ForeignKey): Link to the Vendor model.
        date (DateTime): Date of the performance record.
        on_time_delivery_rate (float): Historical record
            of the on-time delivery rate.
        quality_rating_avg (float): Historical
            record of the quality rating average.
        average_response_time (float): Historical
            record of the average response time.
        fulfillment_rate (float): Historical record of the fulfillment rate.
    '''

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    on_time_delivery_rate = models.FloatField(default=0.0)
    quality_rating_avg = models.FloatField(default=0.0)
    average_response_time = models.FloatField(default=0.0)
    fulfillment_rate = models.FloatField(default=0.0)

    def __str__(self):
        '''
        Returns a string representation of the historical performance record.

        Returns:
            str: The string representation of the historical
                performance record.
        '''
        return f"Historical Performance for {self.vendor.name} on {self.date}"

    def save(self, *args, **kwargs):
        # Retrieve the most recent record for the same vendor
        previous_record = HistoricalPerformance.objects.filter(
            vendor=self.vendor).order_by('-date').first()
        if previous_record:
            # Iterate over the attributes of the current instance
            for attr in self._meta.get_fields():
                # Check if the attribute is a field (excluding ForeignKey,
                # ManyToManyField, etc.)
                if isinstance(
                        attr, models.Field) and getattr(
                        self, attr.name) == 0.0:
                    setattr(
                        self, attr.name, getattr(
                            previous_record, attr.name))

        # Call the parent class's save method to save the updated instance
        super().save(*args, **kwargs)
