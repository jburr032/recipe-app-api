from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTests(TestCase):
    """ Tests the publically available ingredients end-points """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """ Test that login is requried to access the end-point """
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """ Tests the private ingredients end-points """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('_test_2@test.com', 'mypassword')
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """ Tests retrieving a list of ingredients """

        # Commit ingredients to the DB with the user object
        Ingredient.objects.create(user=self.user, name='kale')
        Ingredient.objects.create(user=self.user, name='carrot')

        # Authenticate the user/make the get call
        res = self.client.get(INGREDIENTS_URL)

        # Validate the return values
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        print('SERIALIZER.DATA', serializer.data)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """ Tests that ingredients for the authenticated user are returned """

        user2 = get_user_model().objects.create_user(
            '_test7@test.com',
            'password'
        )

        Ingredient.objects.create(user=user2, name='Cream')
        user_ingredient = Ingredient.objects.create(
            user=self.user, name='Oats')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], user_ingredient.name)

    def test_create_ingredient_successful(self):
        """ Tests that a user can add an ingredient """
        payload = {'name': 'Almonds'}
        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user, name=payload['name']).exists()
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """ Test that checks an invalid post Ingredient request is rejected """
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
