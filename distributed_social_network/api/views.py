from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.mixins import RetrieveModelMixin

from django.contrib.auth import get_user_model
from posts.utils import Visibility
from posts.models import Post, Comment

from rest_framework.response import Response

from rest_framework.decorators import action

import json

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
            return Response("[]")


class PostViewSet (viewsets.ReadOnlyModelViewSet):
    """API endpoint for reading posts and lists of posts.
    - gets single post
    - gets a list of posts.
    """
    queryset = Post.objects.filter(visibility=Visibility.PUBLIC)
    serializer_class = serializers.PostSerializer


class CommentViews():
    """API endpoints for getting and creating comments for specific posts"""


class AreFriendsView(APIView):
    """/author/<author1_id>/friends/<author2_id>
    For now only works with local server friends.

    TODO: Check remote servers.
    """

    def get(self, request):
        pass
