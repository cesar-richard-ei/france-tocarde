import pytest
import datetime
from django.utils import timezone
from ft.user.models import Membership, User


@pytest.mark.django_db
class TestMembershipModel:
    """Tests pour le modèle Membership."""

    def test_create_membership(self):
        """Test de la création d'une adhésion."""
        user = User.objects.create_user(
            username="testuser1", email="test1@example.com", password="password123"
        )

        start_date = timezone.now()
        end_date = start_date + datetime.timedelta(days=365)

        membership = Membership.objects.create(
            user=user, start_date=start_date, end_date=end_date, is_active=True
        )

        assert membership.id is not None
        assert membership.user == user
        assert membership.start_date == start_date
        assert membership.end_date == end_date
        assert membership.is_active is True

    def test_membership_str_representation(self):
        """Test de la représentation string du modèle Membership."""
        user = User.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="password123",
            first_name="Jean",
            last_name="Dupont",
        )

        start_date = timezone.now()

        membership = Membership.objects.create(
            user=user,
            start_date=start_date,
            end_date=start_date + datetime.timedelta(days=365),
        )

        expected = f"Jean Dupont ({start_date})"
        assert str(membership) == expected

    def test_membership_duration(self):
        """Test que la durée d'adhésion est d'un an."""
        user = User.objects.create_user(
            username="testuser3", email="test3@example.com", password="password123"
        )

        start_date = timezone.now()
        end_date = start_date + datetime.timedelta(days=365)

        membership = Membership.objects.create(
            user=user, start_date=start_date, end_date=end_date
        )

        # La différence devrait être d'un an (avec une marge pour les calculs)
        diff = membership.end_date - membership.start_date
        assert 364 <= diff.days <= 366

    def test_expired_membership(self):
        """Test pour une adhésion expirée."""
        user = User.objects.create_user(
            username="testuser4", email="test4@example.com", password="password123"
        )

        now = timezone.now()
        start_date = now - datetime.timedelta(days=730)  # 2 ans avant
        end_date = now - datetime.timedelta(days=365)  # 1 an avant

        membership = Membership.objects.create(
            user=user, start_date=start_date, end_date=end_date, is_active=False
        )

        assert membership.is_active is False
        assert membership.end_date < now
