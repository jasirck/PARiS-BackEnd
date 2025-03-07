from django.urls import path
from . import views

urlpatterns = [
    path("resorts/", views.ResortView.as_view(), name="resorts"),
    path("resorts/<int:pk>/", views.ResortDetailView.as_view(), name="resort-detail"),
    path("admin-resorts/", views.AdminResortView.as_view(), name="resorts"),
    path(
        "admin-resorts/<int:resort_id>/",
        views.AdminResortView.as_view(),
        name="resorts.get",
    ),
    path(
        "admin-resorts/<int:resort_id>/images/",
        views.AdminResortImageView.as_view(),
        name="resort_images",
    ),
    path("delete-image/", views.delete_image, name="cloudinary-delete"),
    path(
        "admin-resorts-categories/", views.CategoryView.as_view(), name="category-list"
    ),
    path(
        "admin-resorts-categories/<int:pk>/",
        views.CategoryView.as_view(),
        name="category-detail",
    ),
    path("resort-categories/", views.CategoryShowView.as_view(), name="category-Show"),
    path("booked-resort/", views.BookedResortView.as_view(), name="package-request"),
    path("admin-booked-resort/", views.AdminBookedResortView.as_view(), name="package"),
]
