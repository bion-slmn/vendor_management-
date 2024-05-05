'''
Module to serialise Vendor module
'''
from rest_framework import serializers
from .models import Vendor, HistoricalPerformance


class VendorSerializer(serializers.ModelSerializer):
    '''
    Serializer for the Vendor model.

    This serializer serializes and deserializes Vendor instances.
    The 'vendor_code' field is read-only and auto-generated.

    Fields:
        vendor_code (str): The unique identifier for the vendor. (read-only)


    Usage Example:
        To serialize a Vendor instance:
        ```python
        serializer = VendorSerializer(instance=my_vendor)
        serialized_data = serializer.data
        ```

        To deserialize data into a Vendor instance:
        ```python
        serializer = VendorSerializer(data=request.data)
        if serializer.is_valid():
            vendor_instance = serializer.save()
        ```

    '''
    vendor_code = serializers.CharField(read_only=True)

    class Meta:
        model = Vendor
        fields = '__all__'

    def create(self, validated_data):
        """
        Create and return a new `Vendor` instance,
            given the validated data.
        """
        return Vendor.objects.create(**validated_data)

    def update(self, instance, validated_data):
        '''
        Updates the fields of the provided Vendor
            instance with the validated data.

        Args:
            instance (Vendor): The Vendor instance to be updated.
            validated_data (dict): The validated data containing
                updated field values.

        Returns:
            Vendor: The updated Vendor instance.
        '''
        for attr, value in validated_data.items():
            if hasattr(instance, attr):
                setattr(instance, attr, value)
        instance.save()
        return instance


class HistoricalPerformanceSerializer(serializers.ModelSerializer):
    """
    Serializer for the HistoricalPerformance model.

    This serializer provides a way to convert
        HistoricalPerformance instances into JSON format
    and vice versa. It includes all fields of the HistoricalPerformance model.

    Attributes:
        vendor (ForeignKey): Link to the Vendor model.
        date (DateTime): Date of the performance record.
        on_time_delivery_rate (float): Historical record of
            the on-time delivery rate.
        quality_rating_avg (float): Historical record of
            the quality rating average.
        average_response_time (float): Historical record of the
            average response time.
        fulfillment_rate (float): Historical record of the fulfillment rate.
    """

    class Meta:
        model = HistoricalPerformance
        fields = '__all__'
