from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/", include("admin_user.urls")),
    path("api/", include("users.urls")),
    path("api/", include("packages.urls")),
    path("api/", include("resorts.urls")),
    path("api/", include("profileapp.urls")),
    path("api/", include("payments.urls")),
    path("api/", include("messege.urls")),
    path("api/", include("visas.urls")),
    path("api/", include("flights.urls")),
]
