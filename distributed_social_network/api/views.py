from rest_framework import viewsets
from django.contrib.auth import get_user_model

from posts.utils import Visibility
from posts.models import Post

from . import serializers

User = get_user_model()

# Create your views here.

class AuthorViewset (viewsets.ReadOnlyModelViewSet):
    """API endpoint for getting users and user list"""
    queryset = User.objects.filter(is_active=True, host=None)
    serializer_class = serializers.AuthorSerializer


class PostViewSet (viewsets.ReadOnlyModelViewSet):
    """API endpoint for reading posts and lists of posts."""
    queryset = Post.objects.filter(visibility=Visibility.PUBLIC)
    serializer_class = serializers.PostSerializer