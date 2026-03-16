from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Only admins."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsAdminOrManager(BasePermission):
    """Admins and managers."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('admin', 'manager')


class IsAdminOrManagerOrMechanic(BasePermission):
    """Any authenticated staff member."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('admin', 'manager', 'mechanic')


class NoMechanic(BasePermission):
    """Everyone except mechanics."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role != 'mechanic'
