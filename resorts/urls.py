from django.urls import path
from .views import AdminResortView, AdminResortImageView,ResortView,CategoryView,CategoryShowView,ResortDetailView,delete_image

urlpatterns = [
    path('resorts/', ResortView.as_view(), name='resorts'),
    path('resorts/<int:pk>/', ResortDetailView.as_view(), name='resort-detail'),
    path('admin-resorts/', AdminResortView.as_view(), name='resorts'),
    path('admin-resorts/<int:resort_id>/', AdminResortView.as_view(), name='resorts.get'),
    path('admin-resorts/<int:resort_id>/images/', AdminResortImageView.as_view(), name='resort_images'),
    path('delete-image/', delete_image, name='cloudinary-delete'),
    path('admin-resorts-categories/', CategoryView.as_view(), name='category-list'),  
    path('admin-resorts-categories/<int:pk>/', CategoryView.as_view(), name='category-detail'),  
    path('resort-categories/', CategoryShowView.as_view(), name='category-Show'), 


]
