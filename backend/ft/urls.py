from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularRedocView, SpectacularAPIView
from ft.views.VersionView import VersionView


def health_check(request):
    return HttpResponse("OK")


urlpatterns = (
    [
        path("api/admin/", admin.site.urls),
        path("api/api-auth/", include("rest_framework.urls")),
        path("api/health_check", health_check, name="health_check"),
        path("api/accounts/", include("allauth.urls")),
        path("api/_allauth/", include("allauth.headless.urls")),
        path("api/user/", include("ft.user.urls")),
        path("api/event/", include("ft.event.urls")),
        path("api/resources/", include("ft.resources.urls")),
        path("api/version/", VersionView.as_view(), name="version"),
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path(
            "api/schema/redoc/",
            SpectacularRedocView.as_view(url_name="schema"),
            name="redoc",
        ),
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)
