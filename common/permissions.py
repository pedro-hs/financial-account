from rest_framework.permissions import BasePermission, IsAuthenticated


class IsBackOffice(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'collaborator')


class IsUserBase(IsAuthenticated):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and
                    request.user.role in ('customer', 'collaborator'))
