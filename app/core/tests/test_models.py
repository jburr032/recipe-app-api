from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


def sample_user(email='_test_11_@test.com', password='password'):
    """ Create a sample user helper """
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an eamil is successfull"""
        email = 'londonappteam@email.com'
        password = 'password123'

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test that new user emails are normalized by being lowercase"""
        email = 'test@TEST.COM'

        user = get_user_model().objects.create_user(email, '123password')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Tests that a new user has passed-in an email address"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, '123password')

    def test_creating_new_superuser(self):
        """Tests that a new superuser is created"""
        email = 'test@test.com'

        user = get_user_model().objects.create_superuser(email, '123password')

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_tag_str(self):
        """ Test the tag string representation """
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )

        # Django allows you to specify what value you want returned
        # when casting to data types - here we are casting the obj
        # 'tag' to string, so we want the 'name' value to be returned
        self.assertEqual(str(tag), tag.name)
