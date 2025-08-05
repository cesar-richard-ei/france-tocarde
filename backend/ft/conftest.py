import pytest
from rest_framework.test import APIClient
from ft.user.models import User


@pytest.fixture
def api_client():
    """Fixture qui fournit un client API REST pour tester les endpoints."""
    return APIClient()


@pytest.fixture
def user(db):
    """Fixture qui fournit un utilisateur de test."""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpassword",
        first_name="Test",
        last_name="User",
        phone_number="0123456789",
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """Fixture qui fournit un client API authentifié."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_user(db):
    """Fixture qui fournit un utilisateur administrateur."""
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpassword",
        first_name="Admin",
        last_name="User",
        phone_number="0123456789",
    )


@pytest.fixture
def admin_client(api_client, admin_user):
    """Fixture qui fournit un client API authentifié avec un admin."""
    api_client.force_authenticate(user=admin_user)
    return api_client
