from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "admin_profile")
            and request.user.admin_profile.role == "superadmin"
        )


class IsAnyAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "admin_profile")



class IsSuperAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return (
            request.user.is_authenticated
            and hasattr(request.user, "admin_profile")
            and request.user.admin_profile.role == "superadmin"
        )