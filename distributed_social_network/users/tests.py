from django.test import TestCase
from django.test.client import Client
import json
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginTest(TestCase):
    client = Client()
    username = "test1"
    password = "pass123"

    register_input = {
        "username": "test1",
        "password": "pass123",
        "displayName": "moi_displayname",
        "github": "https://github.com/moimoi/",
        "bio": "I am moi, tu es toi",
        "firstName": "Moi",
        "lastName": "Toi",
        "email": "moi@gmail.com",
    }

    def setUp(self):
        User.objects.all().delete
        User.objects.create_user(username=self.username, password="pass123")

    def test_users(self):
        u = len(User.objects.all())
        self.assertEqual(u, 1)

    def test_login_fail(self):
        login = self.client.login(username="invalid_user", password='invalid_password')
        self.assertFalse(login)
        
    def test_login_pass(self):
        # register
        response = self.client.post("/users/signup/", data=self.register_input, 
            content_type="application/json")
        self.assertEqual(response.status_code, 200)
        # login
        response = self.client.post("/users/login/", data={
            "username": self.register_input["username"], 
            "password": self.register_input["password"]},
            content_type="application/json")
        self.assertEqual(response.status_code, 200)

# class FriendsTest(TestCase):

#     client = Client()
#     user1 = 'user1'
#     password1 = 'qwerty'
#     user2 = 'user2'
#     password2 = 'qwertypoiu'
#     user3 = 'user3'
#     password3 = 'qwertypoiu'
#     user4 = 'user4'
#     password4 = 'qwertypoiu'

#     def setUp(self):

#         user1 = User.objects.create_user(username=self.username, password=self.password)

#         self.u1 = User.objects.create_superuser(username=self.user1, password=self.password1)
#         User.objects.create_superuser(username=self.user2, password=self.password2)

#         self.User.objects.Create(host="http://127.0.0.1:8000/", displayName="Moi moi",github="http://github.com/moimoi", user=self.user1))
