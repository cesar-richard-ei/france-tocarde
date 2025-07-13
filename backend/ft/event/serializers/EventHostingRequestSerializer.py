from rest_framework import serializers
from ft.event.models import EventHostingRequest, EventHosting
from ft.user.serializers import UserSerializer
from ft.event.serializers import EventHostingSerializer


class EventHostingRequestSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle EventHostingRequest
    """

    # En lecture : objets complets
    # En écriture : simplement l'ID
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

        # Si nous n'avons pas l'ID d'hébergement, c'est une erreur
        if not hosting_id:
            raise serializers.ValidationError(
                {"hosting_id": "L'ID d'hébergement est requis."}
            )

        # Récupérer l'objet hébergement à partir de l'ID
        try:
            hosting = EventHosting.objects.get(id=hosting_id)
        except EventHosting.DoesNotExist:
            raise serializers.ValidationError(
                {"hosting_id": "Cet hébergement n'existe pas."}
            )

        requester = self.context["request"].user

        # Vérification que l'utilisateur n'est pas l'hôte
        if hosting.host == requester:
            raise serializers.ValidationError(
                {"hosting_id": "Vous ne pouvez pas demander votre propre hébergement."}
            )

        # Vérification que l'utilisateur n'a pas déjà une demande active
        # pour le même événement
        event = hosting.event
        existing_requests = EventHostingRequest.objects.filter(
            hosting__event=event,
            requester=requester,
            status__in=["PENDING", "ACCEPTED"],
        )

        # Exclure la demande actuelle en cas de mise à jour
        if self.instance:
            existing_requests = existing_requests.exclude(pk=self.instance.pk)

        if existing_requests.exists():
            raise serializers.ValidationError(
                {
                    "hosting_id": "Vous avez déjà une demande en cours pour cet événement."
                }
            )

        # Remplacer l'id par l'instance complète pour le reste du traitement
        data["hosting"] = hosting
        return data


class EventHostingRequestActionSerializer(serializers.Serializer):
    """
    Serializer pour les actions sur les demandes d'hébergement
    """

    host_message = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        return data
