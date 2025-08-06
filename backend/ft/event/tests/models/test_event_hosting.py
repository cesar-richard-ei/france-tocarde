import pytest
from django.utils import timezone
from ft.user.models import User
from ft.event.models import Event, EventHosting
import datetime


@pytest.mark.django_db
class TestEventHostingModel:
    """Tests pour le modèle EventHosting."""

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

    def test_create_hosting(self, event, host):
        """Test de la création d'une offre d'hébergement."""
        hosting = EventHosting.objects.create(
            event=event, host=host, available_beds=2, custom_rules="No pets"
        )

        assert hosting.id is not None
        assert hosting.event == event
        assert hosting.host == host
        assert hosting.available_beds == 2
        assert hosting.custom_rules == "No pets"
        assert hosting.is_active is True

    def test_hosting_str_representation(self, event, host):
        """Test de la représentation string d'une offre d'hébergement."""
        hosting = EventHosting.objects.create(event=event, host=host, available_beds=2)

        expected = f"Hébergement par {host} pour {event}"
        assert str(hosting) == expected

    def test_save_method_with_defaults(self, event, host):
        """Test de la méthode save avec les valeurs par défaut."""
        # Définir des valeurs par défaut dans le profil de l'utilisateur
        host.home_available_beds = 5
        host.home_rules = "Default rules"
        host.save()

        # Créer un hébergement sans spécifier available_beds ni custom_rules
        hosting = EventHosting.objects.create(event=event, host=host)

        # Vérifier que les valeurs par défaut ont été appliquées
        assert hosting.available_beds == 5
        assert hosting.custom_rules == "Default rules"

    def test_save_method_with_overrides(self, event, host):
        """Test de la méthode save avec des valeurs spécifiées."""
        # Définir des valeurs par défaut dans le profil de l'utilisateur
        host.home_available_beds = 5
        host.home_rules = "Default rules"
        host.save()

        # Créer un hébergement en spécifiant available_beds et custom_rules
        hosting = EventHosting.objects.create(
            event=event, host=host, available_beds=2, custom_rules="Custom rules"
        )

        # Vérifier que les valeurs spécifiées ont été utilisées
        assert hosting.available_beds == 2
        assert hosting.custom_rules == "Custom rules"

    def test_address_overrides(self, event, host):
        """Test des champs d'adresse spécifiques."""
        hosting = EventHosting.objects.create(
            event=event,
            host=host,
            available_beds=2,
            address_override="123 Test St",
            city_override="Test City",
            zip_code_override="12345",
            country_override="Test Country",
        )

        assert hosting.address_override == "123 Test St"
        assert hosting.city_override == "Test City"
        assert hosting.zip_code_override == "12345"
        assert hosting.country_override == "Test Country"

    def test_unique_constraint(self, event, host):
        """Test de la contrainte d'unicité (event, host)."""
        # Créer un premier hébergement
        EventHosting.objects.create(event=event, host=host, available_beds=2)

        # Tenter de créer un second hébergement avec le même event et host
        with pytest.raises(Exception):
            EventHosting.objects.create(event=event, host=host, available_beds=3)
