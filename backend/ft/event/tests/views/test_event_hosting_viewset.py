import pytest
from django.urls import reverse
from rest_framework import status
from django.utils import timezone
import datetime
from ft.user.models import User
from ft.event.models import Event, EventHosting, EventHostingRequest


@pytest.mark.django_db
class TestEventHostingViewSet:
    """Tests pour le EventHostingViewSet."""

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
    def other_user(self):
        """Fixture pour créer un autre utilisateur."""
        return User.objects.create_user(
            username="other_user", email="other@example.com", password="password123"
        )

    @pytest.fixture
    def hosting(self, event, host):
        """Fixture pour créer une offre d'hébergement."""
        return EventHosting.objects.create(
            event=event, host=host, available_beds=2, custom_rules="No pets"
        )

    @pytest.fixture
    def hosting_request(self, hosting, other_user):
        """Fixture pour créer une demande d'hébergement acceptée."""
        hosting_req = EventHostingRequest.objects.create(
            hosting=hosting, requester=other_user, status="ACCEPTED"
        )
        return hosting_req

    def test_list_hostings_as_anonymous_fails(self, api_client):
        """Test qu'un utilisateur anonyme ne peut pas lister les hébergements."""
        url = reverse("event-hosting-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_hostings_as_authenticated(self, api_client, host, hosting):
        """Test qu'un utilisateur authentifié peut lister les hébergements."""
        api_client.force_authenticate(user=host)

        url = reverse("event-hosting-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == hosting.id

    def test_retrieve_hosting(self, api_client, host, hosting):
        """Test qu'un utilisateur authentifié peut récupérer un hébergement."""
        api_client.force_authenticate(user=host)

        url = reverse("event-hosting-detail", kwargs={"pk": hosting.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == hosting.id
        assert response.data["event"] == hosting.event.id
        assert response.data["host"]["id"] == host.id
        assert response.data["available_beds"] == hosting.available_beds
        assert response.data["custom_rules"] == hosting.custom_rules

    def test_create_hosting(self, api_client, host, event):
        """Test qu'un utilisateur authentifié peut créer un hébergement."""
        api_client.force_authenticate(user=host)

        url = reverse("event-hosting-list")
        data = {
            "event": event.id,
            "available_beds": 3,
            "custom_rules": "No smoking",
            "address_override": "123 Test St",
            "city_override": "Test City",
            "zip_code_override": "12345",
            "country_override": "Test Country",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["host"]["id"] == host.id
        assert response.data["event"] == event.id
        assert response.data["available_beds"] == 3
        assert response.data["custom_rules"] == "No smoking"
        assert response.data["address_override"] == "123 Test St"

    def test_update_own_hosting(self, api_client, host, hosting):
        """Test qu'un utilisateur peut mettre à jour son propre hébergement."""
        api_client.force_authenticate(user=host)

        url = reverse("event-hosting-detail", kwargs={"pk": hosting.id})
        data = {
            "available_beds": 4,
            "custom_rules": "Updated rules",
            "is_active": False,
        }

        response = api_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["available_beds"] == 4
        assert response.data["custom_rules"] == "Updated rules"
        assert response.data["is_active"] is False

    def test_update_others_hosting_fails(self, api_client, other_user, hosting):
        """Test qu'un utilisateur ne peut pas mettre à jour l'hébergement d'un autre."""
        api_client.force_authenticate(user=other_user)

        url = reverse("event-hosting-detail", kwargs={"pk": hosting.id})
        data = {"available_beds": 1}

        response = api_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_own_hosting(self, api_client, host, hosting):
        """Test qu'un utilisateur peut supprimer son propre hébergement."""
        api_client.force_authenticate(user=host)

        url = reverse("event-hosting-detail", kwargs={"pk": hosting.id})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Vérifier que l'hébergement a bien été supprimé
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_others_hosting_fails(self, api_client, other_user, hosting):
        """Test qu'un utilisateur ne peut pas supprimer l'hébergement d'un autre."""
        api_client.force_authenticate(user=other_user)

        url = reverse("event-hosting-detail", kwargs={"pk": hosting.id})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_filter_hostings_by_event(self, api_client, host, event, hosting):
        """Test du filtrage des hébergements par événement."""
        api_client.force_authenticate(user=host)

        # Créer un autre événement et hébergement
        other_event = Event.objects.create(
            name="Other Event",
            description="Other Event Description",
            location="Other Location",
            start_date=timezone.now() + datetime.timedelta(days=20),
            end_date=timezone.now() + datetime.timedelta(days=22),
            type="DRINK",
        )

        EventHosting.objects.create(event=other_event, host=host, available_beds=1)

        # Filtrer par le premier événement
        url = f"{reverse('event-hosting-list')}?event={event.id}"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["event"] == event.id

        # Filtrer par le second événement
        url = f"{reverse('event-hosting-list')}?event={other_event.id}"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["event"] == other_event.id

    def test_me_action(self, api_client, host, hosting):
        """Test de l'action me pour récupérer ses propres hébergements."""
        api_client.force_authenticate(user=host)

        url = reverse("event-hosting-me")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["id"] == hosting.id
        assert response.data[0]["host"]["id"] == host.id

    def test_for_event_action(self, api_client, host, event, hosting):
        """Test de l'action for_event pour récupérer les hébergements d'un événement."""
        api_client.force_authenticate(user=host)

        url = f"{reverse('event-hosting-for-event')}?event_id={event.id}"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["id"] == hosting.id
        assert response.data[0]["event"] == event.id

    def test_for_event_action_without_event_id(self, api_client, host):
        """Test de l'action for_event sans spécifier d'event_id."""
        api_client.force_authenticate(user=host)

        url = reverse("event-hosting-for-event")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "event_id" in response.data["error"]

    def test_available_places_action(self, api_client, host, hosting, hosting_request):
        """Test de l'action available_places."""
        api_client.force_authenticate(user=host)

        url = reverse("event-hosting-available-places", kwargs={"pk": hosting.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_beds"] == 2
        assert response.data["accepted_guests"] == 1
        assert response.data["available_places"] == 1
