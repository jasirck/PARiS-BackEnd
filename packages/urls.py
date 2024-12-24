from django.urls import path
from . import views

urlpatterns = [
    path('packages/',views.PackageView.as_view(),name='package'),
    path('admin-packages/', views.AdminPackageView.as_view(), name='package-list'),  
    path('admin/admin-packages/<int:pk>/', views.AdminPackageView.as_view(), name='package-detail'),
    path('packages-deteils/<int:pk>/', views.PackageDetailsView.as_view(), name='package-details'),

    path('admin-packages-request/', views.BookedPackageView.as_view(), name='package-request'),


    path('holidays/', views.HolidaysView.as_view(),name='holiday'),
    path('admin-holidays/', views.AdminHolidayView.as_view(), name='holiday-list'),  
    path('admin/admin-holidays/<int:pk>/', views.AdminHolidayView.as_view(), name='holiday-detail'),
    path('holidays-deteils/<int:pk>/', views.HolidayDetailsView.as_view(), name='holiday-details'),

    path('booked-holidays/', views.BookedHolidayView.as_view(), name='package-request'),
    path('admin-booked-holidays/', views.AdminBookedHolidayView.as_view(), name='package'),


    path('admin-package-categories/', views.CategoryView.as_view(), name='category-list'),  
    path('admin-package-categories/<int:pk>/', views.CategoryView.as_view(), name='category-detail'),  
    path('package-categories/', views.CategoryShowView.as_view(), name='category-Show'), 
    
    path('booked-package/', views.BookedPackageView.as_view(), name='package-request'),
    path('admin-booked-package/', views.AdminBookedpackageView.as_view(), name='package'),

    path('create-checkout-session/', views.CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path("confirm-payment/",views.ConfirmPaymentView.as_view(), name="confirm-payment"),

]
