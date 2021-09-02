from rest_framework.permissions import BasePermission, IsAuthenticated


class IsBackOffice(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'collaborator')


class IsUserBase(IsAuthenticated):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and
                    request.user.role in ('customer', 'collaborator'))


class IsUser(IsUserBase):
    def has_object_permission(self, request, view, instance):
        if request.user.role == 'collaborator':
            return True

        return request.user.role == 'customer' and instance.user == request.user


class IsUserCompany(IsUserBase):
    def has_object_permission(self, request, view, instance):
        if request.user.role == 'collaborator':
            return True

        return request.user.role == 'customer' and instance.company.user == request.user
