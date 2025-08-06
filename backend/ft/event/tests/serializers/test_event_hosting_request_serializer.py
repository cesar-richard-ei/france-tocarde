import pytest
from django.utils import timezone
import datetime
from rest_framework.exceptions import ValidationError
from ft.user.models import User
from ft.event.models import Event, EventHosting, EventHostingRequest
from ft.event.serializers import EventHostingRequestSerializer


@pytest.mark.django_db
class TestEventHostingRequestSerializer:
    """Tests pour le EventHostingRequestSerializer."""

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

    @pytest.fixture
    def request_context(self, requester):
        """Fixture pour simuler le contexte de la requête."""

        class MockRequest:
            def __init__(self, user):
                self.user = user

        return {"request": MockRequest(requester)}

    def test_serialize_hosting_request(self, hosting_request):
        """Test de la sérialisation d'une demande d'hébergement."""
        serializer = EventHostingRequestSerializer(hosting_request)
        data = serializer.data

        assert data["id"] == hosting_request.id
        assert "hosting" in data
        assert "requester" in data
        assert data["status"] == hosting_request.status
        assert data["message"] == hosting_request.message
        assert data["host_message"] == hosting_request.host_message

        # Vérifier que les champs en lecture seule sont bien marqués comme tels dans les métadonnées
        read_only_fields = [
            "id",
            "requester",
            "status",
            "host_message",
            "created_at",
            "updated_at",
        ]
        for field in read_only_fields:
            if field in serializer.fields:  # Vérifier que le champ existe
                assert (
                    serializer.fields[field].read_only is True
                ), f"Le champ {field} devrait être en lecture seule"

    def test_deserialize_valid_hosting_request(
        self, hosting, requester, request_context
    ):
        """Test de la désérialisation d'une demande d'hébergement valide."""
        data = {
            "hosting_id": hosting.id,
            "message": "Je voudrais un hébergement pour l'événement",
        }

        serializer = EventHostingRequestSerializer(data=data, context=request_context)
        assert serializer.is_valid(), serializer.errors

        # Vérifier que les données validées contiennent l'objet hosting
        assert "hosting" in serializer.validated_data
        assert serializer.validated_data["hosting"] == hosting

    def test_validate_request_for_own_hosting(self, hosting, request_context):
        """Test de la validation: un hôte ne peut pas demander son propre hébergement."""
        # Modifier le contexte pour que le requester soit l'hôte
        request_context["request"].user = hosting.host

        data = {
            "hosting_id": hosting.id,
            "message": "Je voudrais un hébergement pour l'événement",
        }

        serializer = EventHostingRequestSerializer(data=data, context=request_context)
        assert not serializer.is_valid()
        assert "hosting_id" in serializer.errors
        assert "propre hébergement" in str(serializer.errors["hosting_id"][0])

    def test_validate_already_accepted_request(
        self, event, requester, host, request_context
    ):
        """Test de la validation: un utilisateur ne peut pas faire plusieurs demandes acceptées."""
        # Créer un premier hébergement et une demande acceptée
        hosting1 = EventHosting.objects.create(event=event, host=host, available_beds=2)

        EventHostingRequest.objects.create(
            hosting=hosting1,
            requester=requester,
            status=EventHostingRequest.Status.ACCEPTED,
        )

        # Créer un second hébergement pour le même événement
        hosting2 = EventHosting.objects.create(
            event=event,
            host=User.objects.create_user(
                username="host2", email="host2@example.com", password="password123"
            ),
            available_beds=3,
        )

        # Tenter de faire une demande pour ce second hébergement
        data = {
            "hosting_id": hosting2.id,
            "message": "Je voudrais un hébergement pour l'événement",
        }

        serializer = EventHostingRequestSerializer(data=data, context=request_context)
        assert not serializer.is_valid()
        assert "hosting_id" in serializer.errors
        assert "déjà une demande acceptée" in str(serializer.errors["hosting_id"][0])

    def test_validate_already_pending_request(
        self, hosting, requester, request_context
    ):
        """Test de la validation: un utilisateur ne peut pas faire plusieurs demandes en cours."""
        # Créer une demande en attente
        EventHostingRequest.objects.create(
            hosting=hosting,
            requester=requester,
            status=EventHostingRequest.Status.PENDING,
        )

        # Tenter de faire une autre demande pour le même hébergement
        data = {
            "hosting_id": hosting.id,
            "message": "Une autre demande pour le même hébergement",
        }

        serializer = EventHostingRequestSerializer(data=data, context=request_context)
        assert not serializer.is_valid()
        assert "hosting_id" in serializer.errors
        assert "déjà une demande en cours" in str(serializer.errors["hosting_id"][0])

    def test_hosting_not_found(self, request_context):
        """Test de la validation: l'hébergement doit exister."""
        data = {
            "hosting_id": 9999,  # ID qui n'existe pas
            "message": "Je voudrais un hébergement",
        }

        serializer = EventHostingRequestSerializer(data=data, context=request_context)
        assert not serializer.is_valid()
        assert "hosting_id" in serializer.errors
        assert "n'existe pas" in str(serializer.errors["hosting_id"][0])

    def test_update_hosting_request(self, hosting_request, request_context, hosting):
        """Test de la mise à jour d'une demande d'hébergement."""
        # Pour la mise à jour, il faut inclure hosting_id
        data = {
            "message": "Message mis à jour",
            "hosting_id": hosting.id,  # Nécessaire pour la validation
        }

        serializer = EventHostingRequestSerializer(
            hosting_request, data=data, partial=True, context=request_context
        )
        assert serializer.is_valid(), serializer.errors

        updated_request = serializer.save()
        assert updated_request.id == hosting_request.id
        assert updated_request.message == "Message mis à jour"

        # Vérifier que les autres champs n'ont pas été modifiés
        assert updated_request.hosting == hosting_request.hosting
        assert updated_request.requester == hosting_request.requester
        assert updated_request.status == hosting_request.status
