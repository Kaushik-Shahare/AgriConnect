from django.contrib import admin
from django.urls import path, include

from .views import *

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
]
