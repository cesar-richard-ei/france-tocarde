import pytest
from django.urls import reverse
from rest_framework import status
from django.utils import timezone
from decimal import Decimal
import datetime
from ft.user.models import User
from ft.event.models import Event, CarpoolTrip, CarpoolRequest, CarpoolPayment


@pytest.mark.django_db
class TestCarpoolRequestViewSet:
    """Tests pour le CarpoolRequestViewSet."""

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
            seats_total=3,  # Utiliser seats_total au lieu de seats_available
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
    def accepted_request(self, passenger, trip):
        """Fixture pour créer une demande acceptée."""
        return CarpoolRequest.objects.create(
            passenger=passenger,
            trip=trip,
            status="ACCEPTED",
            seats_requested=1,
            message="Je voudrais réserver 1 place.",
        )

    def test_list_carpool_requests_as_anonymous_fails(self, api_client):
        """Test qu'un utilisateur anonyme ne peut pas lister les demandes."""
        url = reverse("carpool-request-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_carpool_requests_as_passenger(
        self, api_client, passenger, pending_request
    ):
        """Test qu'un passager peut voir ses demandes."""
        api_client.force_authenticate(user=passenger)

        url = reverse("carpool-request-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == pending_request.id

    def test_list_carpool_requests_as_driver(self, api_client, driver, pending_request):
        """Test qu'un conducteur peut voir les demandes pour ses trajets."""
        api_client.force_authenticate(user=driver)

        url = reverse("carpool-request-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == pending_request.id

    def test_create_carpool_request(self, api_client, passenger, trip):
        """Test de création d'une demande de covoiturage."""
        api_client.force_authenticate(user=passenger)

        url = reverse("carpool-request-list")
        data = {
            "trip_id": trip.id,
            "seats_requested": 2,
            "message": "Je voudrais réserver 2 places.",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["seats_requested"] == 2
        assert response.data["message"] == "Je voudrais réserver 2 places."
        assert response.data["status"] == "PENDING"

    def test_retrieve_own_request(self, api_client, passenger, pending_request):
        """Test qu'un passager peut voir sa propre demande."""
        api_client.force_authenticate(user=passenger)

        url = reverse("carpool-request-detail", kwargs={"pk": pending_request.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == pending_request.id

    def test_accept_request(self, api_client, driver, pending_request):
        """Test qu'un conducteur peut accepter une demande."""
        api_client.force_authenticate(user=driver)

        url = reverse(
            "carpool-request-request-action", kwargs={"pk": pending_request.id}
        )
        data = {"action": "accept", "response_message": "Bienvenue à bord!"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "ACCEPTED"
        assert response.data["response_message"] == "Bienvenue à bord!"

    def test_reject_request(self, api_client, driver, pending_request):
        """Test qu'un conducteur peut refuser une demande."""
        api_client.force_authenticate(user=driver)

        url = reverse(
            "carpool-request-request-action", kwargs={"pk": pending_request.id}
        )
        data = {
            "action": "reject",
            "response_message": "Désolé, je n'ai plus de place.",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "REJECTED"
        assert response.data["response_message"] == "Désolé, je n'ai plus de place."

    def test_cancel_request(self, api_client, passenger, pending_request):
        """Test qu'un passager peut annuler sa demande."""
        api_client.force_authenticate(user=passenger)

        url = reverse(
            "carpool-request-request-action", kwargs={"pk": pending_request.id}
        )
        data = {"action": "cancel"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "CANCELLED"

    def test_register_payment(self, api_client, driver, accepted_request):
        """Test qu'un conducteur peut enregistrer un paiement."""
        api_client.force_authenticate(user=driver)

        url = reverse("carpool-request-payment", kwargs={"pk": accepted_request.id})
        data = {
            # CarpoolRequestViewSet ajoute automatiquement request_id
            "amount": "15.00",
            "is_completed": True,
            "payment_method": "CASH",
            "notes": "Paiement reçu en main propre",
        }

        response = api_client.post(url, data, format="json")

        # Afficher les erreurs en cas d'échec
        if response.status_code != status.HTTP_200_OK:
            print(f"Erreur: {response.status_code}")
            print(f"Réponse: {response.data}")

        assert response.status_code == status.HTTP_200_OK

        # Vérifier que le paiement a bien été enregistré
        payments = CarpoolPayment.objects.filter(request=accepted_request)
        assert payments.count() == 1
        assert payments.first().amount == Decimal("15.00")
        assert payments.first().is_completed is True
        assert payments.first().payment_method == "CASH"

    def test_passenger_cannot_register_payment(
        self, api_client, passenger, accepted_request
    ):
        """Test qu'un passager ne peut pas enregistrer de paiement."""
        api_client.force_authenticate(user=passenger)

        url = reverse("carpool-request-payment", kwargs={"pk": accepted_request.id})
        data = {"amount": "15.00", "is_completed": True, "payment_method": "CASH"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
