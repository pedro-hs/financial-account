import json

from accounts.models import CompanyAccount, PersonAccount
from common.errors import BadRequest
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.response import Response

from .executor import TransactionExecutor
from .models import CompanyTransaction, PersonTransaction
from .serializers import (CompanyTransactionSerializer, ListCompanyTransactionSerializer,
                          ListPersonTransactionSerializer, PersonTransactionSerializer)


class ListCompanyTransactionsViewSet(generics.ListAPIView, viewsets.ViewSet):
    queryset = CompanyTransaction.objects.all()
    http_method_names = ['get', 'head']
    serializer_class = CompanyTransactionSerializer

    class Meta:
        model = ListCompanyTransactionSerializer


class ListPersonTransactionsViewSet(generics.ListAPIView, viewsets.ViewSet):
    queryset = PersonTransaction.objects.all()
    http_method_names = ['get', 'head']
    serializer_class = ListPersonTransactionSerializer

    class Meta:
        model = PersonTransaction


class CreateTransaction(generics.CreateAPIView, viewsets.ViewSet):
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


class CreateCompanyTransactionViewSet(CreateTransaction):
    queryset = CompanyTransaction.objects.all()
    http_method_names = ['post', 'head']
    serializer_class = CompanyTransactionSerializer

    class Meta:
        model = CompanyTransaction

    def has_valid_owner_id(self, account, owner_id):
        return account.company.cnpj == owner_id

    def query_account(self, number):
        return get_object_or_404(CompanyAccount, pk=number)


class CreatePersonTransactionViewSet(CreateTransaction):
    queryset = PersonTransaction.objects.all()
    http_method_names = ['post', 'head']
    serializer_class = PersonTransactionSerializer

    class Meta:
        model = PersonTransaction

    def has_valid_owner_id(self, account, owner_id):
        return account.user.cpf == owner_id

    def query_account(self, number):
        return get_object_or_404(PersonAccount, pk=number)
