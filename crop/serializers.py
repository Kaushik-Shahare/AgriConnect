from rest_framework import serializers
from .models import *
from account.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User 
        fields = ['id', 'profile_image', 'email', 'user_type', 'name', 'phone', 'address', 'city', 'state', 'country', 'zip']

class QuantityAddedSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuantityAdded
        fields = '__all__'

class CropSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    quantity_added = QuantityAddedSerializer(read_only=True, many=True)

    class Meta:
        model = Crop
        fields = '__all__'
        read_only_fields = ['user']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation

class CropCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crop
        fields = '__all__'

    def create(self, validated_data):
        user = self.context['request'].user
        
        # Ensure only farmers can create crops
        if user.user_type != 'farmer':
            raise serializers.ValidationError('Only farmers can create crops')

        # Check if the crop already exists for the farmer
        crop = Crop.objects.filter(user=user, name=validated_data['name']).first()
        if crop:
            raise serializers.ValidationError('You have already listed this crop. Please update the quantity instead.')

        

        # Create a new crop entry
        crop = Crop.objects.create(**validated_data)

        # Add an entry in QuantityAdded to track the initial quantity
        QuantityAdded.objects.create(crop=crop, quantity=validated_data['quantity'])

        return crop

    
class SalesSerializer(serializers.ModelSerializer):
    crop = CropSerializer(read_only=True)

    class Meta:
        model = Sales
        fields = '__all__'
        read_only_fields = ['crop', 'sale_date', 'user']

    def create(self, validated_data):
        # Fetching the crop from context rather than validated_data
        crop = self.context['crop']

        if crop.user == self.context['request'].user:
            raise serializers.ValidationError('You cannot buy your own crop.')

        if crop.quantity < validated_data['quantity_sold']:
            raise serializers.ValidationError('Insufficient quantity in stock.')


        validated_data['user'] = self.context['request'].user

        # Deduct the sold quantity from the available crop quantity
        crop.quantity -= validated_data['quantity_sold']
        crop.save()  # Save updated quantity
        # Creating a sale record
        sale = Sales.objects.create(crop=crop, **validated_data)
        return sale

        