"""
URL configuration for project_auth project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView
from django.conf import settings
from django.conf.urls.static import static
from app_auth.views import (
    get_profile,
    create_user,
    update_user,
    delete_user,
    ServerViewSet,
    ChannelViewSet,
    MessageViewSet,
    friendship_view,
    private_message_view,
)

# Initialize the router for ViewSets
router = DefaultRouter()
router.register(r'servers', ServerViewSet, basename='servers')
router.register(r'channels', ChannelViewSet, basename='channels')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('profile/', get_profile, name='get_profile'),
    path('register/', create_user, name='create_user'),
    path('update-profile/', update_user, name='update_user'),
    path('delete-user/', delete_user, name='delete_user'),

    # Include the router-generated URLs for ViewSets
    path('', include(router.urls)),
    
    path('friends/', friendship_view, name='friendship_view'),
    path('private-messages/', private_message_view, name='private_message_view'),

    # Custom route for messages under a specific channel
    path('channels/<int:channel_id>/messages/', MessageViewSet.as_view({'get': 'list', 'post': 'create'}), name='message-list'),
]

# Add media URL configuration
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)