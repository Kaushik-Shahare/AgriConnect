from .models import User
from rest_framework import serializers
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    profile_image = serializers.URLField()  
    class Meta:
        model = User
        fields = ('id', 'username', 'profile_image', 'email', 'user_type', 'name', 'phone', 'address', 'city', 'state', 'country', 'zip')
        read_only_fields = ['id', 'user_type', 'email', 'username']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username','email', 'password', 'user_type')

    def create(self, validated_data):
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            user_type = validated_data.get('user_type')
        )
        return user

class LoginSerializer(serializers.Serializer):
    
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if user is None:
            raise serializers.ValidationError('Invalid credentials')
        return user