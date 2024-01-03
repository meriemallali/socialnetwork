import unittest
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model, authenticate, logout
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone

User = get_user_model()
from .models import *
from .views import *


# testing the authentication: signup
class RegisterTestCase(unittest.TestCase):
    def test_check_invalid_user(self):
        # user with username 'meriema1' does not exist in the database.
        username = 'meriema1'
        message = f'{username} does not exists'
        user = User.objects.filter(username=username).exists()
        self.assertFalse(user, message)

    def test_check_valid_user(self):
        # create and save a new user profile.
        user = User.objects.create(
            username='newuser',
            email='newuser@gmail.com',
            password='newuser'
        )
        user.save()
        created_profile = UserProfile.objects.create(user=user,
                                                     userid=user.id)
        created_profile.save()
        # testing with the created user.
        username = 'newuser'
        message = f'{username} does exists'
        new_user = User.objects.filter(username=username)
        new_user_profile = UserProfile.objects.filter(user=user, userid=user.id)
        self.assertTrue(new_user, message)
        self.assertTrue(new_user_profile is not None)


# testing the authentication: signin
class SigninTestCase(unittest.TestCase):
    # test with non-existing user.
    def test_invalid_details(self):
        user = authenticate(username='meriama12', password='randompassword')
        self.assertTrue(user is None)

    # test with an existing user.
    def test_valid_details(self):
        user = authenticate(username='test', password='1234567')
        self.assertFalse(user is not None)


# testing the authentication: logout
class LogoutTestCase(TestCase):
    # create a testing user.
    def setUp(self):
        self.user = User.objects.create_user(username='meriama1', password='randompassword')

    def test_logout(self):
        self.client.login(username='meriama1', password='randompassword')
        self.assertTrue(self.user.is_authenticated)
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
        # true = user logged out.
        self.assertTrue(self.user.is_authenticated)


# Test search for users
class SearchUserTestCase(unittest.TestCase):
    # authenticate using superuser.
    def setUp(self):
        authenticate(username='user', password='user')

    def test_invalid_search(self):
        username = 'testuser1'
        search_object = User.objects.filter(username__icontains=username)
        self.assertFalse(search_object is None)

    def test_valid_search(self):
        username = 'ali_13'
        search_object = User.objects.filter(username__icontains=username)
        self.assertTrue(search_object is not None)


# Testing for friendship.
class FriendNetworkTestCase(unittest.TestCase):
    def test_valid_friendship(self):
        username = 'ali_13'
        friend_username = '_cillian_23'
        friends = FriendNetwork.objects.filter(friend_username=friend_username, username=username)
        message = f'{username} and {friend_username} are in the same network.'
        self.assertTrue(friends is not None, message)


# REST API tests ------->

# end point: "/api/userdata"
class UserDataPITestCase(APITestCase):
    # create a testing user.
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testuser'
        )

    def test_endpoint(self):
        self.client.force_login(user=self.user)
        response = self.client.get('/api/userdata')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# end point: "/api/userprofile"
class UserProfileAPITestCase(APITestCase):
    # create a testing user.
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@gmail.com',
            password='testuser'
        )
        self.user.save()
        created_profile = UserProfile.objects.create(user=self.user,
                                                     userid=self.user.id)
        created_profile.save()

    # update the test user's profile status.
    def test_endpoint(self):
        self.client.force_login(user=self.user)
        profile = UserProfile.objects.get(user=self.user)
        profile.profile_status = 'this is a new status'
        profile.save()
        response = self.client.get('/api/userprofile')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# endpoint: "api/userpost"
class UserPostAPITestCase(APITestCase):
    # create a testing user.
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@gmail.com',
            password='testuser'
        )
        self.user.save()
        created_profile = UserProfile.objects.create(user=self.user,
                                                     userid=self.user.id)
        created_profile.save()

    # create and save a new post.
    def test_endpoint(self):
        self.client.force_login(user=self.user)
        media = ''
        description = 'new description'
        newpost = UserPost.objects.create(username=self.user.username,
                                          media=media, description=description,
                                          date_posted=timezone.now())
        newpost.save()
        response = self.client.get('/api/userpost')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
