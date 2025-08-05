import pytest
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
import datetime
from ft.event.models import Event


@pytest.mark.django_db
class TestEventViewSet:
    """Tests pour le EventViewSet."""

    def test_list_events(self, api_client):
        """Test de listage des événements."""
        # Créer quelques événements
        start_date = timezone.now() + datetime.timedelta(days=30)
        end_date = timezone.now() + datetime.timedelta(days=32)

        for i in range(3):
            Event.objects.create(
                name=f"Test Event {i}",
                description=f"Description de l'événement test {i}",
                location="Paris",
                start_date=start_date,
                end_date=end_date,
                type="CONGRESS",
            )

        url = reverse("event-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # L'API retourne des données paginées
        assert len(response.data["results"]) == 3

    def test_retrieve_event(self, api_client):
        """Test de récupération d'un événement spécifique."""
        start_date = timezone.now() + datetime.timedelta(days=30)
        end_date = timezone.now() + datetime.timedelta(days=32)

        event = Event.objects.create(
            name="Test Event",
            description="Description de l'événement test",
            location="Paris",
            start_date=start_date,
            end_date=end_date,
            type="CONGRESS",
        )

        url = reverse("event-detail", kwargs={"pk": event.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Test Event"

    def test_create_event_as_anonymous_fails(self, api_client):
        """Test qu'un utilisateur anonyme ne peut pas créer d'événement."""
        url = reverse("event-list")
        event_data = {
            "name": "New Event",
            "description": "Event description",
            "location": "Paris",
            "start_date": "2023-12-01T10:00:00Z",
            "end_date": "2023-12-03T18:00:00Z",
            "type": "CONGRESS",
        }

        response = api_client.post(url, event_data, format="json")

        # L'API refuse l'accès mais avec un HTTP 403 au lieu de 401
        assert response.status_code == status.HTTP_403_FORBIDDEN
