from datetime import datetime
from django.db import models

from ft.user.models import User
from ft.event.models import Event


class EventHosting(models.Model):
    """
    An EventHosting represents an offer of hosting proposed by a user for an event.
    """

    event: Event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name="Événement",
        help_text="Événement pour lequel l'hébergement est proposé",
    )
    host: User = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Hôte",
        help_text="Utilisateur qui propose l'hébergement",
        related_name="event_hostings",
    )
    available_beds: int = models.PositiveSmallIntegerField(
        verbose_name="Nombre de lits disponibles",
        help_text="Nombre de lits disponibles pour les personnes hébergées",
    )
    custom_rules: str = models.TextField(
        null=True,
        blank=True,
        verbose_name="Règles spécifiques",
        help_text=(
            "Règles spécifiques pour cet hébergement "
            "(si différentes des règles habituelles)"
        ),
    )
    address_override: str = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Adresse spécifique",
        help_text=(
            "Adresse spécifique pour cet hébergement "
            "(si différente de l'adresse habituelle)"
        ),
    )
    city_override: str = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Ville spécifique",
        help_text=(
            "Ville spécifique pour cet hébergement "
            "(si différente de la ville habituelle)"
        ),
    )
    zip_code_override: str = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name="Code postal spécifique",
        help_text=(
            "Code postal spécifique pour cet hébergement "
            "(si différent du code postal habituel)"
        ),
    )
    country_override: str = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Pays spécifique",
        help_text=(
            "Pays spécifique pour cet hébergement " "(si différent du pays habituel)"
        ),
    )
    is_active: bool = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Si l'offre d'hébergement est active",
    )
    created_at: datetime = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création",
        help_text="Date de création de l'offre d'hébergement",
    )
    updated_at: datetime = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de mise à jour",
        help_text="Date de mise à jour de l'offre d'hébergement",
    )

    class Meta:
        verbose_name = "Hébergement"
        verbose_name_plural = "Hébergements"
        ordering = ["event", "host"]
        unique_together = ["event", "host"]

    def __str__(self):
        return f"Hébergement par {self.host} pour {self.event}"

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.available_beds is None:
                self.available_beds = self.host.home_available_beds
            if not self.custom_rules:
                self.custom_rules = self.host.home_rules

        super().save(*args, **kwargs)
