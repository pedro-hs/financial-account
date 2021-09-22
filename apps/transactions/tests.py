from datetime import timedelta
from unittest import mock

from common.errors import BadRequest
from django.forms import model_to_dict
from django.urls import reverse
from rest_framework import routers
from rest_framework.test import APIClient, APITestCase

from apps.accounts.models import PersonAccount
from apps.transactions.models import PersonTransaction
from apps.transactions.serializers import PersonTransactionSerializer
from apps.users.models import User

from .executor.main import TransactionExecutor

router = routers.DefaultRouter()

client = APIClient()


class TestTransactionExecutor(APITestCase):
    def setUp(self):
        User.objects.create(cpf='23756054611', email='test@mail.com',
                            password='!bF6tVmbXt9dMc#', full_name='Pedro Henrique Santos',
                            role='collaborator')
        user = User.objects.get(cpf='23756054611')
        client.force_authenticate(user=user)

        PersonAccount.objects.create(user=user, number='12345678', digit='1', agency='22',
                                     status='open', credit_limit=100, credit_outlay=0, withdrawal_limit=50, balance=0)

    def execute_and_validate(self, amount, transaction_status, account_status, balance, transaction_type, canceled_reason=None):
        account = PersonAccount.objects.get(number='12345678')
        response = TransactionExecutor(account, amount, transaction_type).process()
        account = PersonAccount.objects.get(number='12345678')
        transaciton = PersonTransaction.objects.get(id=response.id)
        serializer = PersonTransactionSerializer(transaciton)

        assert response.id is not None
        assert response.amount == amount
        assert response.transaction_type == transaction_type
        assert response.status == transaction_status
        assert account.balance == balance
        assert account.status == account_status

        if canceled_reason:
            response.canceled_reason == canceled_reason

        self.assertEqual(model_to_dict(response), model_to_dict(serializer.instance))

    @mock.patch('apps.transactions.executor.transaction.send_message')
    def test_withdrawal_sucess(self, patch):
        PersonAccount.objects.update(balance=40)
        self.execute_and_validate(amount=20, transaction_status='done', account_status='open',
                                  balance=20, transaction_type='withdrawal')

        patch.assert_called()

    @mock.patch('apps.transactions.executor.transaction.send_message')
    def test_withdrawal_error(self, patch):
        PersonAccount.objects.update(balance=60)
        self.execute_and_validate(amount=100, transaction_status='canceled', account_status='open',
                                  balance=60, transaction_type='withdrawal', canceled_reason='insufficient_fund')

        patch.assert_called()

    @mock.patch('apps.transactions.executor.transaction.send_message')
    def test_deposit_sucess(self, patch):
        self.execute_and_validate(amount=40, transaction_status='done', account_status='open',
                                  balance=40, transaction_type='deposit')

        patch.assert_called()

    @mock.patch('apps.transactions.executor.transaction.send_message')
    def test_deposit_error(self, patch):
        PersonAccount.objects.update(balance=60)
        self.execute_and_validate(amount=60, transaction_status='canceled', account_status='open',
                                  balance=60, transaction_type='withdrawal', canceled_reason='limit')

        patch.assert_called()

    def test_error_validations(self):
        account = PersonAccount.objects.get(number='12345678')

        try:
            TransactionExecutor(account, 40, 'invalid').process()
        except BadRequest as error:
            assert error.detail == 'Invalid transaction_type'

        try:
            TransactionExecutor(account, -1, 'deposit').process()
        except BadRequest as error:
            assert error.detail == 'Invalid amount'

    @mock.patch('apps.transactions.executor.transaction.send_message')
    def test_frozen_account(self, patch):
        PersonAccount.objects.update(status='frozen')
        self.execute_and_validate(amount=40, transaction_status='canceled', account_status='frozen',
                                  balance=0, transaction_type='deposit', canceled_reason='frozen')

        patch.assert_called()

    @mock.patch('apps.transactions.executor.transaction.send_message')
    def test_pay_credit_error(self, patch):
        self.execute_and_validate(amount=40, transaction_status='canceled', account_status='open',
                                  balance=0, transaction_type='pay_credit', canceled_reason='no_pay')

        account = PersonAccount.objects.get(number='12345678')
        PersonAccount.objects.update(credit_expires=account.credit_expires - timedelta(days=60), credit_outlay=80)
        self.execute_and_validate(amount=30, transaction_status='canceled', account_status='open',
                                  balance=0, transaction_type='pay_credit', canceled_reason='insufficient_fund')

        PersonAccount.objects.update(credit_expires=account.credit_expires - timedelta(days=35), credit_outlay=60)
        self.execute_and_validate(amount=90, transaction_status='done', account_status='open',
                                  balance=0, transaction_type='pay_credit')
        account = PersonAccount.objects.get(number='12345678')
        assert str(round(account.credit_outlay, 2)) == str(9.74)

        patch.assert_called()

    @mock.patch('apps.transactions.executor.transaction.send_message')
    def test_pay_credit_success(self, patch):
        account = PersonAccount.objects.get(number='12345678')
        PersonAccount.objects.update(credit_expires=account.credit_expires - timedelta(days=30), credit_outlay=30)
        self.execute_and_validate(amount=120, transaction_status='done', account_status='open',
                                  balance=90, transaction_type='pay_credit')

        patch.assert_called()

    @mock.patch('apps.transactions.executor.transaction.send_message')
    def test_use_credit_success(self, patch):
        self.execute_and_validate(amount=30, transaction_status='done', account_status='open',
                                  balance=0, transaction_type='use_credit')

        patch.assert_called()
