from django.contrib.auth import get_user_model
from rest_framework import serializers

from posts.utils import content_type_str, visibility_str
from posts.models import Post, Comment


User = get_user_model()

class AuthorSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
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


class PostSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField()
    # size = serializers.SerializerMethodField()
    contentType = serializers.SerializerMethodField()
    visibility = serializers.SerializerMethodField()
    author = AuthorSerializer()
    categories = serializers.StringRelatedField(many=True)
    comments = CommentSerializer(many=True)
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
        return obj.comments.count()

    def get_visibility(self, obj):
        return visibility_str[obj.visibility]

    def get_contentType(self, obj):
        return content_type_str[obj.content_type]


