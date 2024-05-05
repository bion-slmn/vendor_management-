'''
THis module defines endpoint for authN and authZ of the user,
it uses token based authN
'''
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializer import UserSerializer
from django.contrib.auth.models import User


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class UserLoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = get_object_or_404(User, username=username)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'username': user.username,
                             'success': True}, status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=401)
