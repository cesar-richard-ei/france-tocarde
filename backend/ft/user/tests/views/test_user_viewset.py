import pytest
from rest_framework import status
from django.urls import reverse
from ft.user.models import User


@pytest.mark.django_db
class TestUserViewSet:
    """Tests pour le UserViewSet."""

    def test_list_users_as_anonymous(self, api_client):
        """Test qu'un utilisateur anonyme peut lister les utilisateurs."""
        url = reverse("user-list")
        response = api_client.get(url)

        # L'API autorise l'accès aux listes d'utilisateurs pour tous
        assert response.status_code == status.HTTP_200_OK

    def test_list_users_as_user(self, api_client, user):
        """Test qu'un utilisateur authentifié peut lister les utilisateurs."""
        api_client.force_authenticate(user=user)

        # Créer quelques utilisateurs
        User.objects.create_user(
            username="test1", email="test1@example.com", password="password"
        )
        User.objects.create_user(
            username="test2", email="test2@example.com", password="password"
        )

        url = reverse("user-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Vérifier que la liste contient des utilisateurs
        assert len(response.data) >= 3  # au moins l'utilisateur courant + 2 créés

    def test_retrieve_current_user(self, api_client, user):
        """Test qu'un utilisateur peut récupérer ses propres informations."""
        api_client.force_authenticate(user=user)

        url = reverse("current-user")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == user.email
        assert "first_name" in response.data
        assert "last_name" in response.data

    def test_update_user(self, api_client, user):
        """Test qu'un utilisateur peut mettre à jour son profil."""
        api_client.force_authenticate(user=user)

        url = reverse("user-detail", args=[user.id])
        update_data = {"first_name": "Updated", "last_name": "Name"}

        response = api_client.patch(url, update_data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "Updated"
        assert response.data["last_name"] == "Name"

        # Vérifier que les changements sont bien enregistrés
        updated_user = User.objects.get(id=user.id)
        assert updated_user.first_name == "Updated"
        assert updated_user.last_name == "Name"
