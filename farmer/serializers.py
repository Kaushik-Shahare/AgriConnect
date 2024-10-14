from rest_framework import serializers
from .models import FarmerProfile
from account.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User 
        fields = ['id', 'email', 'user_type', 'name', 'phone', 'address', 'city', 'state', 'country', 'zip'] 

class FarmerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = FarmerProfile
        fields = '__all__'
        read_only_fields = ['user']