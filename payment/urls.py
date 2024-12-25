from django.urls import path
from . import views

urlpatterns = [
    path('booked-checkout-session/', views.CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    # path('booked-checkout-session/', views.PackageCheckoutSessionView.as_view(), name='create-checkout-session'),
    path("confirm-payment/",views.ConfirmPaymentView.as_view(), name="confirm-payment"),
]
