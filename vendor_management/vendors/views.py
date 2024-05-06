'''
This module defines  API endpoints
'''
from django.shortcuts import get_object_or_404
from .models import Vendor, HistoricalPerformance
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .serializer import VendorSerializer, HistoricalPerformanceSerializer
import uuid
from django.core.cache import cache
# Create your views here.


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def create_or_list_vendor(request):
    """
    Handles creating a new vendor or listing existing vendors

    This function supports the following request methods:
    - GET: Lists vendors, with pagination support.
            The number of vendors per page can be specified using
            the 'page_size' query parameter.
    - POST: Creates a new vendor with the data provided in the request body.

    Parameters:
    - request: The HTTP request object.

    Returns:
    - Response: A response object with a list of vendors (for GET requests)
            or the created vendor's details (for POST requests).

    Raises:
    - PermissionDenied: If the user does not have the
    required permissions
        to perform the operation.
    - ValidationError: If the request data is invalid or
    missing required fields.

    Note:
    - Pagination is implemented using Django REST Framework's
        pagination classes,
        allowing for efficient retrieval of large datasets.
    - Permissions are managed through Django REST Framework's
        permission classes,
        ensuring that only authenticated users can create vendors.
    """
    # if the request is GET, list all the vendors
    if request.method == 'GET':
        cached_data = cache.get('cache_all_vendors')
        if cached_data:
            all_vendors = cached_data
        else:
            all_vendors = list(Vendor.objects.all().order_by('id'))
            cache.set('cache_all_vendors', all_vendors, timeout=60)
        try:
            page_number = request.query_params.get('page', 1)
            page_size = request.query_params.get('page_size', 10)
            p = Paginator(all_vendors, page_size)

            page_obj = p.get_page(int(page_number))

        # if page is empty then return last page
        except EmptyPage:
            page_obj = p.page(p.num_pages)
        # if page_number is not an integer then assign the first page
        except (PageNotAnInteger, Exception):
            page_obj = p.page(1)
        finally:
            serialise = VendorSerializer(page_obj, many=True)
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
    serializer = VendorSerializer(data=request.data)
    if serializer.is_valid():
        # save the object
        serializer.save()
        # return the response
        return Response('Vendor created sucesfully', status.HTTP_201_CREATED)
    return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def get_or_update_vendor(request, vendor_id):
    """
    Handles retrieving, updating, or deleting a specific vendor's
    details based on the request method.

    This function supports the following request methods:
    - GET: Retrieves the details of the specified vendor.
    - PUT : Updates the details of the specified vendor.
    - DELETE: Deletes the specified vendor.

    Parameters:
    - request: The HTTP request object.
    - vendor_id: The unique identifier of the vendor.

    Returns:
    - Response: A response object with the vendor's details,
        a success message upon update or deletion,
        or an error message if the operation fails.

    Raises:
    - Http404: If the specified vendor does not exist.
    - PermissionDenied: If the user does not have the
        required permissions to perform the operation.
    """
    vendor = get_object_or_404(Vendor, id=str(vendor_id))
    if request.method == 'GET':
        cached_data = cache.get(f'Vendor_{vendor_id}')
        if cached_data:
            return Response(cached_data, status.HTTP_200_OK)
        # retrive the data of that vendor
        serialise = VendorSerializer(vendor)
        data = serialise.data
        cache.set(f'Vendor_{vendor_id}', data, timeout=60)
        return Response(data, status.HTTP_200_OK)
    elif request.method == 'PUT':
        # update the object
        serialise = VendorSerializer(vendor, data=request.data, partial=True)
        if serialise.is_valid():
            serialise.save()
            return Response(
                'Vendor created sucesfully',
                status.HTTP_201_CREATED)
        return Response(serialise.errors, status.HTTP_400_BAD_REQUEST)
    # if the method is delete
    elif request.method == 'DELETE':
        name = vendor.name
        vendor.delete()
    return Response(f'Vendor: {name} created sucesfully deleted')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_performance(request, vendor_id):
    '''
    Retrieve performance metrics for a specific vendor.

    Parameters:
        request (HttpRequest): The request object sent by the client.
        vendor_id (int): The ID of the vendor whose performance metrics are t
            to be retrieved.

    Returns:
        HttpResponse: A JSON response containing the performance
        metrics for the specified vendor.
    '''
    vendor = get_object_or_404(Vendor, id=vendor_id)
    performance = HistoricalPerformance.objects.filter(vendor=vendor).values()

    return Response(performance)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_performance(request, vendor_id):
    """
    Retrieve and paginate the historical performance data for a specific vendor

    This view function fetches the historical performance
        records for a vendor specified by `vendor_id`.
    It supports pagination through query parameters `page` and `page_size`.

    Parameters:
    - request: The HTTP request object.
    - vendor_id: The ID of the vendor for which to
        retrieve historical performance data.

    Returns:
    - A JSON response containing the paginated historical performance data,
        along with pagination information.
    """
    try:
        # Correctly use .only() with field names as strings
        vendor = Vendor.objects.filter(id=vendor_id).first()

        if not vendor:
            return Response(
                f'Vendor with ID {vendor_id} does not exist.',
                status=status.HTTP_404_NOT_FOUND)
        data = {
            'vendor_id': vendor.id,
            'on_time_delivery_rate': vendor.on_time_delivery_rate,
            'quality_rating_avg': vendor.quality_rating_avg,
            'average_response_time': vendor.average_response_time,
            'fulfillment_rate': vendor.fulfillment_rate
        }

        return Response(data)
    except Exception as e:
        # Handle any unexpected errors
        return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
