import pytest
from django.utils import timezone
import datetime
from ft.event.models import Event, EventSubscription
from ft.user.models import User
from ft.event.serializers import EventSerializer


@pytest.mark.django_db
class TestEventSerializer:
    """Tests pour le EventSerializer."""

    def test_event_serialization(self):
        """Test de la sérialisation d'un événement."""
        event = Event.objects.create(
            name="Congrès National",
            description="Grand congrès annuel",
            location="Paris",
            start_date=timezone.now() + datetime.timedelta(days=30),
            end_date=timezone.now() + datetime.timedelta(days=32),
            is_public=True,
            at_compiegne=False,
            type="CONGRESS",
            prices="Standard: 15€",
        )

        serializer = EventSerializer(event)
        data = serializer.data

        assert data["name"] == "Congrès National"
        assert data["description"] == "Grand congrès annuel"
        assert data["location"] == "Paris"
        assert data["is_public"] is True
        assert data["at_compiegne"] is False
        assert data["type"] == "CONGRESS"
        assert data["prices"] == "Standard: 15€"
        assert "subscriptions_count" in data
        assert "first_subscribers" in data

    def test_subscriptions_count_calculation(self):
        """Test du calcul du nombre d'inscriptions."""
        event = Event.objects.create(
            name="Test Event",
            location="Paris",
            start_date=timezone.now() + datetime.timedelta(days=30),
            end_date=timezone.now() + datetime.timedelta(days=32),
            type="CONGRESS",
        )

        # Créer 3 inscriptions YES
        user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="pass"
        )
        user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="pass"
        )
        user3 = User.objects.create_user(
            username="user3", email="user3@example.com", password="pass"
        )

        EventSubscription.objects.create(event=event, user=user1, answer="YES")
        EventSubscription.objects.create(event=event, user=user2, answer="YES")
        EventSubscription.objects.create(event=event, user=user3, answer="YES")

        # Créer 2 inscriptions NO
        user4 = User.objects.create_user(
            username="user4", email="user4@example.com", password="pass"
        )
        user5 = User.objects.create_user(
            username="user5", email="user5@example.com", password="pass"
        )

        EventSubscription.objects.create(event=event, user=user4, answer="NO")
        EventSubscription.objects.create(event=event, user=user5, answer="NO")

        # Créer 1 inscription MAYBE
        user6 = User.objects.create_user(
            username="user6", email="user6@example.com", password="pass"
        )
        EventSubscription.objects.create(event=event, user=user6, answer="MAYBE")

        serializer = EventSerializer(event)
        counts = serializer.data["subscriptions_count"]

        assert counts["YES"] == 3
        assert counts["NO"] == 2
        assert counts["MAYBE"] == 1

    def test_first_subscribers_calculation(self):
        """Test du calcul des premiers inscrits."""
        event = Event.objects.create(
            name="Test Event",
            location="Paris",
            start_date=timezone.now() + datetime.timedelta(days=30),
            end_date=timezone.now() + datetime.timedelta(days=32),
            type="CONGRESS",
        )

        # Créer 3 inscriptions YES
        user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="pass",
            first_name="Jean",
            last_name="Dupont",
        )
        user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="pass",
            first_name="Marie",
            last_name="Martin",
        )
        user3 = User.objects.create_user(
            username="user3",
            email="user3@example.com",
            password="pass",
            first_name="Pierre",
            last_name="Durand",
        )

        # Créer dans l'ordre pour tester le tri
        EventSubscription.objects.create(event=event, user=user3, answer="YES")
        EventSubscription.objects.create(event=event, user=user2, answer="YES")
        EventSubscription.objects.create(event=event, user=user1, answer="YES")

        serializer = EventSerializer(event)
        subscribers = serializer.data["first_subscribers"]

        # Vérifier que nous avons bien 3 entrées dans first_subscribers
        assert len(subscribers) == 3
