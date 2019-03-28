import io
from rest_framework.parsers import JSONParser
from rest_framework import serializers

from post.models import Post, Categories
from users.models import User


# for multiple posts that you don't need the comments
class posts_request_deserializer(serializers.Serializer):
    posts = serializers.ListField()

    def create(self, validated_data):
        post_list = []
        for post in validated_data['posts']:
            post = post_deserializer_no_comment(data=post)
            if Post.objects.filter(id=post.id).count() == 0:
                post.save()
            else:  # idk
                pass
            post_list.append(post)
        return post_list


# for single post with no comments
class post_deserializer_no_comment(serializers.Serializer):
    id = serializers.HyperlinkedIdentityField()
    title = serializers.CharField()
    source = serializers.CharField()
    description = serializers.CharField()
    contentType = serializers.CharField()
    author = serializers.JSONField(True)
    content = serializers.CharField()
    categories = serializers.ListField()
    published = serializers.TimeField()
    visibility = serializers.CharField()
    visibleTo = serializers.ListField()
    unlisted = serializers.BooleanField()

    def create(self, validated_data):
        usr = user_deserializer(validated_data['author'])
        tags = validated_data['categories']
        visibleList = []
        for ids in validated_data['visibleTo']:
            # asssuming that either we have the user in here or we dont care, since its guaranteed to be not our user
            u = User.objects.get(id=ids)
            if u:
                visibleList.append(u)
        categories = []
        for tag in tags:
            if Categories.objects.filter(name=tag).count() == 0:
                Categories.objects.create(name=tag)
                Categories.save()
            categories.append(tag)

        return Post.objects.create(
            id=validated_data['id'],
            title=validated_data['title'],
            source=validated_data['source'],
            description=validated_data['description'],
            content_type=validated_data['contentType'],
            author=usr,
            content=validated_data['content'],
            published=validated_data['published'],
            visibility=validated_data['published'],
            unlisted=validated_data['unlisted']
        )


# TODO make changes to this
class user_deserializer(serializers.Serializer):
    id = serializers.HyperlinkedIdentityField()
    # i dont know do we even have an email field?
    # email = serializers.EmailField()
    bio = serializers.CharField()
    host = serializers.CharField()
    firstName = serializers.CharField()
    lastName = serializers.CharField()
    displayName = serializers.CharField()
    url = serializers.CharField()
    github = serializers.CharField()

    def create(self, validated_data):
        if User.objects.filter(id=validated_data['id']):
            return User.objects.get(id=validated_data['id'])
        else:
            # also host doesnt have to be our node, can be just random
            # mention this tmr
            usr = User.objects.create(
                id=validated_data['id'],
                bio=validated_data['bio'],
                displayName=validated_data['displayName'],
                host=validated_data['host'],
            )
            usr.set_unusable_password()
            usr.save()
            return usr