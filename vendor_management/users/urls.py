'''
This module creates the paths for registration and login
for a user
'''

from django.urls import path
from .views import UserRegistrationView, UserLoginView

urlpatterns = [
    path(
        'register/',
        UserRegistrationView.as_view(),
        name='user-registration'),
    path(
        'login/',
        UserLoginView.as_view(),
        name='user-login'),
]
