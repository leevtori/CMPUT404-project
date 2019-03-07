from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.conf import settings

import uuid


class Node(models.Model):
    hostname = models.URLField()

    # TODO: Add node authentication info


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    display_name = models.CharField(max_length=255)
    host = models.ForeignKey("Node", null=True, blank=True, default=None, on_delete=models.CASCADE)
    github = models.URLField(null=True)
    # url = models.URLField()

    is_active = models.BooleanField(default=False)

    friends = models.ManyToManyField('self')

    def get_url(self):
        return "%s/%s" % (self.host, self.id)