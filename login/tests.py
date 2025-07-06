from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

class LoginViewsTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.test_username = "testuser"
        self.test_password = "secretpass"
        self.test_email = "test@example.com"

        # Create a user for login tests
        self.user = User.objects.create_user(
            username=self.test_username,
            password=self.test_password,
            email=self.test_email,
            first_name="Test",
            last_name="User"
        )

    def test_login_page_get(self):
        """GET request to login page returns 200"""
        response = self.client.get(reverse("login:login_view"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login/login.html")

    def test_login_valid_credentials(self):
        """POST request with valid credentials redirects to dashboard"""
        response = self.client.post(reverse("login:login_view"), {
            "username": self.test_username,
            "password": self.test_password
        })
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertRedirects(response, reverse("dashboard:home"))

    def test_login_invalid_credentials(self):
        """POST request with wrong password stays on login page"""
        response = self.client.post(reverse("login:login_view"), {
            "username": self.test_username,
            "password": "wrongpass"
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login/login.html")
        self.assertContains(response, "Invalid credentials")

    def test_register_user_success(self):
        """Registering a new user redirects to dashboard"""
        response = self.client.post(reverse("login:register_view"), {
            "username": "newuser",
            "password": "newpassword",
            "repeat_password": "newpassword",
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "User"
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("dashboard:home"))

        # Verify user was created
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_existing_username(self):
        """Trying to register with existing username returns error"""
        response = self.client.post(reverse("login:register_view"), {
            "username": self.test_username,
            "password": "anotherpass",
            "repeat_password": "anotherpass",
            "email": "other@example.com"
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login/register.html")
        self.assertContains(response, "Username already exists")

    def test_register_passwords_dont_match(self):
        """Registration fails if passwords don’t match"""
        response = self.client.post(reverse("login:register_view"), {
            "username": "newuser",
            "password": "pass1",
            "repeat_password": "pass2",
            "email": "new@example.com"
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login/register.html")
        self.assertContains(response, "Passwords do not match")

    def test_logout(self):
        """Logout should return to login page"""
        self.client.login(username=self.test_username, password=self.test_password)
        response = self.client.get(reverse("login:logout_user"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login/login.html")