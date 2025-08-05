import pytest
from django.db import IntegrityError
from ft.user.models import User


@pytest.mark.django_db
class TestUserModel:
    """Tests pour le modèle User."""

    def test_create_user(self):
        """Test de la création d'un utilisateur simple."""
        user = User.objects.create_user(
            username="testuser1",
            email="test1@example.com",
            password="password123",
            first_name="John",
            last_name="Doe",
            is_staff=False,  # Assurer explicitement que is_staff est False
        )
        assert user.id is not None
        assert user.email == "test1@example.com"
        assert user.username == "testuser1"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert not user.is_staff
        assert not user.is_superuser

    def test_user_str_representation(self):
        """Test de la représentation string du modèle User."""
        user = User.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="password123",
            first_name="Jean",
            last_name="Dupont",
        )
        assert str(user) == "Jean Dupont"

    def test_email_uniqueness(self):
        """Test que l'email doit être unique."""
        User.objects.create_user(
            username="testuser3", email="duplicate@example.com", password="password123"
        )
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                username="testuser4",
                email="duplicate@example.com",
                password="password123",
            )

    @pytest.mark.parametrize(
        "faluche_status",
        [
            "SYMPATHISANT",
            "IMPETRANT",
            "BAPTISE",
            "OTHER",
        ],
    )
    def test_valid_faluche_status(self, faluche_status):
        """Test des choix valides pour le statut faluche."""
        user = User.objects.create_user(
            username="testuser5", email="test5@example.com", password="password123"
        )
        user.faluche_status = faluche_status
        user.save()
        assert user.faluche_status == faluche_status
