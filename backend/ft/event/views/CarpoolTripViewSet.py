from django.db.models import Q, Count, F
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from ft.event.models import CarpoolTrip
from ft.event.serializers import CarpoolTripSerializer


class CarpoolTripViewSet(viewsets.ModelViewSet):
    """
    API endpoint for the carpool trips.
    """

    queryset = CarpoolTrip.objects.all().order_by("-departure_datetime")
    serializer_class = CarpoolTripSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "event",
        "driver",
        "departure_city",
        "arrival_city",
        "is_active",
    ]
    search_fields = ["departure_city", "arrival_city", "additional_info"]
    ordering_fields = ["departure_datetime", "created_at"]

    def get_queryset(self):
        """
        Filter to get the trips according to the request parameters.
        """
        queryset = super().get_queryset()

        has_seats = self.request.query_params.get("has_seats")
        if has_seats is not None:
            queryset = queryset.annotate(
                accepted_seats=Count("requests", filter=Q(requests__status="ACCEPTED"))
            )
            if has_seats.lower() == "true":
                queryset = queryset.filter(seats_total__gt=F("accepted_seats"))

        departure_after = self.request.query_params.get("departure_after")
        if departure_after:
            queryset = queryset.filter(departure_datetime__gte=departure_after)

        departure_before = self.request.query_params.get("departure_before")
        if departure_before:
            queryset = queryset.filter(departure_datetime__lte=departure_before)

        return queryset

    def perform_create(self, serializer):
        """
        Set the current user as driver when creating.
        """
        serializer.save(driver=self.request.user)
