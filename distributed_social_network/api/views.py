from rest_framework import viewsets
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from posts.utils import Visibility
from posts.models import Post, Comment

from rest_framework.response import Response

from rest_framework.decorators import action

from . import serializers

User = get_user_model()

# Create your views here.

class AuthorViewset (viewsets.ReadOnlyModelViewSet):
    """API endpoint for getting users and user list"""
    queryset = User.objects.filter(is_active=True, host=None)
    serializer_class = serializers.AuthorSerializer

    @action(methods=["get"], detail=True)
    def friends(self, request, pk=None):
        author = self.get_object()
        friends = author.friends.all()
        serializer = serializers.AuthorSerializer(friends, context={'request': request}, many=True)
        return Response(serializer.data)


class PostViewSet (viewsets.ReadOnlyModelViewSet):
    """API endpoint for reading posts and lists of posts."""
    queryset = Post.objects.filter(visibility=Visibility.PUBLIC)
    serializer_class = serializers.PostSerializer
