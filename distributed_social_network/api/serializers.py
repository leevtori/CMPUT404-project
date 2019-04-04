from django.contrib.auth import get_user_model
from rest_framework import serializers

from posts.utils import content_type_str, visibility_str, Visibility, ContentType
from posts.models import Post, Comment, Categories
from django.conf import settings

from users.models import Node

from .utils import get_uuid_from_url
from urllib.parse import urlparse

User = get_user_model()

# NOTE: for debugging purposes
from pprint import pprint

class FriendSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id",)

    def get_id(self, obj):
        return obj.get_url()

class AuthorSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    firstName = serializers.CharField(source="first_name",allow_null=True, allow_blank=True, required=False)
    lastName = serializers.CharField(source="last_name",allow_null=True, allow_blank=True, required=False)
    # serializers.CharField(source="username")

    host = serializers.SerializerMethodField()

    displayName = serializers.CharField(source="username",required=False)
    url = serializers.SerializerMethodField(method_name="get_id")
    github=serializers.CharField(allow_blank=True)

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
        host = obj.host or settings.HOSTNAME
        return str(host)

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

# ============================================================================
# TODO: refactor and clean up stuff below & above
# ============================================================================


class VisibilityField(serializers.Field):
    default_error_messages = {
        'invalid': 'Invalid value'
    }

    def to_internal_value(self, data):
        options = Visibility.get_choices()
        mapping = {v: k for k, v in dict(options).items()}

        try:
            return mapping[data.title()]

        except KeyError:
            self.fail('invalid', input=data)


class CategoryField(serializers.StringRelatedField):
    def to_internal_value(self, data):
        obj, create = Categories.objects.get_or_create(
            name=data
        )

        return obj


class AuthorIDField(serializers.Field):
    default_error_messages = {
        'invalid': 'Invalid value'
    }

    def to_internal_value(self, value):
        try:
            return get_uuid_from_url(value)
        except AttributeError:
            self.fail('invalid', input=value)


class HostField(serializers.Field):
    default_error_messages = {
        'invalid': 'Host Does not exist.'
    }

    def to_internal_value(self, value):
        v = urlparse(value)

        try:
            return Node.objects.get(hostname__icontains=v.hostname)
        except Node.DoesNotExist:
            if v.hostname not in settings.HOSTNAME:
                self.fail('invalid', input=value)
            return None


class UserSerializer(serializers.ModelSerializer):
    id = AuthorIDField()
    host = HostField()
    firstName = serializers.CharField(
        source='first_name',
        required=False,
        allow_blank=True)
    lastName = serializers.CharField(
        source='last_name',
        required=False,
        allow_blank=True)
    displayName = serializers.CharField(source="username")

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

    def create(self, serialized_data):
        # first try to get it.
        obj, create = User.objects.get_or_create(**serialized_data)
        if create:
            obj.local = False  # if we have to create a user, there is no way that they are local!
        return obj


class ContentTypeField(serializers.Field):
    default_error_messages = {
        'invalid': 'Invalid value'
    }

    def to_internal_value(self, value):
        choices = ContentType.get_choices()
        mapping = {value: key for key, value in dict(choices).items()}

        try:
            return mapping[value.lower()]
        except KeyError:
            self.fail("invalid", value)


class AnotherCommentPostSerializer(serializers.ModelSerializer):
    contentType = serializers.CharField(source="content_type")
    author = UserSerializer()

    class Meta:
        model = Comment
        fields = (
            "id",
            "contentType",
            "comment",
            "published",
            "author",
        )

    def create(self, validated_data):
        """
        Insert a description here.
        TODO: a whole lot of refactoring.
        """
        print("Reminder to refactor!!!!")

        # First get or create an author.
        author = validated_data.pop("author")
        author_serializer = UserSerializer(data=author)
        if author.is_valid():
            author = author_serializer.save()

        # And now for the comment itself...
        instance = Comment.objects.create(author=author, **validated_data)

        return instance


class PostCreateSerializer(serializers.ModelSerializer):
    visibility = VisibilityField()
    categories = CategoryField(many=True)
    author = UserSerializer()
    contentType = ContentTypeField()
    comments = AnotherCommentPostSerializer(many=True)

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
            # "visibleTo", NOTE: For now, ignored.
            "unlisted"
        )

    def get_or_create_author(self, author_dict):
        if User.objects.filter(id=author_dict["id"]).exists():
            author_object = User.objects.get(id=author_dict['id'])

        else:
            author_object = User.objects.create(**author_dict)

        return author_object

    def create(self, validated_data):
        ModelClass = self.Meta.model

        comments = validated_data.pop("comments")
        categories = validated_data.pop("categories")
        author = validated_data.pop("author")

        validated_data["author"] = self.get_or_create_author(author)

        # change contentType to content_type
        validated_data.pop("contentType")
        # validated_data["content_type"] = ct
        # Might raise an error, but let it be caught somewhere else.
        instance = ModelClass._default_manager.create(**validated_data)

        # now add the categories.
        instance.categories.add(*categories)

        # Then create the comments
        # FIXME: check if this actually works.
        for comment in comments:
            comment['author'] = self.get_or_create_author(comment["author"])
            Comment.objects.create(**comment, post=instance)

        return instance
