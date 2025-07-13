from rest_framework import serializers
from ft.user.serializers import UserSerializer
from ft.event.models import CarpoolRequest, CarpoolTrip
from .CarpoolTripSerializer import CarpoolTripSerializer


class CarpoolRequestSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle CarpoolRequest.
    """

    passenger = UserSerializer(read_only=True)
    trip = CarpoolTripSerializer(read_only=True)

    is_paid = serializers.SerializerMethodField()
    total_paid = serializers.SerializerMethodField()
    expected_amount = serializers.SerializerMethodField()

    class Meta:
        model = CarpoolRequest
        fields = [
            "id",
            "passenger",
            "trip",
            "status",
            "seats_requested",
            "message",
            "response_message",
            "is_active",
            "created_at",
            "updated_at",
            "is_paid",
            "total_paid",
            "expected_amount",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def get_is_paid(self, obj):
        """
        Retourne si la demande est entièrement payée.
        """
        return obj.is_paid

    def get_total_paid(self, obj):
        """
        Retourne le montant total payé pour cette demande.
        """
        return obj.total_paid

    def get_expected_amount(self, obj):
        """
        Retourne le montant attendu pour cette demande.
        """
        return obj.expected_amount

    def create(self, validated_data):
        # Si aucun passager n'est spécifié, on utilise l'utilisateur courant
        if "passenger" not in validated_data:
            validated_data["passenger"] = self.context["request"].user

        # On vérifie que le conducteur n'essaie pas de faire une demande sur son propre trajet
        if validated_data["passenger"] == validated_data["trip"].driver:
            raise serializers.ValidationError(
                {
                    "passenger": "Le conducteur ne peut pas demander une place sur son propre trajet."
                }
            )

        # On vérifie qu'il reste assez de places
        trip = validated_data["trip"]
        seats_requested = validated_data.get("seats_requested", 1)
        if trip.seats_available < seats_requested:
            raise serializers.ValidationError(
                {
                    "seats_requested": f"Il ne reste que {trip.seats_available} place(s) disponible(s)."
                }
            )

        # On vérifie qu'il n'y a pas déjà une demande pour ce passager et ce trajet
        existing_request = CarpoolRequest.objects.filter(
            passenger=validated_data["passenger"],
            trip=validated_data["trip"],
            status__in=["PENDING", "ACCEPTED"],
            is_active=True,
        ).exists()

        if existing_request:
            if existing_request.status == "PENDING":
                raise serializers.ValidationError(
                    {"trip": "Vous avez déjà une demande en attente pour ce trajet."}
                )
            elif existing_request.status == "ACCEPTED":
                raise serializers.ValidationError(
                    {"trip": "Vous avez déjà une réservation acceptée pour ce trajet."}
                )

        # Par défaut, le statut est "PENDING"
        validated_data["status"] = "PENDING"

        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Vérifier si le status est mis à jour
        if "status" in validated_data:
            new_status = validated_data["status"]

            # Vérifier que le nouveau status est valide
            if new_status not in dict(CarpoolRequest.STATUS_CHOICES):
                raise serializers.ValidationError(
                    {"status": f"Le statut '{new_status}' n'est pas valide."}
                )

            # Si on passe de PENDING à ACCEPTED, vérifier les places disponibles
            if instance.status == "PENDING" and new_status == "ACCEPTED":
                trip = instance.trip
                if trip.seats_available < instance.seats_requested:
                    raise serializers.ValidationError(
                        {"status": f"{trip.seats_available} places restantes."}
                    )

        return super().update(instance, validated_data)


class CarpoolRequestActionSerializer(serializers.Serializer):
    """
    Sérialiseur pour les actions sur une demande de covoiturage.
    """

    action = serializers.ChoiceField(
        choices=["accept", "reject", "cancel"],
        required=True,
    )
    response_message = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        request = self.context.get("request")
        carpool_request = self.context.get("carpool_request")
        user = request.user

        # Vérifier qui peut faire quelle action
        if data["action"] == "accept" or data["action"] == "reject":
            # Seul le conducteur peut accepter ou refuser
            if user != carpool_request.trip.driver:
                raise serializers.ValidationError(
                    {
                        "action": "Seul le conducteur peut accepter ou refuser une demande."
                    }
                )

            # On ne peut pas accepter ou refuser une demande déjà traitée
            if carpool_request.status != "PENDING":
                raise serializers.ValidationError(
                    {
                        "action": f"Cette demande a déjà été {carpool_request.get_status_display().lower()}."
                    }
                )

            # Pour une acceptation, vérifier qu'il reste des places
            if data["action"] == "accept":
                trip = carpool_request.trip
                if trip.seats_available < carpool_request.seats_requested:
                    raise serializers.ValidationError(
                        {
                            "action": f"Il ne reste que {trip.seats_available} place(s) disponible(s)."
                        }
                    )

        elif data["action"] == "cancel":
            if user != carpool_request.passenger:
                raise serializers.ValidationError(
                    {"action": "Seul le passager peut annuler sa demande."}
                )

            if carpool_request.status in ["CANCELLED", "REJECTED"]:
                raise serializers.ValidationError(
                    {
                        "action": f"Cette demande a déjà été {carpool_request.get_status_display().lower()}."
                    }
                )

        return data
