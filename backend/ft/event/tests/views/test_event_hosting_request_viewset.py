import pytest
from django.urls import reverse
from rest_framework import status
from django.utils import timezone
import datetime
from ft.user.models import User
from ft.event.models import Event, EventHosting, EventHostingRequest


@pytest.mark.django_db
class TestEventHostingRequestViewSet:
    """Tests pour le EventHostingRequestViewSet."""

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
    def requester(self):
        """Fixture pour créer un demandeur."""
        return User.objects.create_user(
            username="requester", email="requester@example.com", password="password123"
        )

    @pytest.fixture
    def hosting(self, event, host):
        """Fixture pour créer une offre d'hébergement."""
        return EventHosting.objects.create(
            event=event, host=host, available_beds=2, custom_rules="No pets"
        )

    @pytest.fixture
    def pending_request(self, hosting, requester):
        """Fixture pour créer une demande d'hébergement en attente."""
        return EventHostingRequest.objects.create(
            hosting=hosting, requester=requester, message="I would like a place to stay"
        )

    def test_list_requests_as_anonymous_fails(self, api_client):
        """Test qu'un utilisateur anonyme ne peut pas lister les demandes."""
        url = reverse("event-hosting-request-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_requests_as_requester(self, api_client, requester, pending_request):
        """Test qu'un demandeur peut lister ses propres demandes."""
        api_client.force_authenticate(user=requester)

        url = reverse("event-hosting-request-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == pending_request.id

    def test_list_requests_as_host(self, api_client, host, pending_request):
        """Test qu'un hôte peut lister les demandes pour ses hébergements."""
        api_client.force_authenticate(user=host)

        url = reverse("event-hosting-request-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == pending_request.id

    def test_list_requests_filtered_by_status(self, api_client, requester, hosting):
        """Test du filtrage des demandes par statut."""
        api_client.force_authenticate(user=requester)

        # Créer des demandes avec différents statuts
        pending = EventHostingRequest.objects.create(
            hosting=hosting, requester=requester, status="PENDING"
        )
        accepted = EventHostingRequest.objects.create(
            hosting=hosting, requester=requester, status="ACCEPTED"
        )
        rejected = EventHostingRequest.objects.create(
            hosting=hosting, requester=requester, status="REJECTED"
        )

        # Filtrer par statut PENDING
        url = f"{reverse('event-hosting-request-list')}?status=PENDING"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == pending.id

        # Filtrer par statut ACCEPTED
        url = f"{reverse('event-hosting-request-list')}?status=ACCEPTED"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == accepted.id

    def test_retrieve_request_as_requester(
        self, api_client, requester, pending_request
    ):
        """Test qu'un demandeur peut voir sa propre demande."""
        api_client.force_authenticate(user=requester)

        url = reverse("event-hosting-request-detail", kwargs={"pk": pending_request.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == pending_request.id
        assert response.data["requester"]["id"] == requester.id

    def test_retrieve_request_as_host(self, api_client, host, pending_request):
        """Test qu'un hôte peut voir une demande pour son hébergement."""
        api_client.force_authenticate(user=host)

        url = reverse("event-hosting-request-detail", kwargs={"pk": pending_request.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == pending_request.id
        assert response.data["hosting"]["host"]["id"] == host.id

    def test_retrieve_request_as_other_user_fails(self, api_client, pending_request):
        """Test qu'un autre utilisateur ne peut pas voir une demande."""
        other_user = User.objects.create_user(
            username="other", email="other@example.com", password="password123"
        )
        api_client.force_authenticate(user=other_user)

        url = reverse("event-hosting-request-detail", kwargs={"pk": pending_request.id})
        response = api_client.get(url)

        # L'API répond avec 403 Forbidden plutôt que 404 Not Found
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_request(self, api_client, requester, hosting):
        """Test de création d'une demande d'hébergement."""
        api_client.force_authenticate(user=requester)

        url = reverse("event-hosting-request-list")
        data = {
            "hosting_id": hosting.id,
            "message": "Je voudrais un hébergement pour l'événement",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["requester"]["id"] == requester.id
        assert response.data["hosting"]["id"] == hosting.id
        assert response.data["message"] == "Je voudrais un hébergement pour l'événement"
        assert response.data["status"] == "PENDING"

    def test_create_request_for_own_hosting_fails(self, api_client, host, hosting):
        """Test qu'un hôte ne peut pas demander son propre hébergement."""
        api_client.force_authenticate(user=host)

        url = reverse("event-hosting-request-list")
        data = {
            "hosting_id": hosting.id,
            "message": "Je voudrais mon propre hébergement",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "propre hébergement" in str(response.data["hosting_id"][0])

    def test_update_request_message(
        self, api_client, requester, pending_request, hosting
    ):
        """Test de mise à jour du message d'une demande."""
        api_client.force_authenticate(user=requester)

        url = reverse("event-hosting-request-detail", kwargs={"pk": pending_request.id})
        # Il faut inclure hosting_id pour que la mise à jour soit valide
        data = {"message": "Message mis à jour", "hosting_id": hosting.id}

        response = api_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "Message mis à jour"

    def test_accept_request(self, api_client, host, pending_request):
        """Test qu'un hôte peut accepter une demande."""
        api_client.force_authenticate(user=host)

        url = reverse("event-hosting-request-accept", kwargs={"pk": pending_request.id})
        data = {"host_message": "Bienvenue chez moi !"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "ACCEPTED"
        assert response.data["host_message"] == "Bienvenue chez moi !"

    def test_accept_request_as_requester_fails(
        self, api_client, requester, pending_request
    ):
        """Test qu'un demandeur ne peut pas accepter sa propre demande."""
        api_client.force_authenticate(user=requester)

        url = reverse("event-hosting-request-accept", kwargs={"pk": pending_request.id})
        response = api_client.post(url, {}, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_reject_request(self, api_client, host, pending_request):
        """Test qu'un hôte peut refuser une demande."""
        api_client.force_authenticate(user=host)

        url = reverse("event-hosting-request-reject", kwargs={"pk": pending_request.id})
        data = {"host_message": "Désolé, je n'ai plus de place."}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "REJECTED"
        assert response.data["host_message"] == "Désolé, je n'ai plus de place."

    def test_reject_request_as_requester_fails(
        self, api_client, requester, pending_request
    ):
        """Test qu'un demandeur ne peut pas refuser sa propre demande."""
        api_client.force_authenticate(user=requester)

        url = reverse("event-hosting-request-reject", kwargs={"pk": pending_request.id})
        response = api_client.post(url, {}, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_cancel_request(self, api_client, requester, pending_request):
        """Test qu'un demandeur peut annuler sa demande."""
        api_client.force_authenticate(user=requester)

        url = reverse("event-hosting-request-cancel", kwargs={"pk": pending_request.id})
        response = api_client.post(url, {}, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "CANCELLED"

    def test_cancel_request_as_host_fails(self, api_client, host, pending_request):
        """Test qu'un hôte ne peut pas annuler une demande."""
        api_client.force_authenticate(user=host)

        url = reverse("event-hosting-request-cancel", kwargs={"pk": pending_request.id})
        response = api_client.post(url, {}, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_my_requests_action(self, api_client, requester, pending_request):
        """Test de l'action my_requests."""
        api_client.force_authenticate(user=requester)

        url = reverse("event-hosting-request-my-requests")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["id"] == pending_request.id
        assert response.data[0]["requester"]["id"] == requester.id

    def test_for_my_hostings_action(self, api_client, host, pending_request):
        """Test de l'action for_my_hostings."""
        api_client.force_authenticate(user=host)

        url = reverse("event-hosting-request-for-my-hostings")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["id"] == pending_request.id
        assert response.data[0]["hosting"]["host"]["id"] == host.id
