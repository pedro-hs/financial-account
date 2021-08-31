from common.permissions import IsBackOffice, IsUserBase
from rest_framework import generics, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response

from .constants import ACCOUNT_STATUS
from .models import Company, CompanyAccount, PersonAccount
from .serializers import (CompanySerializer, DefaultCompanyAccountSerializer,
                          DefaultPersonAccountSerializer, PostCompanyAccountSerializer,
                          PostPersonAccountSerializer)


class IsUser(IsUserBase):
    def has_object_permission(self, request, view, instance):
        if request.user.role == 'collaborator':
            return True

        return request.user.role == 'customer' and instance.user == request.user


class IsBackOfficeCompany(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'collaborator')


class IsUserCompany(IsAuthenticated):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and
                    request.user.role in ('customer', 'collaborator'))

    def has_object_permission(self, request, view, instance):
        if request.user.role == 'collaborator':
            return True

        return request.user.role == 'customer' and instance.company.user == request.user


class BaseAccountViewSet(generics.CreateAPIView,
                         generics.UpdateAPIView,
                         generics.RetrieveAPIView,
                         viewsets.ViewSet):
    class Meta:
        abstract = True

    def update(self, request, *args, **kwargs):
        instance = self.Meta.model.objects.get(pk=kwargs['pk'])
        data = request.data

        if data.get('status'):
            if data['status'] not in ACCOUNT_STATUS:
                return Response(status=400, data={'message': 'Invalid status'})

            instance.status = data['status']

        if data.get('credit_limit'):
            instance.credit_limit = data['credit_limit']

        if data.get('withdrawal_limit'):
            instance.withdrawal_limit = data['withdrawal_limit']

        instance.save()
        return Response(status=204)


class PersonAccountViewSet(BaseAccountViewSet):
    queryset = PersonAccount.objects.all()
    http_method_names = ['post', 'put', 'get', 'head']
    serializer_class = DefaultPersonAccountSerializer

    class Meta:
        model = PersonAccount

    def get_permissions(self):
        self.permission_classes = [IsUser]

        if self.request.method in ['POST', 'PUT']:
            self.permission_classes = [IsBackOffice]

        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return PostPersonAccountSerializer

        return DefaultPersonAccountSerializer


class CompanyAccountViewSet(BaseAccountViewSet):
    queryset = CompanyAccount.objects.all()
    http_method_names = ['post', 'put', 'get', 'head']
    serializer_class = DefaultCompanyAccountSerializer

    class Meta:
        model = CompanyAccount

    def get_permissions(self):
        self.permission_classes = [IsUserCompany]

        if self.request.method in ['POST', 'PUT']:
            self.permission_classes = [IsBackOfficeCompany]

        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return PostCompanyAccountSerializer

        return DefaultCompanyAccountSerializer


class CompanyViewSet(generics.CreateAPIView,
                     generics.RetrieveAPIView,
                     generics.DestroyAPIView,
                     viewsets.ViewSet):
    queryset = Company.objects.all()
    http_method_names = ['post', 'get', 'delete', 'head']
    serializer_class = CompanySerializer

    class Meta:
        model = PersonAccount

    def get_permissions(self):
        self.permission_classes = [IsUser]

        if (self.request.method in ['POST', 'DELETE'] or
                (self.request.method == 'GET' and not bool(self.kwargs))):
            self.permission_classes = [IsBackOffice]

        return super().get_permissions()
