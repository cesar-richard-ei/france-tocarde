from rest_framework import serializers
from ft.event.models import EventHosting
from ft.user.serializers import UserSerializer


class EventHostingSerializer(serializers.ModelSerializer):
    """
    Serializer for the EventHosting model.
    """

    host = UserSerializer(read_only=True)

    class Meta:
        model = EventHosting
        fields = [
            "id",
            "event",
            "host",
            "available_beds",
            "custom_rules",
            "address_override",
            "city_override",
            "zip_code_override",
            "country_override",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "host", "created_at", "updated_at"]

    def create(self, validated_data):
        """
        Create an event hosting with default values from the user profile if necessary.
        """
        user = validated_data.get("host")

        if "available_beds" not in validated_data:
            validated_data["available_beds"] = user.home_available_beds

        if "custom_rules" not in validated_data:
            validated_data["custom_rules"] = user.home_rules

        return super().create(validated_data)
