from rest_framework import serializers
from ft.user.serializers import UserSerializer
from ft.event.models import CarpoolTrip, Event
from ft.event.serializers import EventSerializer
from ft.user.models import User


class CarpoolTripSerializer(serializers.ModelSerializer):
    """
    Serializer for the CarpoolTrip model.
    """

    driver = UserSerializer(read_only=True)
    driver_id = serializers.PrimaryKeyRelatedField(
        source="driver",
        queryset=User.objects.all(),  # Correction: User au lieu de Event
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
        if "driver" not in validated_data:
            validated_data["driver"] = self.context["request"].user
        return super().create(validated_data)
