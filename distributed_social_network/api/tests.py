"""
Notes:
    - Unauthenticated requests are not tested because it's a check done by
    DjangoRestFramework (default permission set in settings.py). The response
    will always be 401. There is no reason to check this.
    - Serializer and paginator generated response is not checked.
    - Most response formatting is not checked. The content is checked, but
    format is not, unless it's a response not created by a serializer.
"""
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory

from posts.models import Post, Comment
from users.models import User, Node
from posts.utils import Visibility

import api.views as views
from rest_framework.test import force_authenticate

from django.urls import reverse
from django.conf import settings

import uuid


def create_test_user():
    return User.objects.create_user(
            username="test",
            email="test@test.com",
            bio="Hello world",
            password="aNewPw019",
            is_active=True
        )


def create_foreign_user(username="alien", hostname="http://testhost.com/", prefix="api/", api_user="apiUser"):
    node_usr = User.objects.create_user(
        username=api_user,
        email="api@user.com",
        password="aNewPw019",
        is_active=True
    )

    node = Node.objects.create(
        hostname=hostname,
        prefix=prefix,
        user_auth=node_usr,
        send_username="test",
        send_password="test",
        active=True
        )

    user = User.objects.create_user(
        host=node,
        username=username,
        password="aNewPw019",
        local=False,
        is_active=True
        )

    return user


def create_friend(username, usr):
    friend = User.objects.create_user(
            username=username,
            email="friend@test.com",
            bio="Chicken",
            password="aNewPw019",
            is_active=True
        )

    friend.friends.add(usr)

    return friend


def create_comment(post, author, comment='Test Comment'):
    return Comment.objects.create(
        author=author,
        post=post,
        comment=comment
    )


def create_test_post(author, title="test post", content="test", visibility=Visibility.PUBLIC, visbleTo=[]):
    post = Post.objects.create(
            title=title,
            content=content,
            author=author,
            visibility=visibility
        )
    post.origin = f"{settings.HOSTNAME}/{post.id}"
    post.source = f"{settings.HOSTNAME}/{post.id}"
    post.save()

    post.visible_to.add(*visbleTo)

    return post


class TestPostEndpoints(APITestCase):
    """
    Tests for the endpoints
        - /posts (GET)
        - /posts/post_id (GET)
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = create_test_user()

        cls.friend = create_friend("friend", cls.user)

        cls.foaf = create_friend("foaf", cls.friend)

        cls.post = create_test_post(cls.user, title="public")
        cls.comment = create_comment(cls.post, cls.friend)

        cls.private_post = create_test_post(cls.user, title="private", visibility=Visibility.PRIVATE)

        cls.foaf_post = create_test_post(cls.user, title="foaf", visibility=Visibility.FOAF)

        cls.factory = APIRequestFactory()

    def test_get_post_list(self):
        """
        Tests getting all public posts on server.
        endpoint: /posts
        """

        request = self.factory.get("api/posts")
        force_authenticate(request, user=self.user)

        response = views.PostViewSet.as_view({"get": "list"})(request)

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

        response = views.PostViewSet.as_view({"get": "retrieve"})(request, pk=pid)

        self.assertEqual(response.status_code, 404)

    def test_get_post_detail(self):
        """
        Get post detail of a post that exists.
        """
        request = self.factory.get(reverse('api-posts-detail', args=(self.post.id,)))
        force_authenticate(request, user=self.user)

        response = views.PostViewSet.as_view({"get": "retrieve"})(request, pk=self.post.id)

        self.assertEqual(str(self.post.id), response.data["post"]["id"])
        self.assertIn("getPost", response.data["query"])
        self.assertIn(str(self.comment.id), response.data["post"]["comments"][0]["id"])


class TestAuthorPostEndpoints(APITestCase):
    """
    Test for the endpoints
        - /author/posts (GET and POST)
        - /author/<author_id>/posts (GET)
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = create_test_user()
        cls.friend = create_friend("friend", cls.user)
        cls.foaf = create_friend("foaf", cls.friend)

        cls.alien = create_foreign_user()
        cls.alien.friends.add(cls.user)

        cls.post = create_test_post(cls.user)
        cls.usr_private = create_test_post(cls.user, title='private to user', visibility=Visibility.PRIVATE)
        cls.visibleToAlien = create_test_post(cls.user, title='visible to alient', visibility=Visibility.PRIVATE, visbleTo=[cls.alien])
        cls.foaf = create_test_post(cls.friend, title="foaf", visibility=Visibility.FOAF)
        cls.private = create_test_post(cls.friend, visibility=Visibility.PRIVATE)

        cls.factory = APIRequestFactory()

    def test_author_posts_no_header_get(self):
        """
        Test /author/posts GET without X-User header
        """
        request = self.factory.get(reverse("api-author-post"))
        force_authenticate(request, self.user)

        response = views.AuthorPostView.as_view()(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"detail": "Missing X-User Header Field"})

    def test_author_posts_get(self):
        """
        Test /author/posts GET with the X-User header, where user is recognized
        """

        request = self.factory.get(
            reverse("api-author-post"),
            HTTP_X_USER=self.alien.get_url())
        force_authenticate(request, self.alien.host.user_auth)

        response = views.AuthorPostView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["posts"]), 3)

        #  some formatting checks
        self.assertEqual(response.data["query"], "posts")
        self.assertDictContainsSubset({"count": 3}, response.data)

        #  grab the post ids from the response
        post_ids = [p["id"] for p in response.data["posts"]]

        # Check that the correct posts are in the response.
        self.assertIn(str(self.post.id), post_ids)
        self.assertIn(str(self.foaf.id), post_ids)
        self.assertIn(str(self.visibleToAlien.id), post_ids)
        self.assertNotIn(str(self.private), post_ids)

    def test_author_posts_no_header_post(self):
        """
        Test author/posts POST without X-User header
        """
        request = self.factory.post(
            reverse("api-author-post"),
            {
                "query": "createPost",
                "post": {
                    "id": uuid.uuid4()
                }
            },
            format="json"
        )
        force_authenticate(request, self.alien.host.user_auth)
        response = views.AuthorPostView.as_view()(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"detail": "Missing X-User Header Field"})

    def test_author_posts_non_match(self):
        """
        Test author/posts POST with header, where the author in post does not
        match the header user
        """
        request = self.factory.post(
            reverse("api-author-post"),
            {
                "query": "createPost",
                "post": {
                    "id": "069cc2ae-d9da-45e5-9604-9f133a2184fa",
                    "title": "Some post about chickens",
                    "source": "http://testhost.com/api/posts/069cc2ae-d9da-45e5-9604-9f133a2184fa",
                    "origin": "http://testhost.com/api/posts/069cc2ae-d9da-45e5-9604-9f133a2184fa",
                    "description": "ducks",
                    "contentType": "text/plain",
                    "content": "quack",
                    "author": {
                        "id": "http://testhost.com/api/author/bce6b38b-591d-4ca7-9c8e-96b50bf58cce",
                        "host": "http://testhost.com/api/",
                        "firstName": "",
                        "lastName": "",
                        "displayName": "alien",
                        "url": "http://testhost.com/api/author/bce6b38b-591d-4ca7-9c8e-96b50bf58cce",
                        "github": None
                    },
                    "categories": [],
                    "comments": [],
                    "published": "2019-04-04T03:38:39.886652Z",
                    "visibility": "Public",
                    "visibleTo": [],
                    "unlisted": False
                    }
                },
            format="json",
            HTTP_X_USER=self.alien.get_url()
        )
        force_authenticate(request, self.alien.host.user_auth)
        response = views.AuthorPostView.as_view()(request)

        self.assertEqual(response.status_code, 400)
        self.assertDictContainsSubset(response.data, {'message': 'Author of post does not match authenticated user.', 'query': 'createPost', 'type': False})

    def test_author_posts_invalid(self):
        """
        Test author/pots POST with header, where data is not invalid
        """

        request = self.factory.post(
            reverse("api-author-post"),

            {
                "id": "069cc2ae-d9da-45e5-9604-9f133a2184fa",
                "title": "Some post about chickens",
                "source": "http://testhost.com/api/posts/069cc2ae-d9da-45e5-9604-9f133a2184fa",
                "origin": "http://testhost.com/api/posts/069cc2ae-d9da-45e5-9604-9f133a2184fa",
                "description": "ducks",
                "contentType": "text/plain",
                "content": "quack",
                "author": {
                    "id": self.alien.get_url(),
                    "host": "http://testhost.com/api/",
                    "firstName": "",
                    "lastName": "",
                    "displayName": "alien",
                    "url": self.alien.get_url(),
                    "github": None
                },
                "categories": [],
                "comments": [],
                "unlisted": False
            },
            format="json",
            HTTP_X_USER=self.alien.get_url()
        )
        force_authenticate(request, self.alien.host.user_auth)
        response = views.AuthorPostView.as_view()(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'message': 'Malformed request', 'query': 'createPost', 'type': False})

    def test_author_posts_valid(self):
        """
        author/posts POST with header and valid post body
        """
        request = self.factory.post(
            reverse("api-author-post"),
            {
                "query": "createPost",
                "post": {
                    "id": "069cc2ae-d9da-45e5-9604-9f133a2184fa",
                    "title": "Some post about chickens",
                    "source": "http://testhost.com/api/posts/069cc2ae-d9da-45e5-9604-9f133a2184fa",
                    "origin": "http://testhost.com/api/posts/069cc2ae-d9da-45e5-9604-9f133a2184fa",
                    "description": "ducks",
                    "contentType": "text/plain",
                    "content": "quack",
                    "author": {
                        "id": self.alien.get_url(),
                        "host": "http://testhost.com/api/",
                        "firstName": "",
                        "lastName": "",
                        "displayName": "alien",
                        "url": self.alien.get_url(),
                        "github": None
                    },
                    "categories": [],
                    "comments": [],
                    "published": "2019-04-04T03:38:39.886652Z",
                    "visibility": "Public",
                    "visibleTo": [],
                    "unlisted": False
                    }
                },
            format="json",
            HTTP_X_USER=self.alien.get_url()
        )
        force_authenticate(request, self.alien.host.user_auth)
        response = views.AuthorPostView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertDictContainsSubset(response.data, {'message': 'Post created', 'query': 'createPost', 'type': True})

        self.assertTrue(Post.objects.filter(id="069cc2ae-d9da-45e5-9604-9f133a2184fa").exists())

    def test_author_id_posts_no_header(self):
        """
        Tests /author/<id>/posts endpoint without the X-User header
        """
        request = self.factory.get(
            reverse("api-author-posts", args=(str(self.user.id), )),
        )
        force_authenticate(request, self.alien.host.user_auth)
        response = views.AuthorViewset.as_view({'get': 'posts'})(request, pk=str(self.user.id))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"detail": "Missing X-User Header Field"})

    def test_author_id_posts_get(self):
        """
        Tests /author/<id>/posts with the X-User header, and a existant user
        """

        request = self.factory.get(
            reverse("api-author-posts", args=(str(self.user.id), )),
            HTTP_X_USER=self.alien.get_url()
        )
        force_authenticate(request, self.alien.host.user_auth)
        response = views.AuthorViewset.as_view({'get': 'posts'})(request, pk=str(self.user.id))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)

        # get the ids of returned posts
        pids = [p["id"] for p in response.data["posts"]]

        self.assertIn(str(self.post.id), pids)
        self.assertIn(str(self.visibleToAlien.id), pids)


class TestCommentEndpoints(APITestCase):
    """
    Tests for the endpoint /posts/<post_id>/comments (GET and POST)
    """
    @classmethod
    def setUpTestData(cls):
        cls.user = create_test_user()
        cls.post = create_test_post(cls.user)
        cls.post2 = create_test_post(cls.user, content="test post 2", visibility=Visibility.PRIVATE)

        cls.alien = create_foreign_user()

        cls.comment = create_comment(cls.post, cls.alien)
        cls.comment2 = create_comment(cls.post2, cls.user)

        cls.factory = APIRequestFactory()

    def test_comment_get(self):
        """
        Tests getting comments of a post
        /posts/<id>/comments
        """

        request = self.factory.get(
            reverse('api-comments', args=(str(self.post.id), ))
        )
        force_authenticate(request, self.alien.host.user_auth)

        response = views.CommentView.as_view()(request, pk=str(self.post.id))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

        cids = [c["id"] for c in response.data["comments"]]
        self.assertEqual(len(cids), 1)

        self.assertIn(str(self.comment.id), cids)

    def test_comment_post_unknown_foreign_author(self):
        """
        Tests /posts/<id>/comments POST with an unknown foreign author
        """
        c_id = "de305d54-75b4-431b-adb2-eb6b9e546013"
        request = self.factory.post(
            reverse('api-comments', args=(str(self.post.id), )),
            {
                "query": "addComment",
                "post": {
                    "id": c_id,
                    "contentType": "text/plain",
                    "comment": "Let's be frands!",
                    "published": "2019-03-09T13:07:04+00:00",
                    "author": {
                        "id": "http://testhost.com/e2c0c9ad-c518-42d4-9eb6-87c40f2ca151",
                        "email": "unknown@test.com",
                        "bio": "test",
                        "host": "http://testhost.com",
                        "firstName": "",
                        "lastName": "",
                        "displayName": "unknown",
                        "url": "http://testhost.com/e2c0c9ad-c518-42d4-9eb6-87c40f2ca151",
                        "github": None
                    }
                }
            },
            format="json"
        )
        force_authenticate(request, self.alien.host.user_auth)
        response = views.CommentView.as_view()(request, pk=str(self.post.id))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"query": "addComment", "type": True, "message": "Comment added"})
        self.assertTrue(Comment.objects.filter(id=c_id).exists())

    def test_comment_post_403(self):
        """
        Tests posting a comment on a private post.
        """

        c_id = "de305d54-75b4-431b-adb2-eb6b9e546013"
        request = self.factory.post(
            reverse('api-comments', args=(str(self.post2.id), )),
            {
                "query": "addComment",
                "post": {
                    "id": c_id,
                    "contentType": "text/plain",
                    "comment": "Let's be frands!",
                    "published": "2019-03-09T13:07:04+00:00",
                    "author": {
                        "id": self.alien.get_url(),
                        "email": self.alien.email,
                        "bio": self.alien.bio,
                        "host": str(self.alien.host),
                        "firstName": "",
                        "lastName": "",
                        "displayName": self.alien.username,
                        "url": self.alien.get_url(),
                        "github": None
                    }
                }
            },
            format="json"
        )
        force_authenticate(request, self.alien.host.user_auth)
        response = views.CommentView.as_view()(request, pk=str(self.post2.id))

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, {"query": "addComment", "type": False, "message": "Comment not allowed"})
        self.assertFalse(Comment.objects.filter(id=c_id).exists())


    def test_comment_post_known_author(self):
        """
        Tests /posts/<id>/comments POST with a known author of comment
        (foreign or local doesn't really matter here)
        """
        c_id = "de305d54-75b4-431b-adb2-eb6b9e546013"
        request = self.factory.post(
            reverse('api-comments', args=(str(self.post.id), )),
            {
                "query": "addComment",
                "post": {
                    "id": c_id,
                    "contentType": "text/plain",
                    "comment": "Let's be frands!",
                    "published": "2019-03-09T13:07:04+00:00",
                    "author": {
                        "id": self.alien.get_url(),
                        "email": self.alien.email,
                        "bio": self.alien.bio,
                        "host": str(self.alien.host),
                        "firstName": "",
                        "lastName": "",
                        "displayName": self.alien.username,
                        "url": self.alien.get_url(),
                        "github": None
                    }
                }
            },
            format="json"
        )
        force_authenticate(request, self.alien.host.user_auth)
        response = views.CommentView.as_view()(request, pk=str(self.post.id))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"query": "addComment", "type": True, "message": "Comment added"})
        self.assertTrue(Comment.objects.filter(id=c_id).exists())


    def test_comment_post_invalid(self):
        """
        Test /posts/<id>/comments POST with malformed data
        """
        request = self.factory.post(
            reverse('api-comments', args=(str(self.post.id), )),
            {
                "query": "addComment",
                "post": {
                }
            },
            format="json"
        )
        force_authenticate(request, self.alien.host.user_auth)

        response = views.CommentView.as_view()(request, pk=str(self.post.id))
        self.assertEqual(response.status_code, 400)


class TestFriendsEndpoints(APITestCase):
    """
    Test for the endpoints
        - /author/<author_id>/friends (GET and POST)
        - /author/<author1_id>/friends/<author2_id> (GET)
    """
    @classmethod
    def setUpTestData(cls):
        cls.user = create_test_user()
        cls.friend = create_friend("frand", cls.user)


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
