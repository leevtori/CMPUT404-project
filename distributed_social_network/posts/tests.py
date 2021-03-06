from django.test import TestCase, Client, TransactionTestCase
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse

from posts.models import Post, Comment
from users.models import User, Node

import posts.views as views
from posts.utils import Visibility

from django.views.generic import ListView
from django.test.client import RequestFactory
from django.conf import settings
from urllib.parse import urljoin


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

        self.friend2 = User.objects.create_user(
            username="friend2",
            email="friend2@test.com",
            bio="Turkey",
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

        self.post = self.create_post("Public Post", "Public post content", self.user, Visibility.PUBLIC)

        self.comment = Comment.objects.create(
            author=self.user,
            post=self.post,
            comment="Test comment",
        )

        self.private_post = self.create_post("Private", "Should not be visible", self.friend, Visibility.PRIVATE)

        self.foaf_post = self.create_post("Foaf", "Hello", self.foaf, Visibility.FOAF)

        self.user.friends.add(self.friend)
        self.friend.friends.add(self.user)

        self.user.friends.add(self.friend2)
        self.friend2.friends.add(self.user)

        self.friend.friends.add(self.foaf)
        self.foaf.friends.add(self.friend)

    def create_post(self, _title, _content, _author, _vis):
        post = Post.objects.create(
            title=_title,
            content=_content,
            author=_author,
            visibility = _vis
        )
        post.source = urljoin(settings.HOSTNAME, '/api/posts/%s' % post.id)
        post.origin = urljoin(settings.HOSTNAME, '/api/posts/%s' % post.id)
        return post


    def test_view_pub_post_loggedout(self):
        #try to view public post detail without logging in
        response = self.client.get(reverse('postdetail', args=[self.post.id]))
        self.assertEqual(response.status_code, 302)

    def test_view_prv_post_loggedout(self):
        #try to view private post detail without logging in
        response = self.client.get(reverse('postdetail', args=[self.private_post.id]))
        self.assertEqual(response.status_code, 302)

    def test_view_foaf_post_loggedout(self):
        #try to view foaf post detail without logging in
        response = self.client.get(reverse('postdetail', args=[self.foaf_post.id]))
        self.assertEqual(response.status_code, 302)

    def test_view_feed_loggedout(self):
         #try to view feed
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 302)

    def test_view_postdetail_loggedin(self):
        #log in
        login = self.client.login(username=self.user.username, password='aNewPw019')
        self.assertTrue(login)
        response = self.client.get(reverse('postdetail', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)

        #check comments
        comments = response.context['post_comments']
        self.assertTrue(self.comment in comments)
        


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
        post = self.create_post("Test Post 1", "Test pub post", self.user, Visibility.PUBLIC)

        # log in as myself
        login = self.client.login(username=self.user.username, password='aNewPw019')
        self.assertTrue(login)

        # check if it's on my feed
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 200)
        public_feed_posts = response.context['object_list']
        self.assertTrue(post in public_feed_posts)

        # check if it's on my profile
        response = self.client.get(reverse('profile', args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
        profile_posts = response.context['object_list']
        self.assertTrue(post in profile_posts)


    def test_add_private_post(self):
        post = self.create_post("Test Post 2", "Test priv post", self.user, Visibility.PRIVATE)

        #log in as myself
        login = self.client.login(username=self.user, password='aNewPw019')
        self.assertTrue(login)
        #check if it's on my feed
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 200)
        public_feed_posts = response.context['object_list']
        self.assertTrue(post in public_feed_posts)

        #log out
        self.client.logout()

        # log in as friend
        login = self.client.login(username=self.friend, password='aNewPw019')
        self.assertTrue(login)
        # check if it's on friend's feed
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 200)
        public_feed_posts = response.context['object_list']
        self.assertFalse(post in public_feed_posts)

        #give visibility to a special friend
        post.visible_to.add(self.friend2)
        #log in as special friend
        login = self.client.login(username=self.friend2, password='aNewPw019')
        self.assertTrue(login)
        # check if it's on special friend's feed
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 200)
        public_feed_posts = response.context['object_list']
        self.assertTrue(post in public_feed_posts)


    def test_add_friendsonly_post(self):
        post = self.create_post("Test Post 3", "Test friends only post", self.user, Visibility.FRIENDSONLY)

        # log in as friend
        login = self.client.login(username=self.friend, password='aNewPw019')
        self.assertTrue(login)
        # check if it's on friend's feed
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 200)
        public_feed_posts = response.context['object_list']
        self.assertTrue(post in public_feed_posts)

        #log in as non-friend - foaf
        self.client.logout()
        login = self.client.login(username=self.foaf, password='aNewPw019')
        self.assertTrue(login)
        # check if it's on foaf's feed
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 200)
        public_feed_posts = response.context['object_list']
        self.assertFalse(post in public_feed_posts)

    def test_add_foaf_post(self):
        post = self.create_post("Test Post 4", "Test foaf post", self.user, Visibility.FOAF)
        
        # log in as friend
        login = self.client.login(username=self.friend, password='aNewPw019')
        self.assertTrue(login)
        # check if it's on friend's feed
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 200)
        public_feed_posts = response.context['object_list']
        self.assertTrue(post in public_feed_posts)

        #log in as foaf
        self.client.logout()
        login = self.client.login(username=self.foaf, password='aNewPw019')
        self.assertTrue(login)
        # check if it's on foaf's feed
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 200)
        public_feed_posts = response.context['object_list']
        self.assertTrue(post in public_feed_posts)

    def test_delete_post(self):
        post = self.create_post("Test Post 5", "Delete me", self.user, Visibility.PUBLIC)

        #log in as me
        login = self.client.login(username=self.user, password='aNewPw019')
        self.assertTrue(login)
        # check if it's on the feed
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 200)
        public_feed_posts = response.context['object_list']
        self.assertTrue(post in public_feed_posts)

        response = self.client.get(reverse('deletepost', args=[post.id]))
        self.assertEqual(response.status_code, 302)

        # check if it's on the feed
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 200)
        public_feed_posts = response.context['object_list']
        self.assertFalse(post in public_feed_posts)

    def test_delete_others_post(self):
        #log in
        login = self.client.login(username=self.friend, password='aNewPw019')
        self.assertTrue(login)

        response = self.client.get(reverse('deletepost', args=[self.post.id]))
        self.assertEqual(response.status_code, 404)



        




