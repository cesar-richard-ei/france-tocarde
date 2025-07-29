from datetime import datetime
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from ft.user.managers import UserManager


class User(AbstractUser):
    """
    A User is a user of the FT application.
    """

    class FalucheStatus(models.TextChoices):
        SYMPATHISANT = "SYMPATHISANT", "Sympathisant"
        IMPETRANT = "IMPETRANT", "Impétrant"
        BAPTISE = "BAPTISE", "Baptisé"
        OTHER = "OTHER", "Autre folklore"

    email: str = models.EmailField(_("email address"), unique=True)
    last_name: str = models.CharField(max_length=150, verbose_name="Nom")
    first_name: str = models.CharField(max_length=150, verbose_name="Prénom")

    address: str = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="Adresse"
    )
    city: str = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Ville"
    )
    zip_code: str = models.CharField(
        max_length=10, null=True, blank=True, verbose_name="Code postal"
    )
    country: str = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Pays"
    )

    phone_number: str = models.CharField(
        max_length=14,
        null=True,
        blank=True,
        verbose_name="Numéro de téléphone",
        help_text="Numéro de téléphone de l'utilisateur",
    )
    birth_date: datetime.date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de naissance",
        help_text="Date de naissance de l'utilisateur (format: JJ/MM/AAAA)",
    )

    has_car: bool = models.BooleanField(
        default=False,
        verbose_name="A un véhicule",
        help_text="Si vous avez un véhicule pour transporter des personnes.",
    )
    car_seats: int = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Nombre de places dans le véhicule",
        help_text="Nombre de places disponibles (conducteur inclus)",
    )

    can_host_peoples: bool = models.BooleanField(
        default=False,
        verbose_name="Peut accueillir des personnes",
        help_text="Si vous avez un domicile avec des lits disponibles.",
    )
    home_available_beds: int = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Nombre de lits disponibles",
        help_text="Nombre de lits disponibles pour les personnes hébergées",
    )
    home_rules: str = models.TextField(
        null=True,
        blank=True,
        verbose_name="Règles du domicile",
        help_text="Ex: Allergies, horraires, etc.",
    )

    faluche_nickname: str = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        verbose_name="Surnom de Fal",
        help_text="Surnom de Faluche de l'utilisateur",
    )
    faluche_status = models.CharField(
        max_length=20,
        choices=FalucheStatus.choices,
        null=True,
        blank=True,
        verbose_name="Statut de Faluche",
        help_text="Statut de Faluche de l'utilisateur",
    )

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["last_name", "first_name"]

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)
