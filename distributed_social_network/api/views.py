from rest_framework import viewsets
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.views import APIView
from rest_framework.mixins import RetrieveModelMixin

from django.contrib.auth import get_user_model
from posts.utils import Visibility
from posts.models import Post, Comment


from rest_framework import permissions
from rest_framework.response import Response

from rest_framework.decorators import action

from posts.views import PostVisbilityMixin

from . import serializers
import re
User = get_user_model()


class AuthorViewset (viewsets.ReadOnlyModelViewSet):
    """API endpoint for getting users and user list
     - Gets profile
     - Gets a list of authors
    """
    queryset = User.objects.filter(is_active=True, host=None)
    serializer_class = serializers.AuthorSerializer

    @action(methods=["post", "get"], detail=True)
    def friend(self, request, pk=None):
        """
        FIXME: return a url instead of uuid.
        """
        user = self.get_object()
        friends = user.friends.all()

        if request.method == "GET":
            serializer = serializers.AuthorSerializer(friends, many=True, context={'request': request})
            return Response(serializer.data)

        else:
            print(request.data)
            # Parse the url to a uuid only.
            # UUID regex pattern from
            # https://stackoverflow.com/questions/7905929/how-to-test-valid-uuid-guid/13653180#13653180
            # Taken March 12, 2018

            p = "([0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})"
            pattern = re.compile(p, re.IGNORECASE)
            author_query = [pattern.search(id).group() for id in request.data["authors"]]

            are_friends = friends.filter(id__in=author_query).values_list("id", flat=True)

            response_data = dict(request.data)
            response_data["authors"] = [str(friend) for friend in are_friends]

            return Response(response_data)

    @action(methods=["get"], detail=True)
    def posts(self, request, pk=None):
        if request.method == "GET":
            user = self.get_object()

            # Not really meant to be used this way...but it works?
            post_filter = PostVisbilityMixin()
            qs = post_filter.filter_user_visible(user, Post.objects.all())

            print(qs)
            serializer = serializers.PostSerializer(qs, many=True, context={'request': request})
            return Response(serializer.data)


class AuthorPostView(APIView):
    """
    Gets a list of posts visible to currently authenticated used or
    creates new post for authenticated user.
    /author/{author_id}/posts
    """
    permission_classes = (permissions.IsAuthenticated)

    def get(self, request):
        return Response(status=501)

    def post(self, request):
        return Response(status=501)


class PostViewSet (viewsets.ReadOnlyModelViewSet):
    """API endpoint for reading posts and lists of posts.
    - gets single post
    - gets a list of posts.
    """
    queryset = Post.objects.filter(visibility=Visibility.PUBLIC)
    serializer_class = serializers.PostSerializer


    @action(methods=["post", "get"], detail=True)
    def comments(self, request, pk=None):
        """ For getting and creating comments"""
        post = self.get_object()

        if request.method == "GET":
            comments = post.comment_set.all()
            serializer = serializers.CommentSerializer(comments, many=True, context={'request': request})

            return Response(serializer.data)

        if request.method == "POST":
            return Response(status=501)

    def list(self, request):
        qs = Post.objects.filter(visibility=Visibility.PUBLIC)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class AreFriendsView(APIView):
    """
    Checks if two users are friends
    /author/<author1_id>/friends/<author2_id>
    """

    def get(self, request, pk1, pk2):
        return Response(status=501)


class CreatePostView(CreateAPIView):
    serializer_class = serializers.PostSerializer
