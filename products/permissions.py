from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        if not (
            request.user and request.user.is_authenticated and request.user.is_staff
        ):
            return False

        if request.method == "POST":
            return False

        return True
