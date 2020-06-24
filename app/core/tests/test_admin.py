from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse


class AdminSiteTests(TestCase):

    def setUp(self):
        self.client = Client()
        email = 'test@test.com'
        password = 'password123'
        self.admin = get_user_model().objects.create_superuser(email, password)
        self.client.force_login(self.admin)

        self.user = get_user_model().objects.create_user(
            'test_1@test.com', 'Test login')

    def test_users_listed(self):
        """ Test to check whether user model is registered """
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
