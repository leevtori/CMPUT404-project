from django.test import TestCase, Client, TransactionTestCase
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse

from posts.models import Post, Comment
from users.models import User

import posts.views as views
from posts.utils import Visibility

from django.views.generic import ListView
from django.test.client import RequestFactory

# Create your tests here.

# class PostTestCase(TestCase):
#     def setup(self):
#         Comment.objects.create()


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
        )

        self.comment = Comment.objects.create(
            author=self.user,
            post=self.post,
            comment="Test comment",
        )

        self.private_post = Post.objects.create(
            title="Private",
            content="Should not be visible",
            author=self.friend,
            visibility=Visibility.PRIVATE,
        )

        self.foaf_post = Post.objects.create(
            title="Foaf",
            content="Hello",
            author=self.foaf,
            visibility=Visibility.FOAF,
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



class TestPosts(TestCase):

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
        )

        self.comment = Comment.objects.create(
            author=self.user,
            post=self.post,
            comment="Test comment",
        )

        self.private_post = Post.objects.create(
            title="Private",
            content="Should not be visible",
            author=self.friend,
            visibility=Visibility.PRIVATE,
        )

        self.foaf_post = Post.objects.create(
            title="Foaf",
            content="Hello",
            author=self.foaf,
            visibility=Visibility.FOAF,
        )

        self.user.friends.add(self.friend)
        self.friend.friends.add(self.user)

        self.friend.friends.add(self.foaf)
        self.foaf.friends.add(self.friend)


    def test_view_post_logout(self):
        #try to view public post detail without logging in
        response = self.client.get(reverse('create', args=[self.post.id]))
        self.assertEqual(response.status_code, 302)

        #try to view public post detail without logging in
        response = self.client.get(reverse('create', args=[self.private_post.id]))
        self.assertEqual(response.status_code, 302)

        #try to view public post detail without logging in
        response = self.client.get(reverse('create', args=[self.foaf_post.id]))
        self.assertEqual(response.status_code, 302)

         #try to view feed
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 302)

    def test_feed(self):
        # log in
        login = self.client.login(username=self.user.username, password='aNewPw019')
        self.assertTrue(login)

        # view feed
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 200)

        # test public feed
        public_feed_posts = response.context['object_list']
        self.assertTrue(self.post in public_feed_posts)
        self.assertTrue(self.foaf_post in public_feed_posts)
        self.assertFalse(self.private_post in public_feed_posts)


    def test_add_public_post(self):
        post = Post.objects.create(
            title="Test Post 1",
            content="Test public post",
            author=self.user,
        )
        # log in
        login = self.client.login(username=self.user.username, password='aNewPw019')
        self.assertTrue(login)

        # check if it's on the feed
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 200)
        public_feed_posts = response.context['object_list']
        self.assertTrue(post in public_feed_posts)

        # check if it's on their profile
        response = self.client.get(reverse('profile', args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
        profile_posts = response.context['object_list']
        self.assertTrue(post in profile_posts)

        #check post detail
        response = self.client.get(reverse('create', args=[post.id]))
        self.assertEqual(response.status_code, 200)

    def test_add_private_post(self):
        post = Post.objects.create(
            title="Test Post 2",
            content="Test private post",
            author=self.user,
            visibility=Visibility.PRIVATE,
        )

        # log in as friend
        login = self.client.login(username=self.friend, password='aNewPw019')
        self.assertTrue(login)
        # check if it's on friend's feed
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 200)
        public_feed_posts = response.context['object_list']
        self.assertFalse(post in public_feed_posts)


    
    def test_add_private_post(self):
        post = Post.objects.create(
            title="Test Post 3",
            content="Test private post",
            author=self.user,
            visibility=Visibility.PRIVATE,
        )

        # log in as friend
        login = self.client.login(username=self.friend, password='aNewPw019')
        self.assertTrue(login)
        # check if it's on friend's feed
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 200)
        public_feed_posts = response.context['object_list']
        self.assertFalse(post in public_feed_posts)

    def test_add_friendsonly_post(self):
        post = Post.objects.create(
            title="Test Post 3",
            content="Test friends only post",
            author=self.user,
            visibility=Visibility.FRIENDSONLY,
        )

        # log in as friend
        login = self.client.login(username=self.friend, password='aNewPw019')
        self.assertTrue(login)
        # check if it's on friend's feed
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 200)
        public_feed_posts = response.context['object_list']
        self.assertTrue(post in public_feed_posts)

        #log in as non-friend
        self.client.logout()
        login = self.client.login(username=self.foaf, password='aNewPw019')
        self.assertTrue(login)
        # check if it's on foaf's feed (it shouldn't)
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 200)
        public_feed_posts = response.context['object_list']
        self.assertFalse(post in public_feed_posts)


    #TODO: create foaf post


        
        




