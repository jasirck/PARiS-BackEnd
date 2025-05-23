# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("admin/login/", views.AdminLoginView.as_view(), name="admin-login"),
    path("admin/users/", views.UserListView.as_view(), name="user-list"),
    path("admin/admins/", views.AdminListView.as_view(), name="admin-list"),
    path("admin/admins/<int:pk>/", views.AdminDetailView.as_view(), name="admin-detail"),
    path("admin/dashboard/", views.DashboardView.as_view(), name="dashboard"),
]
