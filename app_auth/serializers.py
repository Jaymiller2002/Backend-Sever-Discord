from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Server, Channel, Message, Friendship, PrivateMessage


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Include user details in profile

    class Meta:
        model = Profile
        fields = ['user', 'first_name', 'last_name', 'bio', 'image']  # Specify the fields


class ServerSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=False)  # Allow updating members

    class Meta:
        model = Server
        fields = ['id', 'name', 'owner', 'description', 'image', 'members']

    def update(self, instance, validated_data):
        members_data = validated_data.pop('members', [])
        instance = super().update(instance, validated_data)

        # Handle members updating logic
        instance.members.clear()
        for member_data in members_data:
            user = User.objects.get(id=member_data['id'])
            instance.members.add(user)

        return instance


class ChannelSerializer(serializers.ModelSerializer):
    server = ServerSerializer(read_only=True)  # Show server details

    class Meta:
        model = Channel
        fields = ['id', 'name', 'server', 'is_voice_channel']


class MessageSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # Show user details in messages
    channel = ChannelSerializer(read_only=True)  # Show channel details in messages

    class Meta:
        model = Message
        fields = ['id', 'user', 'channel', 'content', 'timestamp', 'edited']

class FriendshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = ['id', 'from_user', 'to_user', 'is_accepted', 'created_at']  # Adjusted field names

class PrivateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateMessage
        fields = ['id', 'sender', 'receiver', 'content', 'timestamp']  # Adjusted field names