from uuid import uuid4

from accounts.models import CompanyAccount, PersonAccount
from common.errors import BadRequest

from .constants import CANCELED_REASONS, TRANSACTION_STATUS, TRANSACTION_TYPES
from .models import CompanyTransaction, PersonTransaction


class Transaction:
    def __init__(self, account, amount, transaction_type):
        self.account = account
        is_company = not hasattr(self.account, 'user')
        self.owner = self.account.company if is_company else self.account.user
        self.owner_id = self.account.company.cnpj if is_company else self.account.user.cpf
        self.account_instance = (CompanyAccount().objects.get(self.account.number)
                                 if is_company else PersonAccount().objects.get(self.account.number))
        self.transaction_instance = CompanyTransaction() if is_company else PersonTransaction()
        self.owner_type = 'company' if is_company else 'user'

        if self.account_instance.status == 'frozen':
            transaction_data = {'status': 'canceled',
                                'transaction_type': transaction_type,
                                'canceled_reason': 'frozen',
                                'note': "Account is frozen and can't execute transactions",
                                'amount': amount}
            self.create(transaction_data)

    def create(self, transaction_data):
        if transaction_data.get('status') not in TRANSACTION_STATUS:
            transaction_data = {**transaction_data,
                                'status': 'canceled',
                                'canceled_reason': 'invalid_enum',
                                'note': 'Provided status is invalid'}

        if transaction_data.get('canceled_reason') not in CANCELED_REASONS:
            transaction_data = {**transaction_data,
                                'status': 'canceled',
                                'canceled_reason': 'invalid_enum',
                                'note': 'Provided canceled reason is invalid'}

        transaction = {**transaction_data,
                       self.owner_type: self.owner}
        self.transaction_instance.objects.create(**transaction)
        self.account_instance.save()


class DepositTransaction(Transaction):
    def __call__(self, account, amount):
        transaction_type = 'deposit'

        super().__init__(account, amount, transaction_type)
        balance = self.account_instance.balance
        balance = balance + amount

        self.create({'status': 'done',
                     'transaction_type': transaction_type,
                     'amount': amount})


class WithDrawalTransaction(Transaction):
    def __call__(self, account, amount):
        transaction_type = 'withdrawal'

        super().__init__(account, amount, transaction_type)
        balance = self.account_instance.balance
        withdrawal_limit = self.account_instance.balance

        transaction_canceled_data = {'status': 'canceled',
                                     'transaction_type': transaction_type,
                                     'amount': amount}

        if amount > balance:
            self.create({**transaction_canceled_data,
                         'canceled_reason': 'insufficient_fund',
                         'note': 'Fund is lower than balance'})

        if amount > withdrawal_limit:
            self.create({**transaction_canceled_data,
                         'canceled_reason': 'limit',
                         'note': 'Limit of withdrawal achieved'})

        self.account_instance.balance = self.account_instance.balance - amount

        self.create({'status': 'done',
                     'transaction_type': transaction_type,
                     'amount': amount})


class BuyCreditTransaction(Transaction):
    def __call__(self, account, amount):
        transaction_type = 'buy_credit'

        super().__init__(account, amount, transaction_type)
        credit_limit = self.account_instance.balance
        credit_outlay = self.account_instance.credit_outlay
        credit_fees = self.account_instance.credit_fees

        transaction_canceled_data = {'status': 'canceled',
                                     'transaction_type': transaction_type,
                                     'amount': amount}

        if credit_fees:
            self.create({**transaction_canceled_data,
                         'canceled_reason': 'debitor',
                         'note': 'Is need to pay the credit outlay and fees in order to use credit again'})

        if (credit_outlay + amount) > credit_limit:
            self.create({**transaction_canceled_data,
                         'canceled_reason': 'limit',
                         'note': 'Limit of credit achieved'})

        credit_outlay = + amount

        self.create({'status': 'done',
                     'transaction_type': transaction_type,
                     'amount': amount})


class PayCreditTransaction(Transaction):
    def __call__(self, account, amount):
        transaction_type = 'pay_credit'

        super().__init__(account, amount, transaction_type)
        self.balance = self.account_instance.balance
        self.credit_outlay = self.account_instance.credit_outlay
        self.credit_fees = self.account_instance.credit_fees
        self.credit_expires = self.account_instance.credit_fees

        if self.credit_fees:
            self.pay_credit_fees(amount)

        else:
            self.pay_credit_outlay(amount)

        self.create({'status': 'done',
                     'transaction_type': transaction_type,
                     'amount': amount})

        def pay_credit_outlay(self, amount):
            if amount >= self.credit_outlay:
                chargeback = amount - self.credit_outlay
                self.credit_outlay = 0

                if chargeback:
                    self.balance = self.balance + chargeback

            if amount < self.credit_outlay:
                self.credit_outlay = self.credit_outlay - amount

        def pay_credit_fees(self, amount):
            if amount >= self.credit_fees:
                remaining = amount - self.credit_fees
                self.credit_fees = 0

                if remaining:
                    self.pay_credit_outlay(remaining)

            if amount < self.credit_fees:
                self.credit_fees = self.credit_fees - amount


TRANSACTIONS = {'deposit': DepositTransaction,
                'withdrawal': WithDrawalTransaction,
                'buy_credit': BuyCreditTransaction,
                'pay_credit': PayCreditTransaction}


class TransactionExecutor:
    def __call__(self, transaction_type, amount, account):
        self.transaction_type = transaction_type
        self.account = account
        self.validate_data()

        self.execute_transaction(account, amount)

    def validate_data(self):
        if self.transaction_type not in TRANSACTION_TYPES:
            raise BadRequest('Invalid transaction_type')

        if hasattr(self.account, 'user') and hasattr(self.account, 'company'):
            raise BadRequest("Account can't have CPF and CNPJ")

        if not hasattr(self.account, 'user') and not hasattr(self.account, 'company'):
            raise BadRequest('Account need to have an owner')

    def execute_transaction(self, account, amount):
        return TRANSACTIONS[self.transaction_type](account, amount)
