from rest_framework import serializers
from .models import Post
from account.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name']

class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    image_url = serializers.URLField()  

    class Meta:
        model = Post
        fields = ['id', 'content', 'image_url', 'created_at', 'user', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)