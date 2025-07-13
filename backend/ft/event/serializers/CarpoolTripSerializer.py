from rest_framework import serializers
from ft.user.serializers import UserSerializer
from ft.event.models import CarpoolTrip, Event
from ft.event.serializers import EventSerializer


class CarpoolTripSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle CarpoolTrip.
    """

    driver = UserSerializer(read_only=True)
    driver_id = serializers.PrimaryKeyRelatedField(
        source="driver",
        queryset=Event.objects.all(),
        write_only=True,
        required=False,
    )
    event = EventSerializer(read_only=True)
    event_id = serializers.PrimaryKeyRelatedField(
        source="event",
        queryset=Event.objects.all(),
        write_only=True,
    )
    seats_available = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)

    class Meta:
        model = CarpoolTrip
        fields = [
            "id",
            "driver",
            "driver_id",
            "event",
            "event_id",
            "departure_city",
            "departure_address",
            "arrival_city",
            "arrival_address",
            "departure_datetime",
            "return_datetime",
            "has_return",
            "seats_total",
            "seats_available",
            "is_full",
            "price_per_seat",
            "additional_info",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "seats_available",
            "is_full",
        ]

    def create(self, validated_data):
        # Si aucun conducteur n'est spécifié, on utilise l'utilisateur courant
        if "driver" not in validated_data:
            validated_data["driver"] = self.context["request"].user
        return super().create(validated_data)
