import pytest
from rest_framework.test import APIRequestFactory
from ft.event.permissions import (
    IsStaffOrReadOnly,
    IsEventSubscriptionOwnerOrReadOnly,
    IsHostingOwnerOrReadOnly,
    IsHostingRequestRequesterOrHost,
)
from ft.user.models import User
from ft.event.models import EventSubscription, Event, EventHosting
from django.utils import timezone
import datetime


@pytest.mark.django_db
class TestIsStaffOrReadOnly:
    """Tests pour la permission IsStaffOrReadOnly."""

    def test_safe_methods_allowed_for_all(self):
        """Test que les méthodes GET, HEAD, OPTIONS sont autorisées pour tous."""
        factory = APIRequestFactory()
        permission = IsStaffOrReadOnly()

        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="password123"
        )

        for method in ["get", "head", "options"]:
            request = getattr(factory, method)("/")
            request.user = user

            assert permission.has_permission(request, None) is True

    def test_unsafe_methods_allowed_for_staff(self):
        """Test que les méthodes POST, PUT, DELETE sont autorisées pour staff."""
        factory = APIRequestFactory()
        permission = IsStaffOrReadOnly()

        staff = User.objects.create_user(
            username="staffuser",
            email="staff@example.com",
            password="password123",
            is_staff=True,
        )

        for method in ["post", "put", "delete", "patch"]:
            request = getattr(factory, method)("/")
            request.user = staff

            assert permission.has_permission(request, None) is True

    def test_unsafe_methods_denied_for_normal_users(self):
        """Test que les méthodes POST, PUT, DELETE sont refusées aux non-staff."""
        factory = APIRequestFactory()
        permission = IsStaffOrReadOnly()

        user = User.objects.create_user(
            username="normaluser",
            email="normal@example.com",
            password="password123",
            is_staff=False,
        )

        for method in ["post", "put", "delete", "patch"]:
            request = getattr(factory, method)("/")
            request.user = user

            assert permission.has_permission(request, None) is False


@pytest.mark.django_db
class TestIsEventSubscriptionOwnerOrReadOnly:
    """Tests pour la permission IsEventSubscriptionOwnerOrReadOnly."""

    def test_safe_methods_allowed_for_all(self):
        """Test que les méthodes GET, HEAD, OPTIONS sont autorisées pour tous."""
        factory = APIRequestFactory()
        permission = IsEventSubscriptionOwnerOrReadOnly()

        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="password123"
        )

        for method in ["get", "head", "options"]:
            request = getattr(factory, method)("/")
            request.user = user

            assert permission.has_object_permission(request, None, None) is True

    def test_owner_can_modify_subscription(self):
        """Test qu'un utilisateur peut modifier sa propre inscription."""
        factory = APIRequestFactory()
        permission = IsEventSubscriptionOwnerOrReadOnly()

        user = User.objects.create_user(
            username="subowner", email="owner@example.com", password="password123"
        )

        event = Event.objects.create(
            name="Test Event",
            location="Paris",
            start_date=timezone.now() + datetime.timedelta(days=30),
            end_date=timezone.now() + datetime.timedelta(days=32),
            type="CONGRESS",
        )

        subscription = EventSubscription.objects.create(
            event=event, user=user, answer="YES"
        )

        for method in ["put", "patch", "delete"]:
            request = getattr(factory, method)("/")
            request.user = user

            assert permission.has_object_permission(request, None, subscription) is True

    def test_non_owner_cannot_modify(self):
        """Test qu'un user ne peut pas modifier l'inscription d'autrui."""
        factory = APIRequestFactory()
        permission = IsEventSubscriptionOwnerOrReadOnly()

        user = User.objects.create_user(
            username="subowner", email="owner@example.com", password="password123"
        )

        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="password123"
        )

        event = Event.objects.create(
            name="Test Event",
            location="Paris",
            start_date=timezone.now() + datetime.timedelta(days=30),
            end_date=timezone.now() + datetime.timedelta(days=32),
            type="CONGRESS",
        )

        subscription = EventSubscription.objects.create(
            event=event, user=user, answer="YES"
        )

        for method in ["put", "patch", "delete"]:
            request = getattr(factory, method)("/")
            request.user = other_user

            assert (
                permission.has_object_permission(request, None, subscription) is False
            )
