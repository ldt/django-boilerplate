import os
import pytest
import django

# Configure Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.development")
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

@pytest.fixture(scope="session")
def base_url():
    """Provide base URL for E2E tests"""
    return "http://localhost:8001"

@pytest.fixture(scope="session")
def test_user():
    """Provide test user data for authentication tests"""
    # For E2E tests, return user data without creating in DB
    # The actual user will be created via registration API during tests
    return type('TestUser', (), {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123',
        'first_name': 'Test',
        'last_name': 'User'
    })()