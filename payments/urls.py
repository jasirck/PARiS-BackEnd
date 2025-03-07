from django.urls import path
from . import views

urlpatterns = [
    path(
        "booked-checkout-session/",
        views.CreateCheckoutSessionView.as_view(),
        name="create-checkout-session",
    ),
    path(
        "confirm-payment/", views.ConfirmPaymentView.as_view(), name="confirm-payment"
    ),
    path("refund-package/", views.RefundPackageView.as_view(), name="refund-package"),
]
