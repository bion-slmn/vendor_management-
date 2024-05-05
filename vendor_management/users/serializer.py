'''
this module serialises user django objects to python objest
and also deserialises python objects to user objects
'''
from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new user.

    This serializer is used for user registration, allowing clients to
    submit data to create a new user account. It validates the input data
    and creates a new user instance if the data is valid.

    Example of expected input data:
    {
        "username": "example_user",
        "password": "example_password"
    }

    Attributes:
        username (str): The username of the new user.
        password (str): The password of the new user.
    """

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password')
