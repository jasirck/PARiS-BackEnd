
# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('flights/search/', views.FlightSearchView.as_view(), name='flight-search'),
    path('booked/flights/', views.BookFlightView.as_view(), name='booked-flight'),
]