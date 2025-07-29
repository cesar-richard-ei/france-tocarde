from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count

from ft.event.models import EventHostingRequest, EventHosting
from ft.event.serializers import (
    EventHostingRequestSerializer,
    EventHostingRequestActionSerializer,
)
from ft.event.permissions import IsHostingRequestRequesterOrHost


class EventHostingRequestViewSet(viewsets.ModelViewSet):
    """
    API endpoint to manage the hosting requests.
    """

    serializer_class = EventHostingRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsHostingRequestRequesterOrHost]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["requester__first_name", "requester__last_name", "status"]
    ordering_fields = ["created_at", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """
        This view returns a list of hosting requests.
        - A user sees their own requests
        - A host sees the requests for their hostings
        """
        user = self.request.user
        queryset = EventHostingRequest.objects.all()

        if not user.is_staff:
            user_requests = queryset.filter(requester=user)

            host_requests = queryset.filter(hosting__host=user)

            queryset = user_requests | host_requests

        status = self.request.query_params.get("status", None)
        if status:
            queryset = queryset.filter(status=status)

        hosting_id = self.request.query_params.get("hosting", None)
        if hosting_id:
            queryset = queryset.filter(hosting=hosting_id)

        requester_id = self.request.query_params.get("requester", None)
        if requester_id:
            queryset = queryset.filter(requester=requester_id)

        return queryset

    def perform_create(self, serializer):
        """
        Associate the current user as requester when creating.
        """
        serializer.save(requester=self.request.user)

    def get_places_available(self, hosting):
        """
        Calculate the number of places still available for a hosting.
        """
        accepted_requests_count = EventHostingRequest.objects.filter(
            hosting=hosting, status=EventHostingRequest.Status.ACCEPTED
        ).count()

        return hosting.available_beds - accepted_requests_count

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        """
        Action to accept a hosting request.
        Only the host can accept a request.
        """
        hosting_request = self.get_object()

        if hosting_request.hosting.host != request.user:
            return Response(
                {"error": "Vous n'êtes pas autorisé à accepter cette demande."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if hosting_request.status != EventHostingRequest.Status.PENDING:
            return Response(
                {"error": "Cette demande ne peut plus être acceptée."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        places_available = self.get_places_available(hosting_request.hosting)
        if places_available <= 0:
            return Response(
                {"error": "Vous n'avez plus de places disponibles."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = EventHostingRequestActionSerializer(data=request.data)
        if serializer.is_valid():
            if "host_message" in serializer.validated_data:
                hosting_request.host_message = serializer.validated_data["host_message"]

            hosting_request.accept()
            response_serializer = self.get_serializer(hosting_request)
            return Response(response_serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """
        Action to reject a hosting request.
        Only the host can reject a request.
        """
        hosting_request = self.get_object()

        if hosting_request.hosting.host != request.user:
            return Response(
                {"error": "Vous n'êtes pas autorisé à refuser cette demande."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if hosting_request.status != EventHostingRequest.Status.PENDING:
            return Response(
                {"error": "Cette demande ne peut plus être refusée."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = EventHostingRequestActionSerializer(data=request.data)
        if serializer.is_valid():
            if "host_message" in serializer.validated_data:
                hosting_request.host_message = serializer.validated_data["host_message"]

            hosting_request.reject()
            response_serializer = self.get_serializer(hosting_request)
            return Response(response_serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """
        Action to cancel a hosting request.
        Only the requester can cancel their request.
        """
        hosting_request = self.get_object()

        if hosting_request.requester != request.user:
            return Response(
                {"error": "Vous n'êtes pas autorisé à annuler cette demande."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if hosting_request.status not in [
            EventHostingRequest.Status.PENDING,
            EventHostingRequest.Status.ACCEPTED,
        ]:
            return Response(
                {"error": "Cette demande ne peut plus être annulée."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        hosting_request.cancel()
        serializer = self.get_serializer(hosting_request)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def my_requests(self, request):
        """
        Return only the requests made by the connected user.
        """
        requests = EventHostingRequest.objects.filter(requester=request.user)
        serializer = self.get_serializer(requests, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def for_my_hostings(self, request):
        """
        Return only the requests for the hostings of the connected user.
        """
        requests = EventHostingRequest.objects.filter(hosting__host=request.user)
        serializer = self.get_serializer(requests, many=True)
        return Response(serializer.data)
