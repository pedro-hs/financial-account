from common.errors import BadRequest
from common.permissions import IsBackOffice, IsUser, IsUserCompany
from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .constants import ACCOUNT_STATUS
from .models import Company, CompanyAccount, PersonAccount
from .serializers import (DefaultCompanyAccountSerializer, DefaultPersonAccountSerializer,
                          PostCompanyAccountSerializer, PostPersonAccountSerializer)


class BaseAccountViewSet(generics.CreateAPIView,
                         generics.UpdateAPIView,
                         generics.RetrieveAPIView,
                         viewsets.ViewSet):
    class Meta:
        abstract = True

    def update(self, request, *args, **kwargs):
        instance = get_object_or_404(self.Meta.model, pk=kwargs['pk'])
        data = request.data

        if data.get('status'):
            if data['status'] not in ACCOUNT_STATUS:
                raise BadRequest('Invalid status')

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
            self.permission_classes = [IsBackOffice]

        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return PostCompanyAccountSerializer

        return DefaultCompanyAccountSerializer
