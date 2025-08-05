import factory
from ft.event.models import EventSubscription
from tests.event.factories.event import EventFactory
from tests.user.factories.user import UserFactory


class EventSubscriptionFactory(factory.django.DjangoModelFactory):
    """Factory pour créer des instances EventSubscription pour les tests."""

    class Meta:
        model = EventSubscription
        django_get_or_create = ("event", "user")

    event = factory.SubFactory(EventFactory)
    user = factory.SubFactory(UserFactory)
    answer = "YES"
    can_invite = True
    is_active = True


class EventSubscriptionNoFactory(EventSubscriptionFactory):
    """Factory pour créer des inscriptions avec réponse négative."""

    answer = "NO"


class EventSubscriptionMaybeFactory(EventSubscriptionFactory):
    """Factory pour créer des inscriptions avec réponse incertaine."""

    answer = "MAYBE"


class InactiveEventSubscriptionFactory(EventSubscriptionFactory):
    """Factory pour créer des inscriptions inactives."""

    is_active = False
