'''
Module to serialise PurchaseOrder module
'''
from rest_framework import serializers
from .models import PurchaseOrder


class PurchaseOrderSerializer(serializers.ModelSerializer):
    '''
    Serializer for the PurchaseOrder model.

    This serializer serializes and deserializes PurchaseOrder instances.
    The 'po_number' field is read-only and cannot be updated
        via this serializer.

    Fields:
        po_number (str): The purchase order number. This field is read-only.

    Usage Example:
        To serialize a PurchaseOrder instance:
        ```python
        serializer = PurchaseOrderSerializer(instance=my_purchase_order)
        serialized_data = serializer.data
        ```

        To deserialize data into a PurchaseOrder instance:
        ```python
        serializer = PurchaseOrderSerializer(data=request.data)
        if serializer.is_valid():
            purchase_order_instance = serializer.save()
        ```
    '''
    id = serializers.IntegerField(read_only=True)
    po_number = serializers.CharField(read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = '__all__'

    def create(self, validated_data):
        """
        Create and return a new `PurchaseOrder` instance,
        given the validated data.
        """
        return PurchaseOrder.objects.create(**validated_data)

    def update(self, instance, validated_data):
        '''
        Updates the fields of the provided PurchaseOrder
            instance with the validated data.

        Args:
            instance (PurchaseOrder): The PurchaseOrder instance to be updated.
            validated_data (dict): The validated data containing
                updated field values.

        Returns:
            PurchaseOrder: The updated PurchaseOrder instance.
        '''

        for attr, value in validated_data.items():
            if hasattr(instance, attr):
                setattr(instance, attr, value)
        instance.save()
        return instance
