from rest_framework import serializers

from account.models import User
from .models import DialogsModel, InboxGroup, InboxMessage, MessageModel

from rest_framework import serializers
from .models import MessageModel

from rest_framework import serializers
from .models import MessageModel

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer to include user information such as ID, email, user_type, and profile details.
    """
    name = serializers.SerializerMethodField()
    you = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'user_type', 'name', 'you']

    def get_name(self, obj):
        """
        Get the name of the user based on their profile.
        """
        # if obj.user_type == 'client':
        #     profile = getattr(obj, 'clientprofile', None)
        #     return f"{profile.firstName} {profile.lastName}" if profile else None
        # elif obj.user_type == 'crew':
        #     profile = getattr(obj, 'crewprofile', None)
        #     return profile.name if profile else None
        # return None
        return obj.email

    def get_you(self, obj):
        """
        Determine if the user is the authenticated user (request.user).
        """
        # `context` is passed to serializers from the view and contains the `request`.
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj == request.user  # Return True if `obj` is the current user
        return False
    
class DialogSerializer(serializers.ModelSerializer):
    """
    Serializer for DialogModel, including user1 and user2 with their profile info.
    """
    user1 = UserProfileSerializer(read_only=True, context={'request': None})
    user2 = UserProfileSerializer(read_only=True, context={'request': None})

    class Meta:
        model = DialogsModel
        fields = ['id', 'user1', 'user2']

    def to_representation(self, instance):
        """
        Override to pass the request context to the user serializers.
        """
        representation = super().to_representation(instance)
        request = self.context.get('request')

        # Pass the `request` context to UserProfileSerializer
        representation['user1'] = UserProfileSerializer(instance.user1, context={'request': request}).data
        representation['user2'] = UserProfileSerializer(instance.user2, context={'request': request}).data

        return representation

class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for MessageModel, including full user information for sender and recipient.
    """
    sender = UserProfileSerializer(read_only=True, context={'request': None})
    recipient = UserProfileSerializer(read_only=True, context={'request': None})

    class Meta:
        model = MessageModel
        fields = ['id', 'sender', 'recipient', 'text', 'read', 'created']

    def to_representation(self, instance):
        """
        Override this method to pass request context to the UserProfileSerializer.
        """
        representation = super().to_representation(instance)
        request = self.context.get('request')

        # Update the context to pass the `request` to UserProfileSerializer
        representation['sender'] = UserProfileSerializer(
            instance.sender, context={'request': request}
        ).data
        representation['recipient'] = UserProfileSerializer(
            instance.recipient, context={'request': request}
        ).data

        return representation

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']

class GroupSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)
    admin = UserSerializer(read_only=True)

    class Meta:
        model = InboxGroup
        fields = ['id', 'name', 'admin', 'members']
        
class GroupSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()  # Use SerializerMethodField to apply custom logic
    admin = UserProfileSerializer(read_only=True, context={'request': None})

    class Meta:
        model = InboxGroup
        fields = ['id', 'name', 'admin', 'members']

    def get_members(self, obj):
        """
        Custom method to serialize the members field with UserProfileSerializer, passing the request context.
        """
        request = self.context.get('request')  # Get the request from context
        # Serialize members using UserProfileSerializer with the request context
        return UserProfileSerializer(
            obj.members.all(),  # ManyToMany field, get all members
            many=True,  # It's a list of users
            context={'request': request}  # Pass the request context for `you` field in UserProfileSerializer
        ).data

    def to_representation(self, instance):
        """
        Override this method to pass request context to the admin field.
        """
        representation = super().to_representation(instance)
        request = self.context.get('request')

        # Update the context to pass the `request` to UserProfileSerializer for admin
        representation['admin'] = UserProfileSerializer(
            instance.admin, context={'request': request}
        ).data

        return representation

class GroupMessageSerializer(serializers.ModelSerializer):
    sender = UserProfileSerializer(read_only=True, context={'request': None})
    group = GroupSerializer()

    class Meta:
        model = InboxMessage
        fields = ['id', 'group', 'sender', 'message', 'timestamp']
        
    def to_representation(self, instance):
        """
        Override this method to pass request context to the UserProfileSerializer.
        """
        representation = super().to_representation(instance)
        request = self.context.get('request')

        # Update the context to pass the `request` to UserProfileSerializer
        representation['sender'] = UserProfileSerializer(
            instance.sender, context={'request': request}
        ).data

        return representation
