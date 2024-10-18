from django.contrib import admin
from app_auth.models import Profile, Server, Channel, Message, Friendship, PrivateMessage

# Profile Admin Configuration
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'bio')  # Display these fields in admin panel
    search_fields = ('user__username', 'first_name', 'last_name')  # Allow searching by user and names
    list_filter = ('user',)  # Filter by user

# Server Admin Configuration
class ServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner')  # Display name and owner in the admin list view
    search_fields = ('name', 'owner__username')  # Allow searching by server name and owner username

# Channel Admin Configuration
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'server')  # Display channel name and related server
    search_fields = ('name', 'server__name')  # Allow searching by channel name and server name

# Message Admin Configuration
class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'channel', 'content', 'timestamp')  # Display these fields in admin
    search_fields = ('user__username', 'content')  # Allow searching by user and message content
    list_filter = ('channel', 'timestamp')  # Filter messages by channel and timestamp

# Friendship Admin Configuration
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'is_accepted', 'created_at')  # Adjust to match your model
    search_fields = ('from_user__username', 'to_user__username')  # Search by usernames of both users
    list_filter = ('is_accepted',)  # Filter by accepted status

# PrivateMessage Admin Configuration
class PrivateMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'content', 'timestamp')  # Adjust to match your model
    search_fields = ('sender__username', 'receiver__username', 'content')  # Search by sender, receiver, or content

# Register models in the admin panel
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Server, ServerAdmin)
admin.site.register(Channel, ChannelAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Friendship, FriendshipAdmin)
admin.site.register(PrivateMessage, PrivateMessageAdmin)
