from django.contrib.auth import get_user_model
from rest_framework import serializers

from posts.utils import content_type_str, visibility_str
from posts.models import Post, Comment
from django.conf import settings

User = get_user_model()


class FriendSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id",)

    def get_id(self, obj):
        return obj.get_url()

class AuthorSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    firstName = serializers.CharField(source="first_name",allow_null=True, allow_blank=True)
    lastName = serializers.CharField(source="last_name",allow_null=True, allow_blank=True)
    # serializers.CharField(source="username")
    host = serializers.SerializerMethodField()

    displayName = serializers.CharField(source="username")
    url = serializers.SerializerMethodField(method_name="get_id")

    class Meta:
        model = User
        fields = (
            "id",
            "host",
            "firstName",
            "lastName",
            "displayName",
            "url",
            "github"
        )

    def get_host(self, obj):
        return obj.host or settings.HOSTNAME

    def get_id(self, obj):
        return obj.get_url()

class CommentSerializer(serializers.ModelSerializer):
    contentType = serializers.SerializerMethodField()
    author = AuthorSerializer()

    class Meta:
        model = Comment
        fields = (
            "id",
            "contentType",
            "comment",
            "published",
            "author",
        )

    def get_contentType(self, obj):
        return content_type_str[obj.content_type]


class CommentPostSerializer(serializers.ModelSerializer):
    contentType = serializers.CharField(source="content_type")
    author = AuthorSerializer()

    class Meta:
        model = Comment
        fields = (
            "id",
            "contentType",
            "comment",
            "published",
            "author",
        )


class PostSerializer(serializers.ModelSerializer):
    contentType = serializers.SerializerMethodField()
    visibility = serializers.SerializerMethodField()
    author = AuthorSerializer()
    categories = serializers.StringRelatedField(many=True)
    comments = CommentSerializer(many=True, source="comment_set")
    visibleTo = serializers.StringRelatedField(many=True, source="visible_to")

    class Meta:
        model = Post
        fields = (
           "id",
           "title",
           "source",
           "origin",
           "description",
           "contentType",
           "content",
           "author",
           "categories",
           "comments",
           "published",
           "visibility",
           "visibleTo",
           "unlisted"
            )

    def get_contentType(self, obj):
        return content_type_str[obj.content_type]

    def get_visibility(self, obj):
        return visibility_str[obj.visibility]


# FIXME: have the correct fields.
# class CommentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Comment
#         fields = "__all__"
