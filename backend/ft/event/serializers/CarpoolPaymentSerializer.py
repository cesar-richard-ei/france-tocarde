from rest_framework import serializers
from ft.event.models import CarpoolPayment, CarpoolRequest


class CarpoolPaymentSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle CarpoolPayment.
    """

    request_id = serializers.PrimaryKeyRelatedField(
        source="request",
        queryset=CarpoolRequest.objects.all(),
        write_only=True,
    )
    payment_method_display = serializers.CharField(
        source="get_payment_method_display",
        read_only=True,
    )
    payment_status_display = serializers.CharField(
        source="get_payment_status_display",
        read_only=True,
    )

    class Meta:
        model = CarpoolPayment
        fields = [
            "id",
            "request",
            "request_id",
            "amount",
            "is_completed",
            "payment_method",
            "payment_method_display",
            "payment_status_display",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "payment_method_display",
            "payment_status_display",
        ]

    def validate(self, data):
        request = self.context.get("request")
        carpool_request = data.get("request")

        if carpool_request and carpool_request.status != "ACCEPTED":
            raise serializers.ValidationError(
                {
                    "request": "Seules les demandes acceptées peuvent avoir des paiements."
                }
            )

        if carpool_request and request.user != carpool_request.trip.driver:
            raise serializers.ValidationError(
                {"request": "Seul le conducteur peut enregistrer des paiements."}
            )

        return data
