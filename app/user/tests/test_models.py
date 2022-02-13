from django.test import TestCase
from django.contrib.auth import get_user_model


class UserModelTests(TestCase):

    def test_new_user_email_normalized(self):
        email = 'test@TEST.COM'
        user = get_user_model().objects.create_user(email, 'Test2022')

        self.assertEqual(user.email, email.lower())

    def test_create_user_with_email_successful(self):
        email = 'test@test.com'
        password = 'Test2022'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_invalid_email(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        user = get_user_model().objects.create_superuser(
            'test@test.com',
            'admin123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
