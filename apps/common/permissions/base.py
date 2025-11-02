from rest_framework import permissions

from apps.users.models.user import Role


class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role == Role.ADMIN
