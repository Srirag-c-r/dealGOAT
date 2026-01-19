"""
Custom permission classes for admin dashboard
"""
from rest_framework.permissions import BasePermission


class IsSuperAdmin(BasePermission):
    """
    Permission class for Super Admin role.
    Allows access only to superusers.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_superuser
        )


class IsModerator(BasePermission):
    """
    Permission class for Moderator role.
    Allows access to superusers and users in the 'Moderator' group.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Super admins have all permissions
        if request.user.is_superuser:
            return True
        
        # Check if user is in Moderator group
        return request.user.groups.filter(name='Moderator').exists()


class IsAnalyst(BasePermission):
    """
    Permission class for Analyst role.
    Allows access to all staff members (read-only operations).
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_staff
        )


class IsAdminUser(BasePermission):
    """
    Permission class for any admin user.
    Allows access to staff members, moderators, and superusers.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_staff
        )


class IsAdminOrReadOnly(BasePermission):
    """
    Permission class that allows read access to anyone,
    but write access only to admin users.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # Write permissions only for admin users
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_staff
        )
