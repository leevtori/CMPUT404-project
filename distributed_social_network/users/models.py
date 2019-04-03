from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.conf import settings
from urllib.parse import urlparse
from urllib.parse import urljoin
from posts.models import Post

import uuid



# TODO: Add node authentication info
class Node(models.Model):
    # objects = NodeManager()
    hostname = models.URLField()
    user_auth = models.OneToOneField("User", on_delete=models.CASCADE)
    prefix = models.CharField(max_length=20, blank=True)
    send_username = models.CharField(max_length=100)
    send_password = models.CharField(max_length=100)
    active = models.BooleanField(default=False)

    def __str__(self):
        return urljoin(self.hostname, self.prefix)


class CustomUserManager(UserManager):

    def create_superuser(self, username, email, password, **extra_fields):
        # host = Node.objects.get_or_create(hostname=settings.HOSTNAME)
        # extra_fields["host_id"] = host[0].id
        extra_fields["is_active"] = True

        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    objects = CustomUserManager()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    display_name = models.CharField(max_length=255)
    host = models.ForeignKey("Node", null=True, blank=True, default=None, on_delete=models.CASCADE)
    github = models.URLField(null=True)
    bio = models.TextField(blank=True)
    local= models.BooleanField(default=True)

    is_active = models.BooleanField(default=False)

    friends = models.ManyToManyField('self', blank=True)
    followers = models.ManyToManyField('self', blank=True, symmetrical=False)
    following = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='following_list')
    incomingRequests = models.ManyToManyField('self', blank=True, symmetrical=False, related_name="incoming_requests")
    outgoingRequests = models.ManyToManyField('self', blank=True, symmetrical=False, related_name="outgoing_requests")

    def get_url(self):
        host = self.host or settings.HOSTNAME
        val = urljoin(str(host), 'author')
        if val[-1] != '/': val+='/'
        val= urljoin(val, str(self.id))
        return val

    def get_friends_posts(self):
        p = Post.objects.all().filter(author__in=self.friends)
        print("OISTS ", p)
        posts = p.values_list("title", flat=True)
        print("posts ", posts)
        return ", ".join(posts)
