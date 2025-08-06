import pytest
from django.utils import timezone
import datetime
from ft.user.models import User
from ft.event.models import Event, EventHosting
from ft.event.serializers import EventHostingSerializer


@pytest.mark.django_db
class TestEventHostingSerializer:
    """Tests pour le EventHostingSerializer."""

    @pytest.fixture
    def event(self):
        """Fixture pour créer un événement."""
        return Event.objects.create(
            name="Test Event",
            description="Test Event Description",
            location="Test Location",
            start_date=timezone.now() + datetime.timedelta(days=10),
            end_date=timezone.now() + datetime.timedelta(days=12),
            type="CONGRESS",
        )

    @pytest.fixture
    def host(self):
        """Fixture pour créer un hôte."""
        return User.objects.create_user(
            username="host",
            email="host@example.com",
            password="password123",
            home_available_beds=3,
            home_rules="No smoking",
        )

    @pytest.fixture
    def hosting(self, event, host):
        """Fixture pour créer une offre d'hébergement."""
        return EventHosting.objects.create(
            event=event,
            host=host,
            available_beds=2,
            custom_rules="No pets",
            address_override="123 Test St",
            city_override="Test City",
            zip_code_override="12345",
            country_override="Test Country",
        )

    @pytest.fixture
    def request_context(self, host):
        """Fixture pour simuler le contexte de la requête."""

        class MockRequest:
            def __init__(self, user):
                self.user = user

        return {"request": MockRequest(host)}

    def test_serialize_hosting(self, hosting):
        """Test de la sérialisation d'une offre d'hébergement."""
        serializer = EventHostingSerializer(hosting)
        data = serializer.data

        assert data["id"] == hosting.id
        assert data["event"] == hosting.event.id
        assert "host" in data
        assert data["available_beds"] == hosting.available_beds
        assert data["custom_rules"] == hosting.custom_rules
        assert data["address_override"] == hosting.address_override
        assert data["city_override"] == hosting.city_override
        assert data["zip_code_override"] == hosting.zip_code_override
        assert data["country_override"] == hosting.country_override
        assert data["is_active"] == hosting.is_active

    def test_deserialize_valid_hosting(self, event, host, request_context):
        """Test de la désérialisation d'une offre d'hébergement valide."""
        data = {
            "event": event.id,
            "available_beds": 2,
            "custom_rules": "No pets",
            "address_override": "123 Test St",
            "city_override": "Test City",
            "zip_code_override": "12345",
            "country_override": "Test Country",
            "is_active": True,
        }

        serializer = EventHostingSerializer(data=data, context=request_context)
        assert serializer.is_valid(), serializer.errors

        hosting = serializer.save(host=host)
        assert hosting.id is not None
        assert hosting.event == event
        assert hosting.host == host
        assert hosting.available_beds == 2
        assert hosting.custom_rules == "No pets"

    def test_create_with_default_values(self, event, host, request_context):
        """Test de la création avec des valeurs par défaut."""
        # Définir des valeurs par défaut dans le profil de l'utilisateur
        host.home_available_beds = 5
        host.home_rules = "Default rules"
        host.save()

        # Le champ available_beds est obligatoire dans le serializer
        data = {
            "event": event.id,
            "available_beds": 5,  # Ce champ est obligatoire
            "is_active": True,
        }

        serializer = EventHostingSerializer(data=data, context=request_context)
        assert serializer.is_valid(), serializer.errors

        hosting = serializer.save(host=host)
        assert hosting.id is not None
        assert hosting.available_beds == 5
        assert hosting.custom_rules == "Default rules"

    def test_update_hosting(self, hosting):
        """Test de la mise à jour d'une offre d'hébergement."""
        data = {
            "available_beds": 4,
            "custom_rules": "Updated rules",
            "is_active": False,
        }

        serializer = EventHostingSerializer(hosting, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors

        updated_hosting = serializer.save()
        assert updated_hosting.id == hosting.id
        assert updated_hosting.available_beds == 4
        assert updated_hosting.custom_rules == "Updated rules"
        assert updated_hosting.is_active is False

        # Vérifier que les autres champs n'ont pas été modifiés
        assert updated_hosting.event == hosting.event
        assert updated_hosting.host == hosting.host
