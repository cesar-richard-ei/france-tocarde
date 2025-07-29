from rest_framework import permissions


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée qui autorise l'accès en lecture à tous les
    utilisateurs, mais qui n'autorise les opérations d'écriture qu'aux
    utilisateurs avec is_staff=True.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user and request.user.is_staff


class IsEventSubscriptionOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée pour permettre uniquement au propriétaire
    d'une inscription de la modifier.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user


class IsHostingOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée pour permettre uniquement à l'hôte
    de modifier son offre d'hébergement.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.host == request.user


class IsHostingRequestRequesterOrHost(permissions.BasePermission):
    """
    Permission personnalisée pour les demandes d'hébergement.
    - Le demandeur peut créer et voir ses propres demandes
    - L'hôte peut voir et répondre aux demandes pour son hébergement
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.requester == request.user or obj.hosting.host == request.user
