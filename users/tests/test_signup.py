from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class SignupEndpointTests(APITestCase):
    
    def test_signup_create_successfully(self):
        payload = {
            "username": "newuser",
            "password": "strongpass123",
            "first_name": "New",
            "last_name": "User",
            "email": "newuser@example.com",
        }

        response = self.client.post(reverse("user-signup"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], payload["username"])
        self.assertEqual(response.data["email"], payload["email"])
        self.assertNotIn("password", response.data)

        created_user = User.objects.get(username=payload["username"])
        self.assertTrue(created_user.check_password(payload["password"]))

    def test_signup_fails_when_required_information_is_missing(self):
        payload = {
            "first_name": "Missing",
            "email": "missing@example.com",
        }

        response = self.client.post(reverse("user-signup"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
        self.assertIn("password", response.data)
        self.assertFalse(User.objects.filter(email=payload["email"]).exists())

# ---------------------------------------------------------------------------------
# Exercise 1 — Signup must require first_name and last_name
# ---------------------------------------------------------------------------------

    def test_signup_fails_without_first_name_and_last_name_returns_400(self):
        
        payload = {
            "username": "newuser",
            "password": "strongpass123",
            "email": "newuser@example.com",
        }
        
        response = self.client.post(reverse("user-signup"), payload, format = "json")
    
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("first_name", response.data)
        self.assertIn("last_name", response.data)
        
    def test_signup_with_valid_payload_returns_201(self):
        
        payload = {
            "username": "newuser",
            "password": "strongpass123", 
            "first_name": "New",
            "last_name": "User",
            "email": "newuser@example.com",
        }
        
        response = self.client.post(reverse("user-signup"), payload, format = "json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("first_name", response.data)
        self.assertIn("last_name", response.data)
        self.assertEqual(response.data["first_name"], payload["first_name"])
        self.assertEqual(response.data["last_name"], payload["last_name"])
        
        created_user = User.objects.get(username = payload["username"])
        self.assertTrue(created_user.check_password(payload["password"]))
        self.assertEqual(created_user.first_name, payload["first_name"])
        self.assertEqual(created_user.last_name, payload["last_name"])
        self.assertEqual(created_user.email, payload["email"])