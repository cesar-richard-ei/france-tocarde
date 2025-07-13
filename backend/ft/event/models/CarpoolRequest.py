from django.db import models
from ft.user.models import User
from .CarpoolTrip import CarpoolTrip


class CarpoolRequest(models.Model):
    """
    Une CarpoolRequest représente une demande de place dans un trajet de covoiturage.
    """

    STATUS_CHOICES = [
        ("PENDING", "En attente"),
        ("ACCEPTED", "Acceptée"),
        ("REJECTED", "Refusée"),
        ("CANCELLED", "Annulée"),
    ]

    passenger = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Passager",
        help_text="Utilisateur demandant une place",
        related_name="carpool_requests_as_passenger",
    )
    trip = models.ForeignKey(
        CarpoolTrip,
        on_delete=models.CASCADE,
        verbose_name="Trajet",
        help_text="Trajet concerné par la demande",
        related_name="requests",
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PENDING",
        verbose_name="Statut",
        help_text="Statut de la demande",
    )
    seats_requested = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Places demandées",
        help_text="Nombre de places demandées",
    )
    message = models.TextField(
        null=True,
        blank=True,
        verbose_name="Message",
        help_text="Message à l'attention du conducteur",
    )
    response_message = models.TextField(
        null=True,
        blank=True,
        verbose_name="Réponse",
        help_text="Réponse du conducteur",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Si la demande est active",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création",
        help_text="Date de création de la demande",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de mise à jour",
        help_text="Date de dernière modification de la demande",
    )

    class Meta:
        verbose_name = "Demande de covoiturage"
        verbose_name_plural = "Demandes de covoiturage"
        ordering = ["-created_at"]
        # Empêcher un passager d'avoir plusieurs demandes actives pour le même trajet
        constraints = [
            models.UniqueConstraint(
                fields=["passenger", "trip", "status"],
                condition=models.Q(status__in=["PENDING", "ACCEPTED"]),
                name="unique_passenger_trip_active",
            )
        ]

    def __str__(self):
        return f"{self.passenger} → {self.trip} ({self.get_status_display()})"

    @property
    def is_paid(self):
        """
        Vérifie si la demande a été entièrement payée.
        """
        # La demande est considérée comme payée s'il existe un paiement complet
        return self.payments.filter(is_completed=True).exists()

    @property
    def total_paid(self):
        """
        Calcule le montant total payé pour cette demande.
        """
        # Somme de tous les paiements associés à cette demande
        return self.payments.aggregate(models.Sum("amount"))["amount__sum"] or 0

    @property
    def expected_amount(self):
        """
        Calcule le montant attendu pour cette demande.
        """
        # Prix par place * nombre de places demandées
        return self.trip.price_per_seat * self.seats_requested
