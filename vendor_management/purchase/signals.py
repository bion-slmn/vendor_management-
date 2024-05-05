'''
create a signals to update the database

'''
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import datetime
from vendors.models import Vendor, HistoricalPerformance
from django.db.models import F, Avg, Sum, Count, Case, When
from purchase.models import PurchaseOrder


def update_vendor_delivery_rate(
        instance: PurchaseOrder,
        vendor: Vendor) -> float:
    '''
    Calculate the on-time delivery rate whenever a
        purchase order is updated.

    Parameters:
        instance (PurchaseOrder): The instance of the purchase
            order being updated.
        vendor (Vendor): The vendor associated with
            the purchase order.

    Returns:
        float: The delivery rate as a percentage .
    '''

    if instance.status == 'Completed':
        # get all the vendor from the purchse ordr
        completed_orders = PurchaseOrder.objects.filter(
            vendor=vendor, status='Completed')
        # Initialize counters for all orders and delivered on time

        delivered_on_time = len(completed_orders.filter(
            acknowledgment_date__lte=F('delivery_date')
        ))
        all_orders = len(completed_orders)
        # Calculate delivery rate (avoid division by zero)
        if all_orders:
            delivery_rate = (delivered_on_time / all_orders)
            delivery_rate = delivered_on_time / all_orders
            return round(delivery_rate, 2)
    return 0.0


def calculate_quality_rating(vendor, instance):
    ''''
    Calculate the average rating of quality when a new purchase order.

    Parameters:
        instance (PurchaseOrder): The instance of the purchase order
            being updated.
        vendor (Vendor): The vendor associated with the purchase order.

    Returns:
        float: The average quality rating.
    '''
    if instance.quality_rating and instance.status == 'Completed':

        rating = PurchaseOrder.objects.filter(
            vendor=vendor,
            quality_rating__isnull=False).aggregate(
            Avg('quality_rating', default=0.0))
        return round(rating['quality_rating__avg'], 1)


def calculate_average_response_time(vendor, instance):
    '''
    Calculate the average response time for a vendor.

    Parameters:
        instance (PurchaseOrder): The instance of the purchase order
            being updated.
        vendor (Vendor): The vendor associated with the purchase order.

    Returns:
        float: The average quality rating.
    '''
    if instance.acknowledgment_date:
        # Filter acknowledged PurchaseOrders for the vendor
        acknowledged_orders = PurchaseOrder.objects.filter(
            vendor=vendor,
            acknowledgment_date__isnull=False
        )

        # Calculate the total response time directly in the database
        total_response_time = acknowledged_orders.aggregate(
            total_seconds=Sum(F('acknowledgment_date') - F('issue_date'))
        )['total_seconds']
        total_orders = len(acknowledged_orders)
        # Calculate the average response time
        if total_orders:
            average_response_time = \
                total_response_time.total_seconds() / total_orders
            return average_response_time

# use post save to update the database


def calculate_fullfillment_rate(instance, vendor):
    '''
    Calculate the fulfillment rate for a
        vendor's Purchase Orders before saving.

    Parameters:
        insatance The sender of the signal.
        vendor: the vendor of the instance
    '''

    if instance.status == 'Completed' or instance.status == 'Canceled':
        # Check if the status has changed :
        # calculate the total number of PO of that vendor
        completed_orders, total_orders = PurchaseOrder.objects.filter(
            vendor=vendor).aggregate(
            completed_orders=Count(
                Case(
                    When(
                        status='Completed', then=1))),
            total_orders=Count('id')).values()
        if total_orders:
            fulfillment_rate = completed_orders / total_orders
        # Update the vendor's fulfillment ra
            return round(fulfillment_rate, 2)


@receiver(post_save, sender=PurchaseOrder)
def update_performance(sender, instance, raw, **kwargs):
    '''
    Update vendor performance metrics when a
        new purchase order is created or updated.

    Parameters:
        sender: The sender of the signal.
        instance (PurchaseOrder): The instance of the
            purchase order being updated.
        created (bool): True if a new purchase order
            is created, False if it's an update.

    Returns:
        None
    '''

    vendor = instance.vendor
    attributes = {'vendor': vendor}

    data = {
        'on_time_delivery_rate': update_vendor_delivery_rate(instance, vendor),
        'average_response_time':
            calculate_average_response_time(vendor, instance),
        'fulfillment_rate': calculate_fullfillment_rate(instance, vendor),
        'quality_rating_avg': calculate_quality_rating(vendor, instance),
    }

    for key, value in data.items():
        if value is not None:
            attributes.update({key: value})
            setattr(vendor, key, value)

    vendor.save()

    # Save historical performance
    HistoricalPerformance.objects.create(**attributes)
