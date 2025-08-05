import pytest
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
import datetime
from ft.event.models import Event, EventSubscription
from ft.user.models import User


@pytest.mark.django_db
class TestEventSubscriptionViewSet:
    """Tests pour le EventSubscriptionViewSet."""

    def test_list_subscriptions_anonymous_fails(self, api_client):
        """Test qu'un anonyme ne peut pas accéder aux inscriptions."""
        url = reverse("event-subscription-list")
        response = api_client.get(url)

        # L'API refuse l'accès avec HTTP 403 au lieu de 401
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_subscriptions_as_user(self, api_client, user):
        """Test qu'un utilisateur peut lister les inscriptions."""
        api_client.force_authenticate(user=user)

        # Créer des inscriptions pour l'utilisateur
        event1 = Event.objects.create(
            name="Event 1",
            location="Paris",
            start_date=timezone.now() + datetime.timedelta(days=30),
            end_date=timezone.now() + datetime.timedelta(days=32),
            type="CONGRESS",
        )

        event2 = Event.objects.create(
            name="Event 2",
            location="Lyon",
            start_date=timezone.now() + datetime.timedelta(days=60),
            end_date=timezone.now() + datetime.timedelta(days=62),
            type="DRINK",
        )

        EventSubscription.objects.create(user=user, event=event1, answer="YES")
        EventSubscription.objects.create(user=user, event=event2, answer="YES")

        # Créer une inscription pour un autre utilisateur
        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="password"
        )

        EventSubscription.objects.create(user=other_user, event=event1, answer="YES")

        url = reverse("event-subscription-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # L'API retourne des données paginées
        results = response.data.get("results", [])
        user_subscriptions = [s for s in results if s["user"] == user.id]
        assert len(user_subscriptions) == 2

    def test_retrieve_own_subscription(self, api_client, user):
        """Test qu'un utilisateur peut voir sa propre inscription."""
        api_client.force_authenticate(user=user)

        event = Event.objects.create(
            name="Test Event",
            location="Paris",
            start_date=timezone.now() + datetime.timedelta(days=30),
            end_date=timezone.now() + datetime.timedelta(days=32),
            type="CONGRESS",
        )

        subscription = EventSubscription.objects.create(
            user=user, event=event, answer="YES"
        )

        url = reverse("event-subscription-detail", kwargs={"pk": subscription.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == subscription.id
        assert response.data["user"] == user.id
        assert response.data["event"] == event.id
