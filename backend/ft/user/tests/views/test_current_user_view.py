import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.test import force_authenticate
from ft.user.views.CurrentUserView import CurrentUserView


@pytest.mark.django_db
class TestCurrentUserView:
    """Tests pour la vue CurrentUserView."""

    def test_get_current_user_authenticated(self, authenticated_client, user):
        """Test pour obtenir l'utilisateur actuellement authentifié."""
        url = reverse("current-user")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == user.id
        assert response.data["email"] == user.email
        assert response.data["first_name"] == user.first_name
        assert response.data["last_name"] == user.last_name
        # Vérifier que le champ username n'est pas renvoyé dans les données
        assert "username" not in response.data

    def test_get_current_user_unauthenticated(self, api_client):
        """Test pour obtenir l'utilisateur actuel sans authentification."""
        url = reverse("current-user")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.data
        assert "Aucun utilisateur n'est connecté" in response.data["detail"]

    def test_handle_exception_other_exceptions(self, monkeypatch, admin_client):
        """Test que handle_exception gère correctement d'autres exceptions."""

        # Créer une exception personnalisée
        class CustomException(APIException):
            status_code = 500
            default_detail = "Une erreur est survenue"

        # Remplacer la méthode get originale pour lever notre exception
        original_get = CurrentUserView.get

        def mock_get(*args, **kwargs):
            raise CustomException()

        # Appliquer le patch sur la vue pour simuler une erreur 500
        monkeypatch.setattr(CurrentUserView, "get", mock_get)

        # Utiliser admin_client qui est authentifié pour bypasser la vérification d'authentification
        url = reverse("current-user")
        response = admin_client.get(url)

        # Restaurer la méthode originale
        monkeypatch.setattr(CurrentUserView, "get", original_get)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "detail" in response.data
        assert "Une erreur est survenue" in response.data["detail"]
