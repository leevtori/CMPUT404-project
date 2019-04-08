from django.test import TestCase
from django.test.client import Client
import json
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser

User = get_user_model()

class LoginTest(TestCase):
    username = "test1"
    password = "pass123"

    def setUp(self):
        User.objects.all().delete
        self.user = User.objects.create_user(username=self.username, email="test@test.com",
            bio="Hello world", password=self.password, is_active=1)

    def test_users(self):
        u = len(User.objects.all())
        self.assertEqual(u, 1)

    def test_login_fail(self):
        login = self.client.login(username="invalid_user", password='invalid_password')
        self.assertFalse(login)
    
    def test_login_success(self):
        login = self.client.login(username=self.user.username, password=self.password)
        self.assertTrue(login)

    def test_logout(self):
        logout=self.client.logout()
        self.assertEqual(logout, None)



class FriendsTest(TestCase):

    def setUp(self):
        self.alice = User.objects.create_user(
                    username="alice",
                    email="alice@test.com",
                    bio="Hello world",
                    password="aNewPw019",
                    is_active=1,
                )

        self.bob = User.objects.create_user(
            username="bob",
            email="bob@test.com",
            bio="Chicken",
            password="aNewPw019",
            is_active=1,
        )

        self.carl = User.objects.create_user(
            username="carl",
            email="carl@test.com",
            bio="Ostrich",
            password="aNewPw019",
            is_active=1,
        )
    
    def test_add_friend(self):
        #alice friends bob and carl
        self.alice.friends.add(self.bob)
        self.alice.friends.add(self.carl)
        alice_friends = self.alice.friends.all()
        self.assertTrue(self.bob in alice_friends)
        self.assertTrue(self.carl in alice_friends)


        #bob friends alice
        self.bob.friends.add(self.alice)
        bob_friends = self.bob.friends.all()
        self.assertTrue(self.alice in bob_friends)


    def test_add_follower(self):
        #bob follows alice
        self.alice.followers.add(self.bob)
        alice_followers = self.alice.followers.all()
        self.assertTrue(self.bob in alice_followers)

        self.bob.following.add(self.alice)
        bob_following = self.bob.following.all()
        self.assertTrue(self.alice in bob_following)

        #alice follows bob
        self.bob.followers.add(self.alice)
        bob_followers = self.bob.followers.all()
        self.assertTrue(self.alice in bob_followers)

        self.alice.following.add(self.bob)
        alice_following = self.alice.following.all()
        self.assertTrue(self.bob in alice_following)

    def test_delete_follower(self):
        #alice unfollows bob
        self.alice.following.remove(self.bob)
        alice_following = self.alice.following.all()
        self.assertFalse(self.bob in alice_following)

    def test_delete_friend(self):
        #alice deletes carl
        self.alice.friends.remove(self.carl)
        alice_friends = self.alice.friends.all()
        self.assertFalse(self.carl in alice_friends)




    # def test_add_friend_view(self):
    #     client = Client(enforce_csrf_checks = False)
    #     # log in as alice
    #     login = client.login(username=self.alice.username, password='aNewPw019')
    #     self.assertTrue(login)

    #     response = client.post('friends/add/', body={'id':str(self.carl.id)}, content_type='application/json')
    #     print(response)
    #     print(response.request)
    #     print(response.content)
        

    
