from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated 
from django.shortcuts import get_object_or_404

from .serializers import * 
from .models import *
from crop.models import Crop, Sales
from crop.serializers import SalesSerializer

# Create your views here.
class CartView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSearializer
    
    def get(self, request):
        user = request.user
        cart = Cart.objects.filter(user=user).first()
            
        serializer = CartSearializer(cart)
        return Response(serializer.data)
    

class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemsSerializer
    
    def post(self, request):
        user = request.user
        
        # Ensure the cart exists
        cart, created = Cart.objects.get_or_create(user=user)
        
        # Pass the cart as context to the serializer
        serializer = self.serializer_class(data=request.data, context={'cart': cart})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        user = request.user
        cart = Cart.objects.filter(user=user).first()
        cart_item = get_object_or_404(CartItems, pk=pk, cart=cart)
        
        serializer = self.serializer_class(cart_item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RemoveFromCartView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        user = request.user
        cart = Cart.objects.filter(user=user).first()
        cart_item = get_object_or_404(CartItems, pk=pk, cart=cart)
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ClearCartView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        cart = Cart.objects.filter(user=user).first()
        cart.cart_items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        cart = Cart.objects.filter(user=user).first()

        if not cart or not cart.cart_items.exists():
            return Response({"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        errors = []
        for cart_item in cart.cart_items.all():
            # Pass cart item details to the serializer
            serializer = SalesSerializer(
                data={
                    "quantity_sold": cart_item.quantity,
                    "price_at_sale": cart_item.crop.price
                },
                context={
                    "crop": cart_item.crop,
                    "request": request
                }
            )
            if serializer.is_valid():
                serializer.save()
            else:
                errors.append(serializer.errors)

        # If there are errors, return them
        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        # Clear the cart after processing
        cart.cart_items.all().delete()
        return Response({"detail": "Checkout successful."}, status=status.HTTP_204_NO_CONTENT)