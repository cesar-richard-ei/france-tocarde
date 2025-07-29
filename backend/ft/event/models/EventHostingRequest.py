from django.db import models

from ft.user.models import User
from ft.event.models import EventHosting


class EventHostingRequest(models.Model):
    """
    Une EventHostingRequest représente une demande d'hébergement faite
    par un utilisateur pour un hébergement proposé.
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", "En attente"
        ACCEPTED = "ACCEPTED", "Acceptée"
        REJECTED = "REJECTED", "Refusée"
        CANCELLED = "CANCELLED", "Annulée"

    hosting = models.ForeignKey(
        EventHosting,
        on_delete=models.CASCADE,
        verbose_name="Hébergement",
        help_text="Hébergement demandé",
        related_name="requests",
    )
    requester = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Demandeur",
        help_text="Utilisateur qui fait la demande d'hébergement",
        related_name="hosting_requests",
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Statut",
        help_text="Statut de la demande d'hébergement",
    )
    message = models.TextField(
        null=True,
        blank=True,
        verbose_name="Message",
        help_text="Message du demandeur à l'hôte",
    )
    host_message = models.TextField(
        null=True,
        blank=True,
        verbose_name="Message de l'hôte",
        help_text="Message de l'hôte au demandeur",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création",
        help_text="Date de création de la demande",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de mise à jour",
        help_text="Date de mise à jour de la demande",
    )

    class Meta:
        verbose_name = "Demande d'hébergement"
        verbose_name_plural = "Demandes d'hébergement"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Demande de {self.requester} pour {self.hosting}"

    def accept(self):
        """
        Accepte la demande d'hébergement.
        """
        if self.status == self.Status.PENDING:
            self.status = self.Status.ACCEPTED
            self.save()

    def reject(self):
        """
        Refuse la demande d'hébergement.
        """
        if self.status == self.Status.PENDING:
            self.status = self.Status.REJECTED
            self.save()

    def cancel(self):
        """
        Annule la demande d'hébergement.
        """
        if self.status in [self.Status.PENDING, self.Status.ACCEPTED]:
            self.status = self.Status.CANCELLED
            self.save()
