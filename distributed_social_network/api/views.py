from rest_framework import viewsets
from rest_framework.generics import GenericAPIView, CreateAPIView, UpdateAPIView
from rest_framework.views import APIView
from rest_framework.mixins import RetrieveModelMixin
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from posts.utils import Visibility
from posts.models import Post, Comment
from users.models import User, Node
from django.http import JsonResponse
from django.conf import settings
from rest_framework.exceptions import ParseError


from rest_framework import permissions
from rest_framework.response import Response

from rest_framework.decorators import action

from posts.views import PostVisbilityMixin

from . import serializers
import re, uuid
import json

User = get_user_model()


def get_uuid_from_url(url):
    p = "([0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})"
    pattern = re.compile(p, re.IGNORECASE)
    return pattern.search(url).group()


def get_author_id(request):
    try:
        user_id = request.META["HTTP_X_USER"]
        user_id = get_uuid_from_url(user_id)
    except (KeyError, User.DoesNotExist):
        raise ParseError(detail="Missing X-User Header Field")

    return user_id


class PaginateOverrideMixin:
    def get_paginated_response(self, data, **kwargs):
        """
        Return a paginated style `Response` object for the given output data.
        overridden from GenericAPIView to pass in additional parameters.
        """
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data, **kwargs)


class AuthorViewset (PaginateOverrideMixin, viewsets.ReadOnlyModelViewSet):
    """API endpoint for getting users and user list
     - Gets profile
     - Gets a list of authors
    """
    queryset = User.objects.filter(is_active=True, host=None)
    serializer_class = serializers.AuthorSerializer

    @action(methods=["get"], detail=True)
    def posts(self, request, pk=None):

        if request.method == "GET":
            user = self.get_object()
            auth_user = get_author_id(request)

            # Not really meant to be used this way...but it works?
            post_filter = PostVisbilityMixin()
            qs = post_filter.filter_user_visible(auth_user, user.posts.all())
            qs = qs.filter(unlisted=False)
            page = self.paginate_queryset(qs)
            if page is not None:
                serializer = serializers.PostSerializer(page, many=True, context={'request': request})
                return self.get_paginated_response(serializer.data, model="posts", query="posts")

            serializer = serializers.PostSerializer(qs, many=True, context={'request': request})
            return Response(serializer.data)

    def list(self, request):
        qs = self.get_queryset()
        qs = qs.filter(local=True)
        page = self.paginate_queryset(qs)

        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data, model="authors", query="authors")

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class FriendsView(GenericAPIView):
    """
    Gets friends of a author specified in URL
    /author/{author_id}/friends
    """
    serializer_class = serializers.FriendSerializer
    queryset = User.objects.all()

    def get_friends(self, pk):
        user = get_object_or_404(User, pk=pk)
        return user.friends.all()

    def format_response(self, friends, request):
        serializer = self.get_serializer(friends, many=True, context={'request': request})
        response = {"query": "friends"}

        if request.method == "POST":
            response["author"] = "author_id"

        response["authors"] = [i["id"] for i in serializer.data]

        return response

    def get(self, request, pk):
        friends = self.get_friends(pk)
        return Response(self.format_response(friends, request))

    def post(self, request, pk):
        # Parse the url to a uuid only.
        # UUID regex pattern from
        # https://stackoverflow.com/questions/7905929/how-to-test-valid-uuid-guid/13653180#13653180
        # Taken March 12, 2018
        friends = self.get_friends(pk)

        author_query = [get_uuid_from_url(id) for id in request.data["authors"]]

        are_friends = friends.filter(id__in=author_query)

        response_data = self.format_response(are_friends, request)

        return Response(response_data)


class AuthorPostView(PaginateOverrideMixin, GenericAPIView):
    """
    Gets a list of posts visible to currently authenticated user or
    creates new post for authenticated user.
    /author/posts
    """
    serializer_class = serializers.PostSerializer
    queryset = Post.objects.all()

    def create_status_responses(self, statusType=True, message="Post created"):
        return {
            "query": "createPost",
            "type": statusType,
            "message": message
        }

    def get(self, request):
        author_id = get_author_id(request)

        if User.objects.filter(pk=author_id).exists():
            user = User.objects.get(pk=author_id)

            post_filter = PostVisbilityMixin()
            posts = post_filter.filter_user_visible(user, self.get_queryset())

        else:
            posts = Post.objects.filter(visibility=Visibility.PUBLIC, unlisted=False, order_by="-published")

        page = self.paginate_queryset(posts)

        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data, model="posts", query="posts")

        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        author_id = get_author_id(request)

        user = get_object_or_404(User, pk=author_id)

        try:
            post = request.data["post"]
        except KeyError:
            return Response(
                self.create_status_responses(statusType=False, message="Malformed request"),
                status=400
                )

        serializer = serializers.PostCreateSerializer(data=post)

        print(serializer.is_valid())
        print(serializer.errors)
        if serializer.is_valid():
            serializer.save()
        return Response(status=501)


class PostViewSet (PaginateOverrideMixin, viewsets.ReadOnlyModelViewSet):
    """API endpoint for reading posts and lists of posts.
    - gets single post
    - gets a list of posts.
    """
    queryset = Post.objects.filter(visibility=Visibility.PUBLIC)
    serializer_class = serializers.PostSerializer


    def list(self, request):
        qs = Post.objects.filter(visibility=Visibility.PUBLIC)

        page = self.paginate_queryset(qs)

        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data, query="posts", model="posts")

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class CommentView(PaginateOverrideMixin, GenericAPIView):
    serializer_class = serializers.CommentPostSerializer

    def get(self, request, pk):
        post = get_object_or_404(Post, pk = pk)
        comments = post.comment_set.all()

        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = serializers.CommentSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data, query="comments", model="comments")

        serializer = serializers.CommentSerializer(comments, many=True, context={'request': request})

        return Response(serializer.data)

    def post(self, request, pk):
        try:
            print("data ", request.data['post'])
        except KeyError:
            return Response(status=400)

        post = get_object_or_404(Post, pk=pk)

        print(1)
        id = request.data['post']['author']['id']
        id = get_uuid_from_url(id)
        print(2)

        # request.data['post'].pop('author')

        serializer = serializers.CommentPostSerializer(data = request.data['post'] , context={'request':request})
        print(3)
        commentUser = get_object_or_404(User, pk=id)

        if serializer.is_valid():
            print(4)
            serializer.save(post_id=pk,author=commentUser,)
            print(5)
            return Response(status=201)
        print("ERRROR ", serializer.errors)
        return Response(serializer.errors, status=400)


class AreFriendsView(APIView):
    """
    Checks if two users are friends
    /author/<author1_id>/friends/<author2_id>
    """

    def get(self, request, pk1, pk2):
        print("HEHRRHEHREHEHH")
        id1=get_uuid_from_url(pk1)
        id2=get_uuid_from_url(pk2)
        author1 = get_object_or_404(User,id=id1)
        author2 = get_object_or_404(User,id=id2)
        author1_id = author1.geturl() #is this in the right format? idk lol
        author2_id = author2.geturl()
        print('auth1 id = ', author1_id)
        print('auth2 id = ', author2_id)
        are_friends = author2 in author1.friends.all()

        data = {
            "query": "friends",
            "friends": are_friends,
            "authors": [
                author1_id,
                author2_id,
            ],
        }
        return JsonResponse(data, safe=False)



# class CreatePostView(CreateAPIView):
#     serializer_class = serializers.PostSerializer


class FriendRequestView(APIView):
    """
    Makes a friend request
    """
    def post(self, request):

        friend_id = request.data['friend']['id']
        friend_id = get_uuid_from_url(friend_id)
        friend =  get_object_or_404(User, pk=friend_id, host=None, is_active=True)

        author_id = request.data['author']['id']
        author_id = get_uuid_from_url(author_id)
        request.data['author']['id'] = author_id

        host = request.data['author']['host']
        node = get_object_or_404(Node, hostname__icontains=host)
        request.data['author']['host'] = node.id

        serializer = serializers.AuthorSerializer(data = request.data['author'], context={'request': request})
        sucess = False

        if serializer.is_valid():
            sucess = True
            try:
                author = User.objects.get(pk=author_id)
            except User.DoesNotExist:
                author = serializer.save(id=author_id)

            friend.incomingRequests.add(author)
            author.outgoingRequests.add(friend)
            friend.followers.add(author)
            author.following.add(friend)
            data = {
                "query": "friendrequest",
                "sucess": sucess,
                "message": "Friend request sent"
            }
            return JsonResponse(data, safe=False, status=200)
        else:
            # return Response(serializer.errors, status=400)
            data = {
                "query": "friendrequest",
                "sucess": sucess,
                "message": "Friend request sent"
            }
            return JsonResponse(data, safe=False, status=400)

