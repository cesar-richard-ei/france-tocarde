import pytest
from django.core.exceptions import ValidationError
from ft.user.models import User
from ft.user.managers import UserManager


@pytest.mark.django_db
class TestUserManager:
    """Tests pour le UserManager."""

    def test_create_user_with_valid_data(self):
        """Test de création d'un utilisateur avec des données valides."""
        user = User.objects.create_user(
            email="test@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
        )

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.is_active is True
        assert user.is_staff is True  # Par défaut dans ce UserManager
        assert user.is_superuser is False
        assert user.check_password("password123") is True

    def test_create_user_without_email_fails(self):
        """Test que la création d'un utilisateur sans email échoue."""
        with pytest.raises(ValueError) as excinfo:
            User.objects.create_user(email="", password="password123")

        assert "Users require an email field" in str(excinfo.value)

    def test_create_user_email_normalization(self):
        """Test de la normalisation de l'email lors de la création d'un utilisateur."""
        user = User.objects.create_user(
            email="TEST@EXAMPLE.COM", password="password123"
        )

        assert user.email == "TEST@example.com"  # Le domaine est en minuscule

    def test_create_user_auto_username(self):
        """Test de la génération automatique du nom d'utilisateur."""
        user = User.objects.create_user(
            email="test.user@example.com", password="password123"
        )

        assert user.username == "testuser"  # Basé sur la partie locale de l'email

    def test_create_user_auto_username_with_conflict(self):
        """Test de la génération du nom d'utilisateur en cas de conflit."""
        # Créer un premier utilisateur
        User.objects.create_user(
            email="test.user@example.com", password="password123", username="testuser"
        )

        # Créer un second utilisateur avec le même email (partie locale)
        user2 = User.objects.create_user(
            email="test.user@other.com", password="password123"
        )

        # Le nom d'utilisateur devrait être incrémenté
        assert user2.username == "testuser1"

    def test_create_superuser(self):
        """Test de création d'un superutilisateur."""
        superuser = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpass",
            first_name="Admin",
            last_name="User",
        )

        assert superuser.id is not None
        assert superuser.email == "admin@example.com"
        assert superuser.is_active is True
        assert superuser.is_staff is True
        assert superuser.is_superuser is True

    def test_create_superuser_with_is_staff_false_fails(self):
        """Test que la création d'un superutilisateur avec is_staff=False échoue."""
        with pytest.raises(ValueError) as excinfo:
            User.objects.create_superuser(
                email="admin@example.com", password="adminpass", is_staff=False
            )

        assert "Superuser must have is_staff=True" in str(excinfo.value)

    def test_create_superuser_with_is_superuser_false_fails(self):
        """Test que la création d'un superutilisateur avec is_superuser=False échoue."""
        with pytest.raises(ValueError) as excinfo:
            User.objects.create_superuser(
                email="admin@example.com", password="adminpass", is_superuser=False
            )

        assert "Superuser must have is_superuser=True" in str(excinfo.value)
