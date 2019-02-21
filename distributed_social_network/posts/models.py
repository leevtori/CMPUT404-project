from django.db import models
from django.conf import settings

from .utils import ContentType, Visibility


class Post (models.Model):
    id = models.UUIDField(primary_key=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    published = models.DateTimeField(auto_now_add=True)
    
    title = models.CharField(max_length=255)
    content = models.TextField()
    source = models.CharField(max_length=255)
    origin = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    
    content_type = models.CharField(choices=ContentType.get_choices(), max_length=3, default=ContentType.PLAIN)
    
    categories = models.ManyToManyField('Categories')
    
    visiblilty = models.CharField(choices=Visibility.get_choices(), max_length=4, default=Visibility.PUBLIC)
    visible_to = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="visible_posts")

    unlisted = models.BooleanField(default=False)


class Categories (models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class attachments(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    file = models.FileField()  # TODO: Configure file serving and saving


class Comment (models.Model):
    id = models.UUIDField(primary_key=True)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)

    published = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    content_type = models.CharField(choices=ContentType.get_choices(), max_length=3, default=ContentType.PLAIN)


class Node(models.Model):
    hostname = models.CharField(max_length=255)
