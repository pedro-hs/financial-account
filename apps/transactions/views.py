import json

from common.errors import BadRequest
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.response import Response

from apps.accounts.models import CompanyAccount, PersonAccount

from .executor.main import TransactionExecutor
from .models import CompanyTransaction, PersonTransaction
from .serializers import (CompanyTransactionSerializer, ListCompanyTransactionSerializer,
                          ListPersonTransactionSerializer, PersonTransactionSerializer)


class BaseTransactionViewSet(generics.CreateAPIView, generics.ListAPIView, viewsets.ViewSet):
    class Meta:
        abstract = True

    def create(self, request, *args, **kwargs):
        data = request.data
        amount = data['amount']
        transaction_type = data['transaction_type']
        account = self.get_acount(request.data)

        transaction_data = TransactionExecutor(account, amount, transaction_type).process()
        transaction_data = model_to_dict(transaction_data)

        return Response(transaction_data, status=201)

    def get_acount(self, data):
        number = data['number']
        digit = data['digit']
        agency = data['agency']
        owner_id = data['owner_id']

        account = self.query_account(int(number))

        if not account:
            raise BadRequest('Invalid account')

        if not self.has_valid_owner_id(account, owner_id) or account.digit != digit or account.agency != agency:
            raise BadRequest('Invalid account')

        return account


class CreateCompanyTransactionViewSet(BaseTransactionViewSet):
    queryset = CompanyTransaction.objects.all()
    http_method_names = ['get', 'post', 'head']
    serializer_class = CompanyTransactionSerializer

    class Meta:
        model = CompanyTransaction

    def has_valid_owner_id(self, account, owner_id):
        return account.company.cnpj == owner_id

    def query_account(self, number):
        return get_object_or_404(CompanyAccount, pk=number)

    def get_serializer_class(self):
        get_serializer = {'list': ListCompanyTransactionSerializer,
                          'create': CompanyTransactionSerializer}
        return get_serializer.get(self.action, CompanyTransactionSerializer)


class CreatePersonTransactionViewSet(BaseTransactionViewSet):
    queryset = PersonTransaction.objects.all()
    http_method_names = ['get', 'post', 'head']
    serializer_class = PersonTransactionSerializer

    class Meta:
        model = PersonTransaction

    def has_valid_owner_id(self, account, owner_id):
        return account.user.cpf == owner_id

    def query_account(self, number):
        return get_object_or_404(PersonAccount, pk=number)

    def get_serializer_class(self):
        get_serializer = {'list': ListPersonTransactionSerializer,
                          'create': PersonTransactionSerializer}
        return get_serializer.get(self.action, PersonTransactionSerializer)
