from rest_framework import serializers
from users.models import User
from django.conf import settings


class FriendRequestUsers(serializers.ModelSerializer):
    id=serializers.SerializerMethodField()
    host = serializers.SerializerMethodField()
    displayName = serializers.CharField(source="username")
    url = serializers.SerializerMethodField(method_name="get_id")
    class Meta:
        model = User
        fields = (
            "id",
            "host",
            "displayName",
            "username",
            "url",
        )

    def get_id(self,obj):
        return obj.get_url()

    def get_host(self,obj):
        if obj.host!=None:
            return obj.host.hostname
        else:
            return settings.HOSTNAME





