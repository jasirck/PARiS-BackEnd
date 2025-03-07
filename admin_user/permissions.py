from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and hasattr(request.user, "is_staff") and request.user.is_staff
        )
