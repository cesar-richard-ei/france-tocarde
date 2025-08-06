import pytest
from django.utils import timezone
from ft.user.models import User
from ft.event.models import Event, EventHosting, EventHostingRequest
import datetime


@pytest.mark.django_db
class TestEventHostingRequestModel:
    """Tests pour le modèle EventHostingRequest."""

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
    def hosting_request(self, hosting, requester):
        """Fixture pour créer une demande d'hébergement."""
        return EventHostingRequest.objects.create(
            hosting=hosting, requester=requester, message="I would like a place to stay"
        )

    def test_create_hosting_request(self, hosting, requester):
        """Test de la création d'une demande d'hébergement."""
        hosting_request = EventHostingRequest.objects.create(
            hosting=hosting,
            requester=requester,
            message="Je voudrais un hébergement pour l'événement",
        )

        assert hosting_request.id is not None
        assert hosting_request.hosting == hosting
        assert hosting_request.requester == requester
        assert hosting_request.message == "Je voudrais un hébergement pour l'événement"
        assert hosting_request.status == EventHostingRequest.Status.PENDING
        assert hosting_request.host_message is None

    def test_hosting_request_str_representation(self, hosting_request):
        """Test de la représentation string d'une demande d'hébergement."""
        expected = (
            f"Demande de {hosting_request.requester} pour {hosting_request.hosting}"
        )
        assert str(hosting_request) == expected

    def test_accept_method(self, hosting_request):
        """Test de la méthode accept."""
        assert hosting_request.status == EventHostingRequest.Status.PENDING
        hosting_request.accept()
        assert hosting_request.status == EventHostingRequest.Status.ACCEPTED

        # Vérifier que le statut n'est pas modifié si déjà accepté
        hosting_request.accept()
        assert hosting_request.status == EventHostingRequest.Status.ACCEPTED

    def test_reject_method(self, hosting_request):
        """Test de la méthode reject."""
        assert hosting_request.status == EventHostingRequest.Status.PENDING
        hosting_request.reject()
        assert hosting_request.status == EventHostingRequest.Status.REJECTED

        # Vérifier que le statut n'est pas modifié si déjà rejeté
        hosting_request.reject()
        assert hosting_request.status == EventHostingRequest.Status.REJECTED

    def test_cancel_method(self, hosting_request):
        """Test de la méthode cancel."""
        # Cas 1: Annulation d'une demande en attente
        assert hosting_request.status == EventHostingRequest.Status.PENDING
        hosting_request.cancel()
        assert hosting_request.status == EventHostingRequest.Status.CANCELLED

        # Cas 2: Annulation d'une demande acceptée
        hosting_request.status = EventHostingRequest.Status.ACCEPTED
        hosting_request.save()
        hosting_request.cancel()
        assert hosting_request.status == EventHostingRequest.Status.CANCELLED

        # Cas 3: La méthode cancel ne devrait pas fonctionner sur une demande déjà rejetée
        hosting_request.status = EventHostingRequest.Status.REJECTED
        hosting_request.save()
        hosting_request.cancel()
        # Le statut ne devrait pas changer
        assert hosting_request.status == EventHostingRequest.Status.REJECTED
