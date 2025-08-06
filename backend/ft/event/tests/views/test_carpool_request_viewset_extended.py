import pytest
from django.urls import reverse
from rest_framework import status
from django.utils import timezone
from decimal import Decimal
import datetime
from ft.user.models import User
from ft.event.models import Event, CarpoolTrip, CarpoolRequest, CarpoolPayment


@pytest.mark.django_db
class TestCarpoolRequestViewSetExtended:
    """Tests étendus pour le CarpoolRequestViewSet."""

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
    def another_passenger(self):
        """Fixture pour créer un autre passager."""
        return User.objects.create_user(
            username="another_passenger",
            email="another@example.com",
            password="password123",
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
    def pending_request(self, passenger, trip):
        """Fixture pour créer une demande en attente."""
        return CarpoolRequest.objects.create(
            passenger=passenger,
            trip=trip,
            status="PENDING",
            seats_requested=2,
            message="Je voudrais réserver 2 places.",
        )

    @pytest.fixture
    def accepted_request(self, another_passenger, trip):
        """Fixture pour créer une demande acceptée."""
        return CarpoolRequest.objects.create(
            passenger=another_passenger,
            trip=trip,
            status="ACCEPTED",
            seats_requested=1,
            message="Je voudrais réserver 1 place.",
        )

    def test_list_carpool_requests(
        self, api_client, driver, passenger, pending_request, accepted_request
    ):
        """Test que l'utilisateur voit ses propres demandes de covoiturage."""
        # Test avec le conducteur qui devrait voir toutes les demandes pour ses trajets
        api_client.force_authenticate(user=driver)
        url = reverse("carpool-request-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2  # Devrait voir les deux demandes

        # Test avec le passager qui ne devrait voir que sa demande
        api_client.force_authenticate(user=passenger)
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1  # Ne devrait voir que sa demande
        assert response.data["results"][0]["id"] == pending_request.id

    def test_request_action_accept_with_message(
        self, api_client, driver, pending_request
    ):
        """Test de l'action accept avec un message de réponse."""
        api_client.force_authenticate(user=driver)

        url = reverse(
            "carpool-request-request-action", kwargs={"pk": pending_request.id}
        )
        data = {"action": "accept", "response_message": "Votre demande est acceptée !"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "ACCEPTED"
        assert response.data["response_message"] == "Votre demande est acceptée !"

    def test_request_action_reject_without_message(
        self, api_client, driver, pending_request
    ):
        """Test de l'action reject sans message de réponse."""
        api_client.force_authenticate(user=driver)

        url = reverse(
            "carpool-request-request-action", kwargs={"pk": pending_request.id}
        )
        data = {"action": "reject"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "REJECTED"
        assert response.data["response_message"] is None

    def test_request_action_with_invalid_action(
        self, api_client, driver, pending_request
    ):
        """Test de l'action avec une action invalide."""
        api_client.force_authenticate(user=driver)

        url = reverse(
            "carpool-request-request-action", kwargs={"pk": pending_request.id}
        )
        data = {"action": "invalid_action"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_payment_with_existing_payment(self, api_client, driver, accepted_request):
        """Test de l'ajout d'un paiement quand un paiement existe déjà."""
        api_client.force_authenticate(user=driver)

        # Créer un paiement existant
        CarpoolPayment.objects.create(
            request=accepted_request,
            amount=Decimal("10.00"),
            is_completed=True,
            payment_method="CASH",
        )

        url = reverse("carpool-request-payment", kwargs={"pk": accepted_request.id})
        data = {
            "amount": "15.00",
            "is_completed": True,
            "payment_method": "TRANSFER",
            "notes": "Nouveau paiement",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK

        # Vérifier que le paiement a été mis à jour
        payment = CarpoolPayment.objects.get(request=accepted_request)
        assert payment.amount == Decimal("15.00")
        assert payment.payment_method == "TRANSFER"
        assert payment.notes == "Nouveau paiement"

    def test_payment_non_accepted_request(self, api_client, driver, passenger, trip):
        """Test de l'ajout d'un paiement pour une demande non acceptée."""
        api_client.force_authenticate(user=driver)

        # Créer une demande en attente
        request = CarpoolRequest.objects.create(
            passenger=passenger, trip=trip, status="PENDING", seats_requested=1
        )

        url = reverse("carpool-request-payment", kwargs={"pk": request.id})
        data = {"amount": "15.00", "is_completed": True, "payment_method": "CASH"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Seules les demandes acceptées" in str(response.data["detail"])

    def test_payment_with_invalid_data(self, api_client, driver, accepted_request):
        """Test de l'ajout d'un paiement avec des données invalides."""
        api_client.force_authenticate(user=driver)

        url = reverse("carpool-request-payment", kwargs={"pk": accepted_request.id})
        data = {
            "amount": "invalid",  # Montant invalide
            "is_completed": True,
            "payment_method": "CASH",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "amount" in response.data
