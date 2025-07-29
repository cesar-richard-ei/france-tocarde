from rest_framework import serializers
from ft.event.models import EventHostingRequest, EventHosting
from ft.user.serializers import UserSerializer
from ft.event.serializers import EventHostingSerializer


class EventHostingRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for the EventHostingRequest model.
    """

    requester = UserSerializer(read_only=True)
    hosting = EventHostingSerializer(read_only=True)
    hosting_id = serializers.IntegerField(write_only=True, source="hosting.id")

    class Meta:
        model = EventHostingRequest
        fields = [
            "id",
            "hosting",
            "hosting_id",
            "requester",
            "status",
            "message",
            "host_message",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "requester",
            "status",
            "host_message",
            "created_at",
            "updated_at",
        ]

    def validate(self, data):
        """
        Vérifie que l'utilisateur ne fait pas une demande pour son propre
        hébergement et qu'il n'a pas déjà une demande pour le même événement.
        """
        hosting_id = data.get("hosting", {}).get("id")

        if not hosting_id:
            raise serializers.ValidationError(
                {"hosting_id": "L'ID d'hébergement est requis."}
            )

        try:
            hosting = EventHosting.objects.get(id=hosting_id)
        except EventHosting.DoesNotExist:
            raise serializers.ValidationError(
                {"hosting_id": "Cet hébergement n'existe pas."}
            )

        requester = self.context["request"].user

        if hosting.host == requester:
            raise serializers.ValidationError(
                {"hosting_id": "Vous ne pouvez pas demander votre propre hébergement."}
            )

        event = hosting.event
        existing_requests = EventHostingRequest.objects.filter(
            hosting__event=event,
            requester=requester,
            status="ACCEPTED",
        )

        if self.instance:
            existing_requests = existing_requests.exclude(pk=self.instance.pk)

        if existing_requests.exists():
            raise serializers.ValidationError(
                {
                    "hosting_id": "Vous avez déjà une demande acceptée pour cet événement."
                }
            )

        existing_hosting_requests = EventHostingRequest.objects.filter(
            hosting=hosting,
            requester=requester,
        ).exclude(status__in=["CANCELLED", "REJECTED"])

        if self.instance:
            existing_hosting_requests = existing_hosting_requests.exclude(
                pk=self.instance.pk
            )

        if existing_hosting_requests.exists():
            raise serializers.ValidationError(
                {
                    "hosting_id": "Vous avez déjà une demande en cours "
                    "pour cet hébergement."
                }
            )

        data["hosting"] = hosting
        return data


class EventHostingRequestActionSerializer(serializers.Serializer):
    """
    Serializer for the actions on the hosting requests.
    """

    host_message = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        return data
