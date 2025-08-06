import pytest
from django.utils import timezone
import datetime
from decimal import Decimal
from ft.user.models import User
from ft.event.models import CarpoolRequest, CarpoolTrip, CarpoolPayment, Event


@pytest.mark.django_db
class TestCarpoolPaymentModel:
    """Tests pour le modèle CarpoolPayment."""

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
            status="ACCEPTED",  # Acceptée pour permettre les paiements
            seats_requested=2,
            message="Je voudrais réserver 2 places.",
        )

    def test_create_carpool_payment(self, carpool_request):
        """Test de la création d'un paiement de covoiturage."""
        payment = CarpoolPayment.objects.create(
            request=carpool_request,
            amount=Decimal("30.00"),
            is_completed=True,
            payment_method="CASH",
            notes="Paiement en espèces",
        )

        assert payment.id is not None
        assert payment.request == carpool_request
        assert payment.amount == Decimal("30.00")
        assert payment.is_completed is True
        assert payment.payment_method == "CASH"
        assert payment.notes == "Paiement en espèces"

    def test_carpool_payment_str_representation(self, carpool_request):
        """Test de la représentation string d'un paiement de covoiturage."""
        payment = CarpoolPayment.objects.create(
            request=carpool_request, amount=Decimal("30.00"), payment_method="CASH"
        )

        expected = f"Paiement de 30.00€ pour {carpool_request}"
        assert str(payment) == expected

    @pytest.mark.parametrize(
        "is_completed,expected_status", [(True, "Complet"), (False, "Partiel")]
    )
    def test_payment_status_display(
        self, carpool_request, is_completed, expected_status
    ):
        """Test de la méthode get_payment_status_display."""
        payment = CarpoolPayment.objects.create(
            request=carpool_request,
            amount=Decimal("15.00"),
            is_completed=is_completed,
            payment_method="CASH",
        )

        assert payment.get_payment_status_display == expected_status

    @pytest.mark.parametrize(
        "method,expected_display",
        [
            ("CASH", "Espèces"),
            ("TRANSFER", "Virement bancaire"),
            ("MOBILE", "Paiement mobile"),
            ("OTHER", "Autre"),
        ],
    )
    def test_payment_method_choices(self, carpool_request, method, expected_display):
        """Test des différentes méthodes de paiement."""
        payment = CarpoolPayment.objects.create(
            request=carpool_request, amount=Decimal("15.00"), payment_method=method
        )

        assert payment.get_payment_method_display() == expected_display
