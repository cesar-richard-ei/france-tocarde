import pytest
from django.utils import timezone
import datetime
from ft.event.models import Event


@pytest.mark.django_db
class TestEventModel:
    """Tests pour le modèle Event."""

    def test_create_event(self):
        """Test de la création d'un événement."""
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

        assert event.id is not None
        assert event.name == "Test Event"
        assert event.location == "Paris"
        assert event.start_date is not None
        assert event.end_date is not None
        assert event.is_active is True
        assert event.type == "CONGRESS"

    def test_event_str_representation(self):
        """Test de la représentation string du modèle Event."""
        event = Event.objects.create(
            name="Congrès National",
            location="Paris",
            start_date=timezone.now() + datetime.timedelta(days=30),
            end_date=timezone.now() + datetime.timedelta(days=32),
            type="CONGRESS",
        )
        assert str(event) == "Congrès National (Paris)"

    @pytest.mark.parametrize(
        "event_type",
        ["CONGRESS", "DRINK", "OFFICE", "OTHER"],
    )
    def test_valid_event_types(self, event_type):
        """Test des types d'événement valides."""
        event = Event.objects.create(
            name="Test Event",
            location="Paris",
            start_date=timezone.now() + datetime.timedelta(days=30),
            end_date=timezone.now() + datetime.timedelta(days=32),
            type=event_type,
        )

        assert event.type == event_type

    def test_past_event(self):
        """Test d'un événement passé."""
        start_date = timezone.now() - datetime.timedelta(days=32)
        end_date = timezone.now() - datetime.timedelta(days=30)

        event = Event.objects.create(
            name="Past Event",
            description="Événement passé",
            location="Paris",
            start_date=start_date,
            end_date=end_date,
            type="CONGRESS",
        )

        now = timezone.now()
        assert event.start_date < now
        assert event.end_date < now
