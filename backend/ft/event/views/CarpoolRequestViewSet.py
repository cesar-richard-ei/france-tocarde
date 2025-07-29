from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from ft.event.models import CarpoolRequest, CarpoolPayment
from ft.event.serializers import (
    CarpoolRequestSerializer,
    CarpoolRequestActionSerializer,
    CarpoolPaymentSerializer,
)


class CarpoolRequestViewSet(viewsets.ModelViewSet):
    """
    API endpoint for the carpool requests.
    """

    queryset = CarpoolRequest.objects.all()
    serializer_class = CarpoolRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["trip", "passenger", "status", "is_active"]
    search_fields = ["message"]

    def get_queryset(self):
        """
        Filtre les demandes selon l'utilisateur connecté.
        - Conducteur: voit toutes les demandes pour ses trajets
        - Passager: voit toutes ses demandes
        """
        user = self.request.user
        return CarpoolRequest.objects.filter(
            trip__driver=user
        ) | CarpoolRequest.objects.filter(passenger=user)

    def perform_create(self, serializer):
        """
        Associate the current user as passenger when creating.
        """
        serializer.save(passenger=self.request.user)

    @action(detail=True, methods=["post"])
    def request_action(self, request, pk=None):
        """
        Endpoint to perform an action on a request:
        - accept: accept the request (driver only)
        - reject: reject the request (driver only)
        - cancel: cancel the request (passenger only)
        """
        carpool_request = self.get_object()
        serializer = CarpoolRequestActionSerializer(
            data=request.data,
            context={"request": request, "carpool_request": carpool_request},
        )

        if serializer.is_valid():
            action = serializer.validated_data["action"]
            response_message = serializer.validated_data.get("response_message")

            if action == "accept":
                carpool_request.status = "ACCEPTED"
            elif action == "reject":
                carpool_request.status = "REJECTED"
            elif action == "cancel":
                carpool_request.status = "CANCELLED"

            if response_message:
                carpool_request.response_message = response_message

            carpool_request.save()

            return Response(
                CarpoolRequestSerializer(carpool_request).data,
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def payment(self, request, pk=None):
        """
        Endpoint to create or update a payment for a carpool request.
        Only the driver can register payments.
        """
        carpool_request = self.get_object()

        if request.user != carpool_request.trip.driver:
            return Response(
                {"detail": "Seul le conducteur peut enregistrer des paiements."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if carpool_request.status != "ACCEPTED":
            return Response(
                {
                    "detail": "Seules les demandes acceptées peuvent avoir des paiements."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = request.data.copy()
        data["request_id"] = carpool_request.id

        existing_payment = CarpoolPayment.objects.filter(
            request=carpool_request, is_completed=True
        ).first()

        if existing_payment:
            serializer = CarpoolPaymentSerializer(
                existing_payment, data=data, partial=True, context={"request": request}
            )
        else:
            serializer = CarpoolPaymentSerializer(
                data=data, context={"request": request}
            )

        if serializer.is_valid():
            payment = serializer.save()

            return Response(
                CarpoolRequestSerializer(carpool_request).data,
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
