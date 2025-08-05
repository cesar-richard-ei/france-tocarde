import pytest
from django.db import IntegrityError
from django.utils import timezone
import datetime
from ft.event.models import Event, EventSubscription
from ft.user.models import User


@pytest.mark.django_db
class TestEventSubscriptionModel:
    """Tests pour le modèle EventSubscription."""

    def test_create_event_subscription(self):
        """Test de la création d'une inscription à un événement."""
        # Créer un utilisateur et un événement
        user = User.objects.create_user(
            username="testuser1",
            email="test1@example.com",
            password="password123",
        )

        event = Event.objects.create(
            name="Test Event",
            description="Description de l'événement test",
            location="Paris",
            start_date=timezone.now() + datetime.timedelta(days=30),
            end_date=timezone.now() + datetime.timedelta(days=32),
            type="CONGRESS",
        )

        # Créer une inscription
        subscription = EventSubscription.objects.create(
            event=event, user=user, answer="YES", can_invite=True, is_active=True
        )

        assert subscription.id is not None
        assert subscription.user == user
        assert subscription.event == event
        assert subscription.answer == "YES"
        assert subscription.can_invite is True
        assert subscription.is_active is True

    def test_subscription_str_representation(self):
        """Test de la représentation string du modèle EventSubscription."""
        user = User.objects.create_user(
            username="testuser2", email="test2@example.com", password="password123"
        )

        event = Event.objects.create(
            name="Congrès National",
            location="Paris",
            start_date=timezone.now() + datetime.timedelta(days=30),
            end_date=timezone.now() + datetime.timedelta(days=32),
            type="CONGRESS",
        )

        subscription = EventSubscription.objects.create(
            event=event, user=user, answer="YES"
        )

        expected = f"Congrès National ({user.email})"
        assert str(subscription) == expected

    def test_unique_together_constraint(self):
        """Test de la contrainte d'unicité user-event."""
        user = User.objects.create_user(
            username="testuser3", email="test3@example.com", password="password123"
        )

        event = Event.objects.create(
            name="Test Event",
            location="Paris",
            start_date=timezone.now() + datetime.timedelta(days=30),
            end_date=timezone.now() + datetime.timedelta(days=32),
            type="CONGRESS",
        )

        EventSubscription.objects.create(event=event, user=user, answer="YES")

        # Tentative de créer une deuxième inscription pour le même user et événement
        with pytest.raises(IntegrityError):
            EventSubscription.objects.create(event=event, user=user, answer="NO")

    @pytest.mark.parametrize("answer", ["YES", "NO", "MAYBE"])
    def test_subscription_valid_answers(self, answer):
        """Test des réponses valides pour une inscription."""
        user = User.objects.create_user(
            username="testuser4", email="test4@example.com", password="password123"
        )

        event = Event.objects.create(
            name="Test Event",
            location="Paris",
            start_date=timezone.now() + datetime.timedelta(days=30),
            end_date=timezone.now() + datetime.timedelta(days=32),
            type="CONGRESS",
        )

        subscription = EventSubscription.objects.create(
            event=event, user=user, answer=answer
        )

        assert subscription.answer == answer
