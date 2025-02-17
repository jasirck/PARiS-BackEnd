from django.urls import path
from . import views


urlpatterns = [
    path('admin-visa-categories/', views.VisaCategoryListCreateView.as_view(), name='visa-category-list-create'),
    path('admin-visa-categories/<int:pk>/', views.VisaCategoryDetailView.as_view(), name='visa-category-detail'),
    path('visa-categories/', views.CategoryShowView.as_view(), name='category-show'),
    path('admin-visas/', views.VisaListCreateView.as_view(), name='visa-list-create'),
    path('visas/<int:pk>/', views.VisaDetailView.as_view(), name='visa-detail'),
    path('visa-days/', views.VisaDaysListCreateView.as_view(), name='visa-days-list-create'),
    path('visa-days/<int:pk>/', views.VisaDaysDetailView.as_view(), name='visa-days-detail'),
    path('visas/<int:pk>/visa_days/', views.VisaVisaDaysView.as_view(), name='visa-visa-days'),

    path('booked-visa/', views.BookedVisaView.as_view(), name='booked-visa'),
    path('admin-visa-booking/', views.AdminBookedVisaAPIView.as_view(), name='booked-visa'),

    
]
