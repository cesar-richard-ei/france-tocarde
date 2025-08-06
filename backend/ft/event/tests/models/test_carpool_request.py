import pytest
from django.db import IntegrityError
from django.utils import timezone
import datetime
from decimal import Decimal
from ft.user.models import User
from ft.event.models import CarpoolRequest, CarpoolTrip, CarpoolPayment, Event


@pytest.mark.django_db
class TestCarpoolRequestModel:
    """Tests pour le modèle CarpoolRequest."""

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
    def driver(self):
        """Fixture pour créer un conducteur."""
        return User.objects.create_user(
            username="driver",
            email="driver@example.com",
            password="password123",
            has_car=True,
            car_seats=5,
        )

    @pytest.fixture
    def passenger(self):
        """Fixture pour créer un passager."""
        return User.objects.create_user(
            username="passenger", email="passenger@example.com", password="password123"
        )

    @pytest.fixture
    def trip(self, event, driver):
        """Fixture pour créer un trajet de covoiturage."""
        return CarpoolTrip.objects.create(
            event=event,
            driver=driver,
            departure_city="Paris",
            arrival_city="Compiègne",
            departure_datetime=timezone.now() + datetime.timedelta(days=9),
            return_datetime=timezone.now() + datetime.timedelta(days=13),
            seats_total=3,
            price_per_seat=Decimal("15.00"),
        )

    @pytest.fixture
    def carpool_request(self, passenger, trip):
        """Fixture pour créer une demande de covoiturage."""
        return CarpoolRequest.objects.create(
            passenger=passenger,
            trip=trip,
            seats_requested=2,
            message="Je voudrais réserver 2 places.",
        )

    def test_create_carpool_request(self, passenger, trip):
        """Test de la création d'une demande de covoiturage."""
        carpool_request = CarpoolRequest.objects.create(
            passenger=passenger,
            trip=trip,
            seats_requested=1,
            message="Bonjour, je voudrais réserver une place.",
        )

        assert carpool_request.id is not None
        assert carpool_request.passenger == passenger
        assert carpool_request.trip == trip
        assert carpool_request.seats_requested == 1
        assert carpool_request.status == "PENDING"
        assert carpool_request.is_active is True
        assert carpool_request.message == "Bonjour, je voudrais réserver une place."

    def test_carpool_request_str_representation(self, carpool_request):
        """Test de la représentation string d'une demande de covoiturage."""
        expected = f"{carpool_request.passenger} → {carpool_request.trip} (En attente)"
        assert str(carpool_request) == expected

    def test_unique_constraint_active_request(self, passenger, trip):
        """Test de la contrainte d'unicité pour les demandes actives."""
        CarpoolRequest.objects.create(
            passenger=passenger, trip=trip, status="PENDING", seats_requested=1
        )

        # Tentative de créer une deuxième demande active pour le même passager et trajet
        with pytest.raises(IntegrityError):
            CarpoolRequest.objects.create(
                passenger=passenger, trip=trip, status="PENDING", seats_requested=1
            )

    def test_multiple_requests_different_status(self, passenger, trip):
        """Test qu'on peut créer plusieurs demandes avec des statuts différents."""
        CarpoolRequest.objects.create(
            passenger=passenger, trip=trip, status="CANCELLED", seats_requested=1
        )

        # On peut créer une demande avec un statut différent
        request2 = CarpoolRequest.objects.create(
            passenger=passenger, trip=trip, status="PENDING", seats_requested=1
        )

        assert request2.id is not None

    def test_is_paid_property_no_payment(self, carpool_request):
        """Test de la propriété is_paid quand il n'y a pas de paiement."""
        assert carpool_request.is_paid is False

    def test_is_paid_property_with_payment(self, carpool_request):
        """Test de la propriété is_paid avec un paiement complet."""
        CarpoolPayment.objects.create(
            request=carpool_request,
            amount=Decimal("30.00"),
            is_completed=True,
            payment_method="CASH",
        )

        # Recharger l'objet pour éviter les problèmes de cache
        carpool_request.refresh_from_db()
        assert carpool_request.is_paid is True

    def test_total_paid_property_no_payment(self, carpool_request):
        """Test de la propriété total_paid sans paiement."""
        assert carpool_request.total_paid == 0

    def test_total_paid_property_with_payments(self, carpool_request):
        """Test de la propriété total_paid avec plusieurs paiements."""
        CarpoolPayment.objects.create(
            request=carpool_request,
            amount=Decimal("10.00"),
            is_completed=True,
            payment_method="CASH",
        )

        CarpoolPayment.objects.create(
            request=carpool_request,
            amount=Decimal("20.00"),
            is_completed=False,  # Paiement non complété, mais doit être comptabilisé
            payment_method="TRANSFER",
        )

        # Recharger l'objet
        carpool_request.refresh_from_db()
        assert carpool_request.total_paid == Decimal("30.00")

    def test_expected_amount_property(self, carpool_request):
        """Test de la propriété expected_amount."""
        # La demande est pour 2 sièges à 15€ par siège
        assert carpool_request.expected_amount == Decimal("30.00")
