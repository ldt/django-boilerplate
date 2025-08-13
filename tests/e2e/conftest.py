import os
import pytest
import django

# Configure Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.development")
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

@pytest.fixture
def test_user(db):
    """Create a test user for authentication tests"""
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User"
    )
    return user