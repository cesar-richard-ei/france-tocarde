import factory
import datetime
from django.utils import timezone
from ft.event.models import Event


class EventFactory(factory.django.DjangoModelFactory):
    """Factory pour créer des instances Event à des fins de test."""

    class Meta:
        model = Event

    name = factory.Faker("sentence", nb_words=4)
    description = factory.Faker("paragraph")
    at_compiegne = True
    is_public = True
    location = factory.Faker("address")
    start_date = factory.LazyFunction(
        lambda: timezone.now() + datetime.timedelta(days=30)
    )
    end_date = factory.LazyFunction(
        lambda: timezone.now() + datetime.timedelta(days=32)
    )
    url_signup = factory.Faker("url")
    url_website = factory.Faker("url")
    prices = "Standard: 15€, Étudiant: 10€"
    is_active = True
    type = "CONGRESS"


class PastEventFactory(EventFactory):
    """Factory pour créer des événements passés."""

    start_date = factory.LazyFunction(
        lambda: timezone.now() - datetime.timedelta(days=32)
    )
    end_date = factory.LazyFunction(
        lambda: timezone.now() - datetime.timedelta(days=30)
    )


class PrivateEventFactory(EventFactory):
    """Factory pour créer des événements privés."""

    is_public = False


class NonCompiegneEventFactory(EventFactory):
    """Factory pour créer des événements hors de Compiègne."""

    at_compiegne = False
