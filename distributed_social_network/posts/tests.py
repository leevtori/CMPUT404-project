from django.test import TestCase

from posts.models import Post, Comment

# Create your tests here.

class PostTestCase(TestCase):
    def setup(self):
        Post.objects.create()

