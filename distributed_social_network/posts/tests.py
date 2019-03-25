from django.test import TestCase, Client
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse

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
            password="aNewPw019",
            is_active=1,
        )

        self.friend = User.objects.create_user(
            username="friend",
            email="friend@test.com",
            bio="Chicken",
            password="aNewPw019",
            is_active=1,
        )

        self.foaf = User.objects.create_user(
            username="foaf",
            email="foaf@test.com",
            bio="Ostrich",
            password="aNewPw019",
            is_active=1,
        )

        self.post = Post.objects.create(
            title="Public Post",
            content="Public post content",
            author=self.user,
            source='uuid1',
        )

        self.comment = Comment.objects.create(
            author=self.user,
            post=self.post,
            comment="Test comment",
        )

        self.private_post = Post.objects.create(
            title="Private",
            content="Should not be visible",
            author=self.user,
            visibility=Visibility.PRIVATE,
            source='uuid2',
        )

        self.foaf_post = Post.objects.create(
            title="Foaf",
            content="Hello",
            author=self.foaf,
            visibility=Visibility.FOAF,
            source='uuid1',
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


    def test_view_post_logout(self):
        # log out
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], AnonymousUser())

        #try to view feed
        print('soruce', self.post.source)
        response = self.client.get(reverse('post-detail', args=[self.post.source]))
        self.assertNotEqual(response.status_code, 200)
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 302)

    def test_create_post(self):
        login = self.client.login(username=self.user.username, password='aNewPw019')
        self.assertTrue(login)
        




