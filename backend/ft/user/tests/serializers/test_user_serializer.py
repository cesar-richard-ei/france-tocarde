import pytest
from ft.user.models import User
from ft.user.serializers import UserSerializer


@pytest.mark.django_db
class TestUserSerializer:
    """Tests pour le UserSerializer."""

    def test_user_serialization(self):
        """Test de la sérialisation d'un utilisateur."""
        user = User.objects.create_user(
            username="testuser1",
            email="test1@example.com",
            password="password123",
            first_name="Jean",
            last_name="Dupont",
            has_car=True,
            car_seats=4,
            can_host_peoples=True,
            home_available_beds=2,
        )

        serializer = UserSerializer(user)
        data = serializer.data

        assert data["first_name"] == "Jean"
        assert data["last_name"] == "Dupont"
        assert data["email"] == "test1@example.com"
        assert data["has_car"] is True
        assert data["car_seats"] == 4
        assert data["can_host_peoples"] is True
        assert data["home_available_beds"] == 2

    @pytest.mark.parametrize(
        "field_name,field_value",
        [
            ("address", "123 Rue du Test"),
            ("city", "Paris"),
            ("zip_code", "75001"),
            ("country", "France"),
            ("phone_number", "0123456789"),
            ("faluche_nickname", "Jeannot"),
            ("home_rules", "Pas de bruit après 22h"),
        ],
    )
    def test_user_optional_fields(self, field_name, field_value):
        """Test des champs optionnels de l'utilisateur."""
        user_data = {
            "username": "testuser2",
            "email": "test2@example.com",
            "password": "password123",
        }
        user_data[field_name] = field_value

        user = User.objects.create_user(**user_data)

        serializer = UserSerializer(user)
        assert serializer.data[field_name] == field_value

    def test_user_update(self):
        """Test de la mise à jour d'un utilisateur."""
        # Créer un utilisateur
        user = User.objects.create_user(
            username="testuser3",
            email="test3@example.com",
            password="password123",
            first_name="Jean",
            last_name="Dupont",
        )

        # Données pour la mise à jour
        updated_data = {
            "first_name": "Pierre",
            "last_name": "Martin",
            "has_car": True,
            "car_seats": 5,
        }

        serializer = UserSerializer(user, data=updated_data, partial=True)
        assert serializer.is_valid()

        updated_user = serializer.save()
        assert updated_user.first_name == "Pierre"
        assert updated_user.last_name == "Martin"
        assert updated_user.has_car is True
        assert updated_user.car_seats == 5

        # Vérifier que l'email n'a pas changé
        assert updated_user.email == "test3@example.com"
