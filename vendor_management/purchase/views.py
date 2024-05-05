'''
This module defines end point for the class Purchse
'''
from django.shortcuts import get_object_or_404
from .models import PurchaseOrder
from vendors.models import Vendor, HistoricalPerformance
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .serializer import PurchaseOrderSerializer
import uuid
from django.core.cache import cache
from django.utils import timezone


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def create_or_list_purchase(request):
    '''
    Handles both the creation of a new purchase order
    and the listing of existing orders.

    GET Request:
    - Lists all purchase orders.
    - Pagination is supported,
    allowing the client to specify the page size for the results.

    POST Request:
    - Creates a new purchase order based on the provided data.

    Parameters:
    - `request`: The HTTP request object.

    Returns:
    - For GET requests, a list of purchase orders with pagination.
    - For POST requests, the newly created purchase order.
    '''
    if request.method == 'GET':
        vendor_id = request.query_params.get('vendor_id')
        # select purchases from the vendor
        if vendor_id:
            vendor = get_object_or_404(Vendor, id=vendor_id)
            all_orders = PurchaseOrder.objects.filter(
                vendor=vendor).order_by('id')
        else:
            # select all purchaseorder
            all_orders = PurchaseOrder.objects.all().order_by('id')
        try:
            page_number = request.query_params.get('page', 1)
            page_size = request.query_params.get('page_size', 10)
            p = Paginator(all_orders, page_size)

            page_obj = p.get_page(int(page_number))

        # if page is empty then return last page
        except EmptyPage:
            page_obj = p.page(p.num_pages)
        # if page_number is not an integer then assign the first page
        except (PageNotAnInteger, Exception):
            page_obj = p.page(1)
        finally:

            serialise = PurchaseOrderSerializer(page_obj, many=True)
            results = {
                'data': serialise.data,
                "next_page": page_obj.next_page_number() if
                page_obj.has_next() else None,
                "page": page_obj.number,
                "page_size": len(
                    page_obj.object_list),
                "prev_page": page_obj.previous_page_number() if
                page_obj.has_previous() else None,
                "total_pages": p.num_pages}
            return Response(results, status.HTTP_200_OK)
    # if the request method is POST
    # deserialiser from pyhton to django object with exception set to true
    vendor_id = request.data.get('vendor')
    try:
        vendor_id = int(vendor_id)

    except Exception as error:
        return Response(f'Error : {error}', status.HTTP_400_BAD_REQUEST)

    vendor = get_object_or_404(Vendor, id=vendor_id)
    data = request.data

    serializer = PurchaseOrderSerializer(data=data)
    if serializer.is_valid():
        # save the object
        serializer.save()
        po_number = serializer.data.get('po_number')
        return Response(
            f'Purchase Order PO number {po_number} created successfully',
            status.HTTP_201_CREATED)
    return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def get_or_update_purchase_order(request, purchase_order_id):
    """
    Handles retrieving, updating, or deleting a specific
    purchaseorder's details based on the request method.

    This function supports the following request methods:
    - GET: Retrieves the details of the specified purchaseorder.
    - PUT : Updates the details of the specified purchaseorder.
    - DELETE: Deletes the specified purchaseorder.

    Parameters:
    - request: The HTTP request object.
    - purchase_order_id: The unique identifier of the purchaseorder.

    Returns:
    - Response: A response object with the purchaseorder's details,
    a success message upon update or deletion,
    or an error message if the operation fails.

    Raises:
    - Http404: If the specified purchaseorder does not exist.
    - PermissionDenied: If the user does not have the
    required permissions to perform the operation.
    """
    # rettrive detail of a specified order
    order = get_object_or_404(PurchaseOrder, id=purchase_order_id)
    cached_data = cache.get(f'PO_{purchase_order_id}')
    
    if request.method == 'GET':
        # retrive the data of that order
        if cached_data:
            return Response(cached_data, status.HTTP_200_OK)
        serialise = PurchaseOrderSerializer(order)
        data = serialise.data
        cache.set(f'PO_{purchase_order_id}', data, timeout=600)
        print(data)
        return Response(data, status.HTTP_200_OK)
    elif request.method == 'PUT':
        # update the object
        serialise = PurchaseOrderSerializer(
            order, data=request.data, partial=True)
        if serialise.is_valid():
            serialise.save()
            return Response('Order updated successfully', status.HTTP_200_OK)
        return Response(serialise.errors, status.HTTP_400_BAD_REQUEST)
    # if the method is delete
    elif request.method == 'DELETE':
        name = order.po_number
        order.delete()
    return Response(f'Vendor: {name} created sucesfully deleted')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_acknowlegment(request, purchase_order_id):
    """
    Update the acknowledgment date of a specific purchase order.

    This view function updates the acknowledgment date of a purchase
    order specified by `purchase_order_id`.
    It expects the new acknowledgment date to be provided
    in the request data under the key 'acknowledgment_date'.

    Parameters:
    - request: The HTTP request object.
    - purchase_order_id: The ID of the purchase order to update.

    Returns:
    - A JSON response indicating success or failure of the update operation.
    """
    order = PurchaseOrder.objects.filter(id=purchase_order_id).first()
    if not order:
        return Response(
            f'Order with ID {purchase_order_id} does not exist.',
            status.HTTP_404_NOT_FOUND)

    status_ = request.data.get('status')
    if status_:
        data = {'status': status_}
        serialise = PurchaseOrderSerializer(order, data=data, partial=True)
        if serialise.is_valid():
            serialise.save()
            return Response(
                {f'Sucessfull update for order {purchase_order_id}'},
                status.HTTP_200_OK)
        return Response(serialise.errors, status.HTTP_400_BAD_REQUEST)
    return Response("Status must be passed", status.HTTP_400_BAD_REQUEST)
