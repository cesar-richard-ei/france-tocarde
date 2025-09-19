from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ft.event.models import Event
from ft.event.serializers import (
    EventSerializer,
    EventSubscribeActionSerializer,
    EventSubscriptionSerializer,
)
from ft.event.permissions import IsStaffOrReadOnly
from rest_framework.permissions import IsAuthenticated


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsStaffOrReadOnly]

    def get_serializer_class(self):
        if self.action == "subscribe":
            return EventSubscribeActionSerializer
        return EventSerializer

    def get_queryset(self):
        return Event.objects.filter(is_active=True)

    @action(
        detail=True,
        methods=["post"],
        url_path="subscribe",
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, *args, **kwargs):
        event = self.get_object()
        from ft.event.models import EventSubscription

        subscription = EventSubscription.objects.update_or_create(
            event=event,
            user=request.user,
            defaults={
                "answer": request.data.get("answer", "YES"),
                "can_invite": request.data.get("can_invite", True),
                "is_active": True,
            },
        )
        serializer = EventSubscriptionSerializer(subscription)
        return Response(serializer.data, status=status.HTTP_200_OK)
