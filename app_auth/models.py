from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    bio = models.TextField(blank=True)  # Optional bio field
    image = models.ImageField(upload_to='images/', blank=True, null=True)

    def __str__(self):
        return self.user.username


class Server(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True)  # Optional description for the server
    image = models.ImageField(upload_to='server_images/', blank=True, null=True)  # Server icon
    members = models.ManyToManyField(User, related_name='servers', blank=True)  # Users in the server

    def __str__(self):
        return self.name


class Channel(models.Model):
    name = models.CharField(max_length=100)
    server = models.ForeignKey(Server, related_name='channels', on_delete=models.CASCADE)
    is_voice_channel = models.BooleanField(default=False)  # Distinguish between text/voice channels

    def __str__(self):
        return f"{self.name} ({'Voice' if self.is_voice_channel else 'Text'})"


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)  # Track if the message has been edited

    def __str__(self):
        return f"Message by {self.user.username} in {self.channel.name} at {self.timestamp}"


class Friendship(models.Model):
    from_user = models.ForeignKey(User, related_name='friendship_requests_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='friendship_requests_received', on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)  # False if the request is pending, True if accepted
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f'{self.from_user.username} to {self.to_user.username}'

class PrivateMessage(models.Model):
    sender = models.ForeignKey(User, related_name='messages_sent', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='messages_received', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message from {self.sender.username} to {self.receiver.username} at {self.timestamp}'