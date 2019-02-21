from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.conf import settings

import uuid


class Node(models.Model):
    hostname = models.URLField()

    # TODO: Add node authentication info


class CustomUserManager(UserManager):

    def create_superuser(self, username, email, password, **extra_fields):
        host = Node.objects.get_or_create(hostname=settings.HOSTNAME)
        extra_fields["host_id"] = host[0].id
        extra_fields["is_active"] = True
         
        return super().create_superuser(username, email, password, **extra_fields)             


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    display_name = models.CharField(max_length=255)
    host = models.ForeignKey("Node", related_name="users", on_delete=models.CASCADE)
    github = models.URLField(null=True)
    # url = models.URLField()

    is_active = models.BooleanField(default=False)

    friends = models.ManyToManyField('self')

    objects = CustomUserManager()

    def get_url(self):
        return "%s/%s" % (self.host, self.id)