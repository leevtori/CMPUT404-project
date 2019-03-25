from django.contrib.auth import get_user_model
from rest_framework import serializers

from posts.utils import content_type_str, visibility_str
from posts.models import Post, Comment

User = get_user_model()


# FIXME: The id and url are wrong.
class AuthorSerializer(serializers.ModelSerializer):
    id = serializers.HyperlinkedIdentityField(view_name="user-detail")
    firstName = serializers.CharField(source="first_name")
    lastName = serializers.CharField(source="last_name")
    displayName = serializers.CharField(source="display_name")

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "bio",
            "host",
            "firstName",
            "lastName",
            "displayName",
            "url",
            "github"
        )

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


# FIXME: missing size and next fields
class PostSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField()
    # size = serializers.SerializerMethodField()
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
           "count",
           "comments",
           "published",
           "visibility",
           "visibleTo",
           "unlisted"
            )

    def get_count(self, obj):
        return obj.comment_set.count()

    def get_contentType(self, obj):
        return content_type_str[obj.content_type]

    def get_visibility(self, obj):
        return visibility_str[obj.visibility]


# FIXME: have the correct fields.
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"
