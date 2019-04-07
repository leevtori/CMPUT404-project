from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory

from posts.models import Post, Comment
from users.models import User
from posts.utils import Visibility

from .views import AuthorViewset, PostViewSet
from rest_framework.test import force_authenticate

from django.urls import reverse
from django.conf import settings

import uuid


class TestPostEndpoints(APITestCase):
    """
    Tests for the endpoints
        - /posts (GET)
        - /posts/post_id (GET)
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="test",
            email="test@test.com",
            bio="Hello world",
            password="aNewPw019"
        )

        cls.friend = User.objects.create_user(
            username="friend",
            email="friend@test.com",
            bio="Chicken",
            password="aNewPw019"
        )

        cls.foaf = User.objects.create_user(
            username="foaf",
            email="foaf@test.com",
            bio="Ostrich",
            password="aNewPw019"
        )

        cls.post = Post.objects.create(
            title="Public Post",
            content="Public post content",
            author=cls.user,
        )
        cls.post.source = settings.HOSTNAME + f"/{cls.post.id}"
        cls.post.origin = cls.post.source
        cls.post.save()

        cls.post.source = settings.HOSTNAME + f"/{cls.post.id}"
        cls.post.origin = cls.post.source
        cls.post.save()

        cls.comment = Comment.objects.create(
            author=cls.user,
            post=cls.post,
            comment="Test comment"
        )

        cls.private_post = Post.objects.create(
            title="Private",
            content="Should not be visible",
            author=cls.user,
            visibility=Visibility.PRIVATE
        )
        cls.private_post.source = settings.HOSTNAME + f"/{cls.private_post.id}"
        cls.private_post.origin = cls.private_post.source
        cls.private_post.save()

        cls.foaf_post = Post.objects.create(
            title="Foaf",
            content="Hello",
            author=cls.foaf,
            visibility=Visibility.FOAF
        )
        cls.foaf_post.source = settings.HOSTNAME + f"/{cls.foaf_post.id}"
        cls.foaf_post.origin = cls.foaf_post.source
        cls.foaf_post.save()

        cls.user.friends.add(cls.friend)
        cls.friend.friends.add(cls.user)

        cls.friend.friends.add(cls.foaf)
        cls.foaf.friends.add(cls.friend)

        cls.factory = APIRequestFactory()

    def test_get_post_list(self):
        """
        Tests getting all public posts on server.
        endpoint: /posts
        """

        request = self.factory.get("api/posts")
        force_authenticate(request, user=self.user)

        response = PostViewSet.as_view({"get": "list"})(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["posts"]), 1)
        # check that the only post is public (there only is one post!)
        self.assertEqual(response.data["posts"][0]["visibility"], "Public")

    def test_get_post_detail_dne(self):
        """
        Try to get details for a post that doesn't exist
        """
        # some uuid (chances that it's uuid is an actual post are slim)
        pid = uuid.uuid4()
        request = self.factory.get(reverse('api-posts-detail', args=(pid,)),)
        force_authenticate(request, user=self.user)

        response = PostViewSet.as_view({"get": "retrieve"})(request, pk=pid)

        self.assertEqual(response.status_code, 404)

    def test_get_post_detail(self):
        """
        Get post detail of a post that exists.
        """
        request = self.factory.get(reverse('api-posts-detail', args=(self.post.id,)))
        force_authenticate(request, user=self.user)

        response = PostViewSet.as_view({"get": "retrieve"})(request, pk=self.post.id)

        self.assertEqual(str(self.post.id), response.data["post"]["id"])
        self.assertIn("getPost", response.data["query"])
        self.assertIn(str(self.comment.id), response.data["post"]["comments"][0]["id"])


class TestAuthorPostEndpoints(APITestCase):
    """
    Test for the endpoints
        - /author/posts (GET and POST)
        - /author/<author_id>/posts (GET)
    """

    def test_author_posts_no_header_get(self):
        """
        Test /author/posts GET without X-User header
        """

    def test_author_posts_get_foreign(self):
        """
        Test /author/posts GET with the X-User header, where user is a foreign
        author
        """

    def test_author_posts_get_local(self):
        """
        Test /author/posts GET with the X-User header, where the user is a local
        author
        """

    def test_author_posts_no_header_post(self):
        """
        Test author/posts POST without X-User header
        """

    def test_author_posts_non_match(self):
        """
        Test author/posts POST with header, where the author in post does not
        match the header user
        """

    def test_author_posts_invalid(self):
        """
        Test author/pots POST with header, where data is not invalid
        """

    def test_author_posts_valid(self):
        """
        author/posts POST with header and valid post body
        """

    def test_author_id_posts_no_header(self):
        """
        Tests /author/<id>/posts endpoint without the X-User header
        """

    def test_author_id_posts_get(self):
        """
        Tests /author/<id>/posts with the X-User header, and a existant user
        """


class TestCommentEndpoints(APITestCase):
    """
    Tests for the endpoint /posts/<post_id>/comments (GET and POST)
    """

    def test_comment_get(self):
        """
        Tests getting comments of a post
        /posts/<id>/comments
        """

    def test_comment_post_unknown_foreign_author(self):
        """
        Tests /posts/<id>/comments POST with an unknown foreign author
        """

    def test_comment_post_known_author(self):
        """
        Tests /posts/<id>/comments POST with a known author of comment
        (foreign or local doesn't really matter here)
        """

    def test_comment_post_invalid(self):
        """
        Test /posts/<id>/comments POST with malformed data
        """


class TestFriendsEndpoints(APITestCase):
    """
    Test for the endpoints
        - /author/<author_id>/friends (GET and POST)
        - /author/<author1_id>/friends/<author2_id> (GET)
    """
    @classmethod
    def setUpTestData(cls):

        cls.user = User.objects.create_user(
            username="test",
            email="test@test.com",
            bio="Hello world",
            password="aNewPw019",
            is_active=True
        )

        cls.friend = User.objects.create_user(
            username="friend",
            email="friend@test.com",
            bio="Chicken",
            password="aNewPw019",
            is_active=True
        )

        cls.other_user = User.objects.create_user(
            username="foaf",
            email="foaf@test.com",
            bio="Ostrich",
            password="aNewPw019",
            is_active=True
        )

        cls.user.friends.add(cls.friend)

        cls.friend.friends.add(cls.user)

        cls.factory = APIRequestFactory()

    def test_friends_get_exists(self):
        """
        Get friends of an existant author on local server
        Tests getting a list of friends of an author.
        endpoint: /user/<userid>/friends
        """

    def test_friends_get_unknown(self):
        """
        Get friends of a non-extant author on local server.
        expects a 404 response.
        """

    def test_friends_post_malformed(self):
        """
        test malformed POST to /user/<id>/friends
        """

    def test_friends_post_valid(self):
        """
        tests POST to /user/<id>/friends
        """

    def test_author_friend_id_true(self):
        """
        tests GET to /author/<id1>/friends/<id2>,
        where id2 is a friend
        """

    def test_author_friend_id_false(self):
        """
        tests GET to /author/<id1>/friends/<id2>
        where id2 is not a friend
        """


class TestFriendRequestEndpoint(APITestCase):
    """
    Tests for endpoint /friendrequest (POST)
    """
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="test",
            email="test@test.com",
            bio="Hello world",
            password="aNewPw019",
            is_active=True
        )

    def test_friend_does_not_exist(self):
        """
        Test that the local "friend" parameter does not exists
        Should return an error
        """

    def test_local_author(self):
        """
        author is a local user, and exists.
        """

    def test_known_remote_author(self):
        """
        test remote author in our database
        """

    def test_unknown_remote_existing_author(self):
        """
        Test with an unknown author from a foreign host.
        Author does exist on foreign host.
        """


class TestAuthorEndpoint(APITestCase):
    """
    Tests for the endpoint /author/<author_id>
    """

    def test_author_id_get_exists(self):
        """
        author id exists
        """

    def test_author_id_get_dne(self):
        """
        Author with id does not exists. should return an error
        """


# class TestAuthorViewSet(APITestCase):
#     @classmethod
#     def setUpTestData(cls):

#         cls.user = User.objects.create_user(
#             username="test",
#             email="test@test.com",
#             bio="Hello world",
#             password="aNewPw019",
#             is_active=True
#         )

#         cls.friend = User.objects.create_user(
#             username="friend",
#             email="friend@test.com",
#             bio="Chicken",
#             password="aNewPw019",
#             is_active=True
#         )

#         cls.other_user = User.objects.create_user(
#             username="foaf",
#             email="foaf@test.com",
#             bio="Ostrich",
#             password="aNewPw019",
#             is_active=True
#         )

#         cls.user.friends.add(cls.friend)    # TODO: TEST the friend action (actions don't seem to work with as_view?)

#         cls.friend.friends.add(cls.user)

#         cls.factory = APIRequestFactory()

#     def test_get_friends(self):
#         """import json
#         Tests getting a list of friends
#         endpoint: /user/<userid>/friends
#         """

#         # request = self.factory.get(
#         #     "api/author/%s/friends/" % self.user.id
#         # )

#         # view = AuthorViewset.as_view({'get': 'friend'})
#         # response = view(request, pk=self.user.id)

#         # self.assertEqual(response.status_code, 200)
#         # self.assertIn(response, self.friend.id)


#     def test_post_friends_none(self):
#         """
#         Tests checking if anyone in post body is a friend.
#         endpoint: /user/<userid>/friends
#         """
#         request = self.factory.post(
#             "api/author/%s/friends/" % self.user.id,
#             {
#                 "query": "friends",
#                 "author": "author_id",
#                 "authors": [
#                     "http://127.0.0.1:5454/author/de305d54-75b4-431b-adb2-eb6b9e546013",
#                     "http://127.0.0.1:5454/author/ae345d54-75b4-431b-adb2-fb6b9e547891"
#                 ]
#             }
#         )

#         force_authenticate(request, user=self.user)

#         view = AuthorViewset.as_view({'post': 'friend'})
#         response = view(request, pk=self.user.id)
#         self.assertEqual(response.status_code, 200)


#     def test_retrieve_author(self):
#         request = self.factory.get("/api/author/%s/" % self.user.id)

#         response = AuthorViewset.as_view({"get": "retrieve"})(request, pk=self.user.id)

#         self.assertEqual(response.status_code, 200)

#         self.assertEqual(response.data["id"], self.user.get_url())


# class TestPostViewSet(APITestCase):
#     @classmethod
#     def setUpTestData(cls):
#         cls.user = User.objects.create_user(
#             username="test",
#             email="test@test.com",
#             bio="Hello world",
#             password="aNewPw019"
#         )

#         cls.friend = User.objects.create_user(
#             username="friend",
#             email="friend@test.com",
#             bio="Chicken",
#             password="aNewPw019"
#         )

#         cls.foaf = User.objects.create_user(
#             username="foaf",
#             email="foaf@test.com",
#             bio="Ostrich",
#             password="aNewPw019"
#         )

#         cls.post = Post.objects.create(
#             title="Public Post",
#             content="Public post content",
#             author=cls.user
#         )

#         cls.comment = Comment.objects.create(
#             author=cls.user,
#             post=cls.post,
#             comment="Test comment"
#         )

#         cls.private_post = Post.objects.create(
#             title="Private",
#             content="Should not be visible",
#             author=cls.user,
#             visibility=Visibility.PRIVATE
#         )

#         cls.foaf_post = Post.objects.create(
#             title="Foaf",
#             content="Hello",
#             author=cls.foaf,
#             visibility=Visibility.FOAF
#         )

#         cls.user.friends.add(cls.friend)
#         cls.friend.friends.add(cls.user)

#         cls.friend.friends.add(cls.foaf)
#         cls.foaf.friends.add(cls.friend)

#         cls.factory = APIRequestFactory()


#     # def test_comment_post(self):
#     #     """
#     #     Test creating a comment for a specific post.
#     #     endpoint; /posts/<post_id>/comments
#     #     Currently not implemented.
#     #     """

#     def test_get_post_list(self):
#         """
#         Tests getting all public posts on server.
#         endpoint: /posts
#         """

#         request = self.factory.get("api/posts")

#         response = PostViewSet.as_view({"get": "list"})(request)

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.data), 1)
#         self.assertEqual(response.data[0]["visibility"], "Public")


# class TestAreFriendsView(APITestCase):
#     """
#     Not tested because none of this is implemented.
#     """
#     @classmethod
#     def setUpTestData(cls):
#         cls.user = User.objects.create_user(
#                 username="test",
#                 email="test@test.com",
#                 bio="Hello world",
#                 password="aNewPw019"
#         )

#         cls.friend = User.objects.create_user(
#             username="friend",
#             email="friend@test.com",
#             bio="Chicken",
#             password="aNewPw019"
#         )

#         cls.factory = APIRequestFactory()


#     # def test_are_friends(self):
#     #     """
#     #     Result if author1 and author2 are friends
#     #     endpoint: /author/<author1_id>/friends/<author2_id>
#     #     """

#     # def test_not_friends(self):
#     #     """
#     #     Result if author1 and author2 are not friends.
#     #     endpoint: /author/<author1_id>/friends/<author2_id>
#     #     """
