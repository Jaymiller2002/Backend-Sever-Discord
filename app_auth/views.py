from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .models import Profile, Server, Channel, Message, Friendship, PrivateMessage
from .serializers import ProfileSerializer, ServerSerializer, ChannelSerializer, MessageSerializer, FriendshipSerializer, PrivateMessageSerializer

# Profile Views

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    user = request.user
    profile = user.profile
    serialized_profile = ProfileSerializer(profile)
    return Response(serialized_profile.data)

@api_view(['POST'])
@permission_classes([])
def create_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    bio = request.data.get('bio', '')  # Optional bio field
    image = request.data.get('image', None)  # Optional image field

    # Check if username already exists
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

    # Create the user and set the password
    user = User.objects.create(username=username)
    user.set_password(password)
    user.save()

    # Create a profile for the user
    profile = Profile.objects.create(
        user=user,
        first_name=first_name,
        last_name=last_name,
        bio=bio,
        image=image
    )

    # Return the serialized profile data
    profile_serialized = ProfileSerializer(profile)
    return Response(profile_serialized.data, status=status.HTTP_201_CREATED)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request):
    user = request.user
    profile = user.profile

    # Update profile fields
    profile.first_name = request.data.get('first_name', profile.first_name)
    profile.last_name = request.data.get('last_name', profile.last_name)
    profile.bio = request.data.get('bio', profile.bio)
    profile.image = request.data.get('image', profile.image)
    profile.save()

    profile_serialized = ProfileSerializer(profile)
    return Response(profile_serialized.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request):
    user = request.user

    # Check if the user exists
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        return Response({"error": "User profile does not exist"}, status=404)

    # Check if the authenticated user is the same as the user being deleted
    if request.user != user:
        return Response({"error": "You are not authorized to delete this user"}, status=403)

    # Delete user and related profile
    user.delete()
    return Response({"message": "User and profile deleted successfully"}, status=204)

# Server Views

class ServerViewSet(viewsets.ModelViewSet):
    queryset = Server.objects.all()
    serializer_class = ServerSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Automatically assign the currently logged-in user as the owner of the server
        serializer.save(owner=self.request.user)

# Channel Views

class ChannelViewSet(viewsets.ModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        server_id = self.request.query_params.get('server')

        if server_id:
            queryset = queryset.filter(server__id=server_id)

        return queryset

    def perform_create(self, serializer):
        server_id = self.request.data.get('server')
        try:
            server = Server.objects.get(id=server_id)
            serializer.save(server=server)
        except Server.DoesNotExist:
            raise ValidationError("The specified server does not exist.")

# Message Views

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        channel_id = self.kwargs.get('channel_pk')
        if channel_id:
            queryset = queryset.filter(channel_id=channel_id)
        return queryset

    def perform_create(self, serializer):
        channel_id = self.kwargs['channel_id']
        serializer.save(user=self.request.user, channel_id=channel_id)

# Friendship Views

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def friendship_view(request):
    if request.method == 'GET':
        # List all friendships where the authenticated user is involved
        friendships = Friendship.objects.filter(from_user=request.user) | Friendship.objects.filter(to_user=request.user)
        serializer = FriendshipSerializer(friendships, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Create a new friendship
        serializer = FriendshipSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.validated_data['to_user'] == request.user:
                return Response({"error": "You cannot befriend yourself."}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(from_user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        friendship_id = request.data.get('id')
        try:
            friendship = Friendship.objects.get(id=friendship_id)
            if request.user == friendship.from_user or request.user == friendship.to_user:
                friendship.delete()
                return Response({"message": "Friendship deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error": "You are not authorized to delete this friendship."}, status=status.HTTP_403_FORBIDDEN)
        except Friendship.DoesNotExist:
            return Response({"error": "Friendship not found."}, status=status.HTTP_404_NOT_FOUND)

# Private Message Views

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def private_message_view(request):
    if request.method == 'GET':
        messages = PrivateMessage.objects.filter(sender=request.user) | PrivateMessage.objects.filter(receiver=request.user)
        serializer = PrivateMessageSerializer(messages, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = PrivateMessageSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.validated_data['receiver'] == request.user:
                return Response({"error": "You cannot send a message to yourself."}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(sender=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        message_id = request.data.get('id')
        try:
            message = PrivateMessage.objects.get(id=message_id)
            if request.user == message.sender or request.user == message.receiver:
                message.delete()
                return Response({"message": "Message deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error": "You are not authorized to delete this message."}, status=status.HTTP_403_FORBIDDEN)
        except PrivateMessage.DoesNotExist:
            return Response({"error": "Message not found."}, status=status.HTTP_404_NOT_FOUND)
