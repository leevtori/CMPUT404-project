from django.test import TestCase

from posts.models import Post, Comment
from users.models import User

import posts.views as views
from posts.utils import Visibility

from django.views.generic import ListView
from django.test.client import RequestFactory

# Create your tests here.

class PostTestCase(TestCase):
    def setup(self):
        Comment.objects.create()


class TestPostVisbilityMixin(TestCase):
    class DummyBase():
        def __init__(self):
            factory = RequestFactory()
            self.request = factory.get('someurl')

        def get_queryset(*arge, **kwargs):
            return Post.objects.all()

    class DummyClass(views.PostVisbilityMixin, DummyBase):
        pass

    def setUp(self):
        self.user = User.objects.create_user(
            username="test",
            email="test@test.com",
            bio="Hello world",
            password="aNewPw019"
        )

        self.friend = User.objects.create_user(
            username="friend",
            email="friend@test.com",
            bio="Chicken",
            password="aNewPw019"
        )

        self.foaf = User.objects.create_user(
            username="foaf",
            email="foaf@test.com",
            bio="Ostrich",
            password="aNewPw019"
        )

        self.post = Post.objects.create(
            title="Public Post",
            content="Public post content",
            author=self.user
        )

        self.comment = Comment.objects.create(
            author=self.user,
            post=self.post,
            comment="Test comment"
        )

        self.private_post = Post.objects.create(
            title="Private",
            content="Should not be visible",
            author=self.user,
            visibility=Visibility.PRIVATE
        )

        self.foaf_post = Post.objects.create(
            title="Foaf",
            content="Hello",
            author=self.foaf,
            visibility=Visibility.FOAF
        )

        self.user.friends.add(self.friend)
        self.friend.friends.add(self.user)

        self.friend.friends.add(self.foaf)
        self.foaf.friends.add(self.friend)


    def test_mixin(self):
        c = self.DummyClass()
        c.request.user = self.user

        qs = c.get_queryset()

        self.assertTrue(qs.exists())

        # public
        self.assertTrue(qs.filter(id=self.post.id).exists())

        # private
        self.assertFalse(qs.filter(id=self.private_post.id).exists())

        # foaf
        self.assertTrue(qs.filter(id=self.foaf_post.id).exists())
