import factory
import datetime
from django.utils import timezone
from ft.user.models import Membership
from tests.user.factories.user import UserFactory


class MembershipFactory(factory.django.DjangoModelFactory):
    """Factory pour créer des instances Membership à des fins de test."""

    class Meta:
        model = Membership

    user = factory.SubFactory(UserFactory)
    start_date = factory.LazyFunction(lambda: timezone.now())
    end_date = factory.LazyFunction(
        lambda: timezone.now() + datetime.timedelta(days=365)
    )
    is_active = True


class ExpiredMembershipFactory(MembershipFactory):
    """Factory pour créer des adhésions expirées."""

    start_date = factory.LazyFunction(
        lambda: timezone.now() - datetime.timedelta(days=730)
    )
    end_date = factory.LazyFunction(
        lambda: timezone.now() - datetime.timedelta(days=365)
    )
    is_active = False
