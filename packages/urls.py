from django.urls import path
from .views import PackageView

urlpatterns = [
    path('packages/', PackageView.as_view(), name='package-list'),  
    path('admin/packages/<int:pk>/', PackageView.as_view(), name='package-detail'),
]
