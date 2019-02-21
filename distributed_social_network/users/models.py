from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    id = models.UUIDField(primary_key=True)

    display_name = models.CharField(max_length=255)
    host = models.ForeignKey("Node", related_name="users", on_delete=models.CASCADE)
    github = models.URLField()
    url = models.URLField()

    is_active = models.BooleanField(default=False)

    friends = models.ManyToManyField('self')


class Node(models.Model):
    hostname = models.URLField()

    # TODO: Add node authentication info
    