from common.permissions import IsBackOffice, IsUserBase
from rest_framework import generics, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response

from .models import STATUS, Company, CompanyAccount, PersonAccount
from .serializers import CompanyAccountSerializer, CompanySerializer, PersonAccountSerializer


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


class PersonAccountViewSet(generics.CreateAPIView,
                           generics.UpdateAPIView,
                           generics.RetrieveAPIView,
                           viewsets.ViewSet):
    queryset = PersonAccount.objects.all()
    http_method_names = ['post', 'put', 'get', 'head']
    serializer_class = PersonAccountSerializer

    class Meta:
        model = PersonAccount

    def get_permissions(self):
        self.permission_classes = [IsUser]

        if self.request.method in ['POST', 'PUT']:
            self.permission_classes = [IsBackOffice]

        return super().get_permissions()

    def update(self, request, *args, **kwargs):
        instance = PersonAccount.objects.get(pk=kwargs['pk'])
        data = request.data

        if instance.user.cpf != data['user'] or instance.digit != data['digit'] or instance.agency != data['agency']:
            return Response(status=400, data={'message': 'Invalid account data'})

        if data['status']:
            if data['status'] not in dict(STATUS).keys():
                return Response(status=400, data={'message': 'Invalid status'})

            instance.status = data['status']

        if data['credit_limit'] and data['credit_limit'] > instance.credit_limit:
            instance.credit_limit = data['credit_limit']

        if data['withdrawal_limit'] and data['withdraw_limit'] > instance.withdraw_limit:
            instance.withdrawal_limit = data['withdraw_limit']

        instance.save()
        return Response(status=204)


class CompanyAccountViewSet(generics.CreateAPIView,
                            generics.UpdateAPIView,
                            generics.RetrieveAPIView,
                            viewsets.ViewSet):
    queryset = CompanyAccount.objects.all()
    http_method_names = ['post', 'put', 'get', 'head']
    serializer_class = CompanyAccountSerializer

    class Meta:
        model = CompanyAccount

    def get_permissions(self):
        self.permission_classes = [IsUserCompany]

        if self.request.method in ['POST', 'PUT']:
            self.permission_classes = [IsBackOfficeCompany]

        return super().get_permissions()

    def update(self, request, *args, **kwargs):
        instance = CompanyAccount.objects.get(pk=kwargs['pk'])
        data = request.data

        if instance.company != data['company'] or instance.digit != data['digit'] or instance.agency != data['agency']:
            return Response(status=400, data={'message': 'Invalid account data'})

        if data['status']:
            if data['status'] not in dict(STATUS).keys():
                return Response(status=400, data={'message': 'Invalid status'})

            instance.status = data['status']

        if data['credit_limit'] and data['credit_limit'] > instance.credit_limit:
            instance.credit_limit = data['credit_limit']

        if data['withdrawal_limit'] and data['withdraw_limit'] > instance.withdraw_limit:
            instance.withdrawal_limit = data['withdraw_limit']

        instance.save()
        return Response(status=204)


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    http_method_names = ['post', 'get', 'delete', 'head']
    serializer_class = PersonAccountSerializer

    class Meta:
        model = PersonAccount

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

    def get_permissions(self):
        self.permission_classes = [IsUser]

        if (self.request.method in ['POST', 'DELETE'] or
                (self.request.method == 'GET' and not bool(self.kwargs))):
            self.permission_classes = [IsBackOffice]

        return super().get_permissions()

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
