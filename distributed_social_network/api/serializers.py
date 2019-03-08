from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

from posts.models import Post

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'display_name', 'github')


class PostSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = "__all__"

    def get_count(self, obj):
        return obj.comment_set.count()