import pytest
from django.urls import reverse
from rest_framework import status
from django.utils import timezone
import datetime
from ft.user.models import User
from ft.event.models import Event, EventSubscription


@pytest.mark.django_db
class TestEventViewSetExtended:
    """Tests étendus pour EventViewSet."""

    @pytest.fixture
    def event(self):
        """Fixture pour créer un événement actif."""
        return Event.objects.create(
            name="Test Event",
            description="Test Event Description",
            location="Test Location",
            start_date=timezone.now() + datetime.timedelta(days=10),
            end_date=timezone.now() + datetime.timedelta(days=12),
            is_active=True,
            type="CONGRESS",
        )

    @pytest.fixture
    def inactive_event(self):
        """Fixture pour créer un événement inactif."""
        return Event.objects.create(
            name="Inactive Event",
            description="Inactive Event Description",
            location="Test Location",
            start_date=timezone.now() + datetime.timedelta(days=10),
            end_date=timezone.now() + datetime.timedelta(days=12),
            is_active=False,
            type="CONGRESS",
        )

    @pytest.fixture
    def user(self):
        """Fixture pour créer un utilisateur."""
        return User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword"
        )

    def test_get_queryset_filters_inactive_events(
        self, api_client, event, inactive_event
    ):
        """Test que get_queryset ne retourne que les événements actifs."""
        url = reverse("event-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["name"] == "Test Event"

    def test_get_serializer_class_default(self, api_client, event):
        """Test que get_serializer_class retourne EventSerializer par défaut."""
        url = reverse("event-detail", kwargs={"pk": event.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Vérifier que tous les champs de EventSerializer sont présents
        assert "id" in response.data
        assert "name" in response.data
        assert "description" in response.data
        assert "location" in response.data
        assert "start_date" in response.data
        assert "end_date" in response.data
        assert "type" in response.data

    def test_subscribe_action_creates_subscription(self, api_client, user, event):
        """Test que l'action subscribe crée une inscription."""
        api_client.force_authenticate(user=user)

        url = reverse("event-subscribe", kwargs={"pk": event.id})
        data = {"answer": "YES", "can_invite": True}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["event"] == event.id
        assert response.data["user"] == user.id
        assert response.data["answer"] == "YES"
        assert response.data["can_invite"] is True
        assert response.data["is_active"] is True

        # Vérifier que l'inscription a été créée en base
        subscription = EventSubscription.objects.get(event=event, user=user)
        assert subscription.answer == "YES"
        assert subscription.can_invite is True

    def test_subscribe_action_updates_existing_subscription(
        self, api_client, user, event
    ):
        """Test que l'action subscribe met à jour une inscription existante."""
        # Créer une inscription existante
        existing = EventSubscription.objects.create(
            event=event, user=user, answer="MAYBE", can_invite=False, is_active=True
        )

        api_client.force_authenticate(user=user)

        url = reverse("event-subscribe", kwargs={"pk": event.id})
        data = {"answer": "NO", "can_invite": True}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["answer"] == "NO"
        assert response.data["can_invite"] is True

        # Vérifier que l'inscription a été mise à jour en base
        existing.refresh_from_db()
        assert existing.answer == "NO"
        assert existing.can_invite is True

    def test_subscribe_action_uses_default_values(self, api_client, user, event):
        """Test que l'action subscribe utilise les valeurs par défaut quand non fournies."""
        api_client.force_authenticate(user=user)

        url = reverse("event-subscribe", kwargs={"pk": event.id})
        data = {}  # Aucune donnée fournie

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["answer"] == "YES"  # Valeur par défaut
        assert response.data["can_invite"] is True  # Valeur par défaut
