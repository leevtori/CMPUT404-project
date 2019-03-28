from django.contrib.auth import get_user_model
from rest_framework import serializers

from posts.utils import content_type_str, visibility_str
from posts.models import Post, Comment

User = get_user_model()


class AuthorSerializer(serializers.ModelSerializer):
    id = serializers.HyperlinkedIdentityField(view_name="api-author-detail")
    # firstName = serializers.CharField(source="first_name")
    # lastName = serializers.CharField(source="last_name")
    # serializers.CharField(source="username")
    displayName = serializers.CharField(source="username")
    url = serializers.HyperlinkedIdentityField(view_name="api-author-detail")

    class Meta:
        model = User
        fields = (
            "id",
            "host",
            "displayName",
            "url",
            "github"
        )


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
