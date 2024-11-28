from rest_framework import serializers
from .models import *
from account.models import User
from crop.serializers import CropSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User 
        fields = ['id', 'profile_image', 'email', 'user_type', 'name', 'phone', 'address', 'city', 'state', 'country', 'zip']

class CartItemsSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartItems
        # fields = '__all__'
        fields = ['id', 'crop', 'quantity']

    def validate(self, data):
        crop = data['crop']
        quantity = data['quantity']
        
        # Validate quantity
        if quantity > crop.quantity:
            raise serializers.ValidationError('The quantity you requested is not available.')
        return data

    def create(self, validated_data):
        cart = self.context['cart']
        crop = validated_data['crop']
        quantity = validated_data['quantity']
        
        # Check if the crop is already in the cart
        cart_item = CartItems.objects.filter(cart=cart, crop=crop).first()
        if cart_item:
            cart_item.quantity += quantity
            cart_item.save()
            return cart_item
        
        # Create a new cart item if it doesn't exist
        return CartItems.objects.create(cart=cart, crop=crop, quantity=quantity)

    def update(self, instance, validated_data):
        quantity = validated_data.get('quantity')

        # Validate quantity
        if quantity > instance.crop.quantity:
            raise serializers.ValidationError('The quantity you requested is not available.')
        
        instance.quantity = quantity
        instance.save()
        return instance
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['crop'] = CropSerializer(instance.crop).data
        return representation

class CartSearializer(serializers.ModelSerializer):
    cart_items = CartItemsSerializer(read_only=True, many=True)

    class Meta:
        model = Cart
        fields = '__all__'

    def to_representation(self, instance):
        # add total price to the representation
        representation = super().to_representation(instance)
        total_price = 0
        for item in instance.cart_items.all():
            total_price += item.quantity * item.crop.price
        representation['total_price'] = total_price
        return representation
    