from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory

from posts.models import Post, Comment
from users.models import User
from posts.utils import Visibility

from .views import AuthorViewset, PostViewSet
from rest_framework.test import force_authenticate


class TestAuthorViewSet(APITestCase):
    # TODO: TEST the friend action (actions don't seem to work with as_view?)
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

    def test_get_friends(self):
        """import json
        Tests getting a list of friends
        endpoint: /user/<userid>/friends
        """

        request = self.factory.get(
            "api/author/%s/friends/" % self.user.id
        )

        view = AuthorViewset.as_view({'get': 'friend'})
        response = view(request, pk=self.user.id)

        self.assertEqual(response.status_code, 200)

    def test_post_friends_none(self):
        """
        Tests checking if anyone in post body is a friend.
        endpoint: /user/<userid>/friends
        """
        request = self.factory.post(
            "api/author/%s/friends/" % self.user.id,
            {
                "query": "friends",
                "author": "author_id",
                "authors": [
                    "http://127.0.0.1:5454/author/de305d54-75b4-431b-adb2-eb6b9e546013",
                    "http://127.0.0.1:5454/author/ae345d54-75b4-431b-adb2-fb6b9e547891"
                ]
            }
        )

        force_authenticate(request, user=self.user)

        view = AuthorViewset.as_view({'post': 'friend'})
        response = view(request, pk=self.user.id)
        self.assertEqual(response.status_code, 200)


    def test_retrieve_author(self):
        request = self.factory.get("/api/author/%s/" % self.user.id)

        response = AuthorViewset.as_view({"get": "retrieve"})(request, pk=self.user.id)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data["id"], self.user.get_url())


class TestPostViewSet(APITestCase):
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
            author=cls.user
        )

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

        cls.foaf_post = Post.objects.create(
            title="Foaf",
            content="Hello",
            author=cls.foaf,
            visibility=Visibility.FOAF
        )

        cls.user.friends.add(cls.friend)
        cls.friend.friends.add(cls.user)

        cls.friend.friends.add(cls.foaf)
        cls.foaf.friends.add(cls.friend)

        cls.factory = APIRequestFactory()


    # def test_comment_post(self):
    #     """
    #     Test creating a comment for a specific post.
    #     endpoint; /posts/<post_id>/comments
    #     Currently not implemented.
    #     """

    def test_get_post_list(self):
        """
        Tests getting all public posts on server.
        endpoint: /posts
        """

        request = self.factory.get("api/posts")

        response = PostViewSet.as_view({"get": "list"})(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["visibility"], "Public")


class TestAreFriendsView(APITestCase):
    """
    Not tested because none of this is implemented.
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

        cls.factory = APIRequestFactory()


    # def test_are_friends(self):
    #     """
    #     Result if author1 and author2 are friends
    #     endpoint: /author/<author1_id>/friends/<author2_id>
    #     """

    # def test_not_friends(self):
    #     """
    #     Result if author1 and author2 are not friends.
    #     endpoint: /author/<author1_id>/friends/<author2_id>
    #     """
