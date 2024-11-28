from django.contrib import admin
from django.urls import path, include

from .views import *

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('add-to-cart/', AddToCartView.as_view(), name='add-to-cart'),
    path('add-to-cart/<int:pk>/', AddToCartView.as_view(), name='add-to-cart'),
    path('remove-from-cart/<int:pk>/', RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('clear-cart/', ClearCartView.as_view(), name='clear-cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
]
