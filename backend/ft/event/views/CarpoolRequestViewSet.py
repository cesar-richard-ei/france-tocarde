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
    API endpoint pour les demandes de covoiturage.
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
        # Les utilisateurs voient les demandes associées à leurs trajets (en tant que conducteur)
        # ou leurs propres demandes (en tant que passager)
        return CarpoolRequest.objects.filter(
            trip__driver=user
        ) | CarpoolRequest.objects.filter(passenger=user)

    def perform_create(self, serializer):
        """
        Associe l'utilisateur courant comme passager lors de la création.
        """
        serializer.save(passenger=self.request.user)

    @action(detail=True, methods=["post"])
    def request_action(self, request, pk=None):
        """
        Endpoint pour effectuer une action sur une demande:
        - accept: accepter la demande (conducteur uniquement)
        - reject: refuser la demande (conducteur uniquement)
        - cancel: annuler la demande (passager uniquement)
        """
        carpool_request = self.get_object()
        serializer = CarpoolRequestActionSerializer(
            data=request.data,
            context={"request": request, "carpool_request": carpool_request},
        )

        if serializer.is_valid():
            action = serializer.validated_data["action"]
            response_message = serializer.validated_data.get("response_message")

            # Mettre à jour le statut selon l'action
            if action == "accept":
                carpool_request.status = "ACCEPTED"
            elif action == "reject":
                carpool_request.status = "REJECTED"
            elif action == "cancel":
                carpool_request.status = "CANCELLED"

            # Enregistrer le message de réponse s'il est fourni
            if response_message:
                carpool_request.response_message = response_message

            carpool_request.save()

            # Retourner la demande mise à jour
            return Response(
                CarpoolRequestSerializer(carpool_request).data,
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def payment(self, request, pk=None):
        """
        Endpoint pour créer ou mettre à jour un paiement pour une demande de covoiturage.
        Seul le conducteur peut enregistrer des paiements.
        """
        carpool_request = self.get_object()

        # Vérifier que l'utilisateur est bien le conducteur
        if request.user != carpool_request.trip.driver:
            return Response(
                {"detail": "Seul le conducteur peut enregistrer des paiements."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Vérifier que la demande est acceptée
        if carpool_request.status != "ACCEPTED":
            return Response(
                {
                    "detail": "Seules les demandes acceptées peuvent avoir des paiements."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = request.data.copy()
        data["request_id"] = carpool_request.id

        # On vérifie si un paiement complet existe déjà
        existing_payment = CarpoolPayment.objects.filter(
            request=carpool_request, is_completed=True
        ).first()

        if existing_payment:
            # Mettre à jour le paiement existant
            serializer = CarpoolPaymentSerializer(
                existing_payment, data=data, partial=True, context={"request": request}
            )
        else:
            # Créer un nouveau paiement
            serializer = CarpoolPaymentSerializer(
                data=data, context={"request": request}
            )

        if serializer.is_valid():
            payment = serializer.save()

            # Retourner la demande mise à jour avec les informations de paiement
            return Response(
                CarpoolRequestSerializer(carpool_request).data,
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
