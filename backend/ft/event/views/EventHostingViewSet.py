from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ft.event.models import EventHosting, Event, EventHostingRequest
from ft.event.serializers import EventHostingSerializer
from ft.event.permissions import IsHostingOwnerOrReadOnly


class EventHostingViewSet(viewsets.ModelViewSet):
    """
    API endpoint to view or modify the hostings.
    """

    serializer_class = EventHostingSerializer
    permission_classes = [permissions.IsAuthenticated, IsHostingOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["host__first_name", "host__last_name", "event__name"]
    ordering_fields = ["created_at", "available_beds"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """
        This view returns a list of hostings.
        Filtering by event or host is possible by passing the parameter in the URL.
        """
        queryset = EventHosting.objects.all()

        event_id = self.request.query_params.get("event", None)
        if event_id:
            queryset = queryset.filter(event=event_id)

        host_id = self.request.query_params.get("host", None)
        if host_id:
            queryset = queryset.filter(host=host_id)

        is_active = self.request.query_params.get("is_active", None)
        if is_active is not None:
            is_active = is_active.lower() == "true"
            queryset = queryset.filter(is_active=is_active)

        return queryset

    def perform_create(self, serializer):
        """
        Associate the current user as host when creating.
        """
        serializer.save(host=self.request.user)

    @action(detail=False, methods=["get"])
    def me(self, request):
        """
        Return only the hostings proposed by the connected user.
        """
        hostings = EventHosting.objects.filter(host=request.user)
        serializer = self.get_serializer(hostings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def for_event(self, request):
        """
        Return only the hostings proposed for a specific event.
        """
        event_id = request.query_params.get("event_id", None)
        if not event_id:
            return Response({"error": "Paramètre event_id requis."}, status=400)

        try:
            event = Event.objects.get(pk=event_id)
            hostings = EventHosting.objects.filter(event=event, is_active=True)
            serializer = self.get_serializer(hostings, many=True)
            return Response(serializer.data)
        except Event.DoesNotExist:
            return Response({"error": "Événement non trouvé."}, status=404)

    @action(detail=True, methods=["get"])
    def available_places(self, request, pk=None):
        """
        Return the number of places available in this hosting.
        """
        hosting = self.get_object()

        accepted_requests_count = EventHostingRequest.objects.filter(
            hosting=hosting, status="ACCEPTED"
        ).count()

        available_places = hosting.available_beds - accepted_requests_count

        return Response(
            {
                "total_beds": hosting.available_beds,
                "accepted_guests": accepted_requests_count,
                "available_places": available_places,
            }
        )
