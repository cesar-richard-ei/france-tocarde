import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestVersionView:
    """Tests pour la vue VersionView."""

    def test_get_version_default(self, api_client, monkeypatch):
        """Test de récupération de la version par défaut."""
        # Supprimer la variable d'environnement VERSION si elle existe
        monkeypatch.delenv("VERSION", raising=False)

        url = reverse("version")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "version" in response.data
        assert response.data["version"] == "development"

    def test_get_version_custom(self, api_client, monkeypatch):
        """Test de récupération de la version personnalisée."""
        # Définir une version personnalisée
        monkeypatch.setenv("VERSION", "1.2.3")

        url = reverse("version")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "version" in response.data
        assert response.data["version"] == "1.2.3"

    def test_version_view_no_auth_required(self, api_client):
        """Test que la vue version est accessible sans authentification."""
        url = reverse("version")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
