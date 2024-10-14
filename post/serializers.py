from rest_framework import serializers
from .models import *
from account.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'profile_image', 'username', 'email', 'name']

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all(), write_only=True, required=False)

    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_at', 'user', 'post']
        read_only_fields = ['id', 'created_at', 'user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    # comments = CommentSerializer(many=True, read_only=True)  # Add comments in the fields list
    image_url = serializers.URLField()  

    class Meta:
        model = Post
        fields = ['id', 'content', 'image_url', 'created_at', 'user', 'updated_at', 'likes']
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

        
    def to_representation(self, instance):
        # Get the default representation
        representation = super().to_representation(instance)
        
        # Add the liked_count to the representation
        representation['likes_count'] = instance.likes.count()
        
        return representation