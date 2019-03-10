from rest_framework import viewsets
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from posts.utils import Visibility
from posts.models import Post, Comment

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


# class CommentViewSet(viewsets.ModelViewSet):
#     """API endpoints for getting and creating comments for specific posts"""
#     serializer_class = serializers.CommentSerializer
#     queryset = Comment.objects.all()

#     def get_queryset(self, request):
#         post_id = request.kwargs["postID"]
#         post = get_object_or_404(Post, id=post_id)
#         return post.comment_set.all()

#     def create(self, request):
#         post = get_object_or_404(Post, id=request.kwargs['postID'])
#         # Lets serializer do the rest of it
