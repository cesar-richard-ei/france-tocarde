import factory
import datetime
from ft.user.models import User


class UserFactory(factory.django.DjangoModelFactory):
    """Factory pour créer des instances User à des fins de test."""

    class Meta:
        model = User

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True
    is_staff = False
    is_superuser = False
    password = factory.PostGenerationMethodCall("set_password", "password123")

    # Attributs spécifiques au modèle User
    address = factory.Faker("street_address")
    city = factory.Faker("city")
    zip_code = factory.Faker("postcode")
    country = factory.Faker("country")
    # Limiter la taille du numéro de téléphone à 14 caractères maximum
    phone_number = factory.LazyFunction(
        lambda: factory.Faker("phone_number").generate()[:14]
    )
    birth_date = factory.LazyFunction(
        lambda: datetime.date.today() - datetime.timedelta(days=365 * 25)
    )
    has_car = False
    car_seats = 0
    can_host_peoples = False
    home_available_beds = 0
    home_rules = None
    faluche_nickname = None
    faluche_status = None

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.groups.add(*extracted)


class StaffUserFactory(UserFactory):
    """Factory pour créer des instances User avec des droits staff."""

    is_staff = True


class UserWithCarFactory(UserFactory):
    """Factory pour créer des utilisateurs avec voiture."""

    has_car = True
    car_seats = 5


class UserWithAccommodationFactory(UserFactory):
    """Factory pour créer des utilisateurs pouvant héberger."""

    can_host_peoples = True
    home_available_beds = 2
    home_rules = "Pas de fumée, pas d'animaux"
