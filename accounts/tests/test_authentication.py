import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .factories import UserFactory

User = get_user_model()


@pytest.mark.django_db
class TestAuthentication:
    def setup_method(self):
        self.client = APIClient()

    def test_user_registration(self):
        """Test user registration through the API"""
        url = "/api/register/"
        data = {
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "password": "testpassword123",
            "password_confirm": "testpassword123",
        }
        response = self.client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED, \
            f"Expected 201 CREATED, got {response.status_code}. Response: {response.data}"
        assert "access" in response.data, "Access token not in response"
        assert "refresh" in response.data, "Refresh token not in response"
        assert User.objects.filter(email="test@example.com").exists(), "User was not created"

    def test_user_login(self):
        """Test user login through the API"""
        # Create a test user
        user = UserFactory(email="test@example.com")
        user.set_password("testpassword123")
        user.save()

        url = "/api/login/"
        data = {"email": "test@example.com", "password": "testpassword123"}
        response = self.client.post(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK, \
            f"Expected 200 OK, got {response.status_code}. Response: {response.data}"
        assert "access" in response.data, "Access token not in response"
        assert "refresh" in response.data, "Refresh token not in response"

    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials through the API"""
        url = "/api/login/"
        data = {"email": "nonexistent@example.com", "password": "wrongpassword"}
        response = self.client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST, \
            f"Expected 400 BAD REQUEST, got {response.status_code}. Response: {response.data}"
        assert "non_field_errors" in response.data, "Error details not in response"

    def test_profile_access_authenticated(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)

        url = reverse("profile")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == user.email

    def test_profile_access_unauthenticated(self):
        url = reverse("profile")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
