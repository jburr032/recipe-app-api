from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserAPITests(TestCase):
    """ Test the user API (public) """

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_successful(self):
        """ Test creating user with valid payload is successful """
        payload = {
            'email': 'test@londonappdev.com',
            'password': 'testpass',
            'name': 'name',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(
            user.check_password(payload['password'])
        )
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """ Tests if a user already exits using POST """
        payload = {
            'email': 'test@test.com',
            'password': 'password123',
            'name': 'Test name'
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """ Test that the password must be more than 5 characters """
        payload = {
            'email': 'test@test.com',
            'password': '123',
            'name': 'Test name'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload['email']).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """ Test to check that a token is returned for a valid user """
        payload = {
            'email': 'test@test.com',
            'password': 'password123',
            'name': 'Test name'
        }

        create_user(**payload)

        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_create_token_invalid_credentials(self):
        """ Test to check bad request is returned with invalid creds """
        create_user(
            email='test@test.com',
            password='password123'
        )
        payload = {
            'email': 'test@test.com',
            'password': 'password',
            'name': 'Test name'
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_no_user(self):
        """ Test to check no token is returned if no user """
        payload = {
            'email': 'test@test.com',
            'password': 'password123',
            'name': 'Test name'
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_missing_field(self):
        """ Test to check no token is returned with incomplete creds """
        res = self.client.post(
            TOKEN_URL, {'email': 'one@email.com', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """ Tests to check that a user must be authenticated """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITests(TestCase):
    """ Tests API requests that require authentication """

    def setUp(self):
        self.user = create_user(
            email='test_1@test.com',
            password='password123',
            name='name'
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """ TEST RETRIEVING USER PROFILE """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_me_not_allowed(self):
        """ TEST THAT POSTS ARE NOT ALLOWED TO ME_URL """
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """ TEST UPDATE USER PROFILE FOR AUTHENTICATED USER"""
        payload = {'name': 'new name', 'password': 'newpassword123'}
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
