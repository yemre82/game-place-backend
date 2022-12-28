from rest_framework.permissions import BasePermission


class IsVerified(BasePermission):
    message = 'User is not verified'

    def has_permission(self, request, view):
        if not request.user:
            return False

        if not request.user.is_verified:
            return False

        return True