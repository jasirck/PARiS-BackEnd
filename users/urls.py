from django.urls import path
from . import views

urlpatterns = [
    path("user/login", views.LoginView.as_view(), name="send-otp"),
    path("auth/google/", views.GoogleLogin.as_view(), name="google_callback"),
    path("user/register", views.RegisterView.as_view(), name="send-otp"),
    path("user/number-verify", views.SendOtpView.as_view(), name="send-otp"),
    path(
        "user/forgot-number-verify", views.SendOtpForgotView.as_view(), name="send-otp"
    ),
    path("user/otp-verify", views.VerifyOtpView.as_view(), name="send-otp"),
    path("token/refresh/", views.RefreshTokenView.as_view(), name="refresh-token"),
    path(
        "user/reset-password/", views.PasswordResetView.as_view(), name="reset-password"
    ),
    path("facebook-data-deletion/", views.FacebookDataDeletionView.as_view(), name="facebook-data-deletion"),
]
