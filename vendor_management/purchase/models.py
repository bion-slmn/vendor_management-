'''
This module defines the purchase order model
'''
from django.utils import timezone
from django.db import models
from vendors.models import Vendor
import uuid


class PurchaseOrder(models.Model):
    '''
    Model to capture the details of each purchase order.

    Attributes:
        po_number (str): Unique number identifying the purchase order.
        vendor (ForeignKey): Link to the Vendor model.
        order_date (DateTime): Date when the order was placed.
        delivery_date (DateTime): Expected or actual delivery date
            of the order.
        items (dict): Details of items ordered (in JSON format).
        quantity (int): Total quantity of items in the purchase order.
        status (str): Current status of the purchase order
            (e.g., pending, completed, canceled).
        quality_rating (float): Rating given to the vendor
            for this purchase order (nullable).
        issue_date (DateTime): Timestamp when the purchase
            order was issued to the vendor.
        acknowledgment_date (DateTime, nullable):
            Timestamp when the vendor acknowledged the purchase order.
    '''
    PENDING = 'Pending'
    COMPLETED = 'Completed'
    CANCELED = 'Canceled'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (CANCELED, 'Canceled'),
    ]

    po_number = models.CharField(max_length=100, unique=True, editable=False)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now=True)
    delivery_date = models.DateTimeField()
    items = models.JSONField()
    quantity = models.IntegerField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=PENDING,
    )
    quality_rating = models.FloatField(null=True)
    issue_date = models.DateTimeField(auto_now_add=True)
    acknowledgment_date = models.DateTimeField(null=True)

    def __str__(self):
        '''
        Returns a string representation of the purchase order.

        Returns:
            str: The string representation of the purchase order.
        '''
        return f"Purchase Order #{self.po_number}"

    def save(self, *args, **kwargs):
        '''
        Save the PurchaseOrder instance.

        If the 'po_number' field is not set, generate a unique
            identifier and set it as the 'po_number'.
        When the order status transitions to 'completed',
            update the acknowledgment_date to the current timestamp.
        Then, save the PurchaseOrder instance to the database.

        Parameters:
            *args: Additional positional arguments to pass
                to the parent class's save method.
            **kwargs: Additional keyword arguments to pass
                to the parent class's save method.

        Example:
            To save a PurchaseOrder instance:
            ```python
            purchase_order_instance =
                PurchaseOrder(vendor=my_vendor, delivery_date=my_delivery_date)
            purchase_order_instance.save()
        ```
        '''

        if not self.po_number:
            self.po_number = str(uuid.uuid4()).replace("-", "")[:10].upper()

        if (self.status == 'Completed' or self.status ==
                'Canceled') and not self.acknowledgment_date:
            self.acknowledgment_date = timezone.now()

        super(PurchaseOrder, self).save(*args, **kwargs)
