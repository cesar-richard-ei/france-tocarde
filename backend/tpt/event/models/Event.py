from datetime import datetime
from django.db import models


class Event(models.Model):
    """
    An Event is an event that can be attended by a user.
    """

    name: str = models.CharField(
        max_length=255, verbose_name="Nom", help_text="Nom de la ressource"
    )
    description: str = models.TextField(
        null=True,
        blank=True,
        verbose_name="Description",
        help_text="Description de l'événement",
    )
    location: str = models.CharField(
        max_length=255, verbose_name="Lieu", help_text="Lieu de l'événement"
    )
    start_date: datetime = models.DateTimeField(
        verbose_name="Date de début", help_text="Date de début de l'événement"
    )
    end_date: datetime = models.DateTimeField(
        verbose_name="Date de fin", help_text="Date de fin de l'événement"
    )
    url_signup: str = models.URLField(
        max_length=255,
        verbose_name="URL de l'inscription",
        help_text="URL de l'inscription à l'événement",
    )
    url_website: str = models.URLField(
        max_length=255,
        verbose_name="URL du site web",
        help_text="URL du site web de l'événement",
    )
    prices: str = models.TextField(
        null=True,
        blank=True,
        verbose_name="Prix",
        help_text="Prix de l'événement",
    )
    is_active: bool = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Si l'événement est actif (visible sur le site)",
    )
    created_at: datetime = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création",
        help_text="Date de création de la ressource",
    )
    updated_at: datetime = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de mise à jour",
        help_text="Date de mise à jour de la ressource",
    )

    class Meta:
        verbose_name = "Événement"
        verbose_name_plural = "Événements"
        ordering = ["start_date", "start_date"]

    def __str__(self):
        return "{} ({})".format(self.name, self.location)
