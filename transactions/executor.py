import logging
from datetime import timedelta
from uuid import uuid4

from accounts.constants import ACCOUNT_TYPES
from accounts.models import CompanyAccount, PersonAccount
from common.errors import BadRequest

from .constants import CANCELED_REASONS, TRANSACTION_STATUS, TRANSACTION_TYPES
from .models import CompanyTransaction, PersonTransaction


class Transaction:

    def __init__(self, account, amount, transaction_type, account_type):
        self.account = account
        self.amount = amount
        self.transaction_type = transaction_type
        self.account_type = account_type

        get_instance = {'user': PersonAccount.objects.filter(pk=self.account.number).first(),
                        'company': CompanyAccount.objects.filter(pk=self.account.number).first()}
        get_model = {'user': PersonTransaction,
                     'company': CompanyTransaction}

        self.owner = getattr(self.account, self.account_type)
        self.account_instance = get_instance[account_type]

        get_owner_id = {'user': (self.account_instance.user.cpf
                                 if hasattr(self.account_instance, 'user') else None),
                        'company': (self.account_instance.company.cnpj
                                    if hasattr(self.account_instance, 'company') else None)}

        self.owner_id = get_owner_id[account_type]
        self.transaction_model = get_model[account_type]

    def execute(self):
        transaction_data = self.pre_validate()

        if transaction_data['status'] != 'canceled':
            transaction_data = self.process()
            transaction_data = self.pos_validate(transaction_data)

        return self.create(transaction_data)

    def pre_validate(self):
        if self.account_instance.status == 'frozen':
            return {'status': 'canceled',
                    'transaction_type': self.transaction_type,
                    'canceled_reason': 'frozen',
                    'note': "Account is frozen and can't execute transactions",
                    'amount': self.amount}

    def pos_validate(self, transaction_data):
        if transaction_data.get('status') not in TRANSACTION_STATUS:
            return {**transaction_data,
                    'status': 'canceled',
                    'canceled_reason': 'invalid_enum',
                    'note': 'Provided status is invalid'}

        if transaction_data.get('canceled_reason') and transaction_data.get('canceled_reason') not in CANCELED_REASONS:
            return {**transaction_data,
                    'status': 'canceled',
                    'canceled_reason': 'invalid_enum',
                    'note': 'Provided canceled reason is invalid'}

        return transaction_data

    def create(self, transaction_data):
        transaction_data = {**transaction_data,
                            'account': self.account}
        new_transaction = self.transaction_model.objects.create(**transaction_data)

        if transaction_data['status'] != 'canceled':
            self.account_instance.save()

        return new_transaction


class DepositTransaction(Transaction):
    def process(self):
        self.account_instance.balance = self.account_instance.balance + self.amount

        return self.create({'status': 'done',
                            'transaction_type': self.transaction_type,
                            'amount': self.amount})


class WithDrawalTransaction(Transaction):
    def process(self):
        balance = self.account_instance.balance

        transaction_canceled_data = {'status': 'canceled',
                                     'transaction_type': self.transaction_type,
                                     'amount': self.amount}

        if self.amount > balance:
            return self.create({**transaction_canceled_data,
                                'canceled_reason': 'insufficient_fund',
                                'note': 'Fund is lower than balance'})

        if self.amount > self.account_instance.withdrawal_limit:
            return self.create({**transaction_canceled_data,
                                'canceled_reason': 'limit',
                                'note': 'Limit of withdrawal achieved'})

        self.account_instance.balance = balance - self.amount

        return self.create({'status': 'done',
                            'transaction_type': self.transaction_type,
                            'amount': self.amount})


class BuyCreditTransaction(Transaction):
    def process(self):
        credit_outlay = self.account_instance.credit_outlay

        transaction_canceled_data = {'status': 'canceled',
                                     'transaction_type': self.transaction_type,
                                     'amount': self.amount}

        if self.account_instance.credit_fees:
            return self.create({**transaction_canceled_data,
                                'canceled_reason': 'debitor',
                                'note': 'Is need to pay the credit outlay and fees in order to use credit again'})

        if (credit_outlay + self.amount) > self.account_instance.credit_limit:
            return self.create({**transaction_canceled_data,
                                'canceled_reason': 'limit',
                                'note': 'Limit of credit achieved'})

        self.account_instance.credit_outlay = + self.amount

        return self.create({'status': 'done',
                            'transaction_type': self.transaction_type,
                            'amount': self.amount})


class PayCreditTransaction(Transaction):
    def __init__(self, account, amount, transaction_type):
        super().__init__(account, amount, transaction_type)
        self.balance = self.account_instance.balance
        self.credit_outlay = self.account_instance.credit_outlay
        self.credit_fees = self.account_instance.credit_fees
        self.credit_expires = self.account_instance.credit_expires

    def process(self):
        if not self.credit_outlay and not self.credit_fees:
            return self.create({'status': 'canceled',
                                'canceled_reason': 'no_pay',
                                'note': 'Nothing to pay',
                                'transaction_type': self.transaction_type,
                                'amount': self.amount})

        if self.credit_fees:
            self.pay_credit_fees(self.amount)

        else:
            self.pay_credit_outlay(self.amount)

        if not self.credit_outlay:
            self.account_instance.credit_expires = self.credit_expires + timedelta(days=30)

        return self.create({'status': 'done',
                            'transaction_type': self.transaction_type,
                            'amount': self.amount})

    def pay_credit_outlay(self, amount):
        if amount >= self.credit_outlay:
            chargeback = amount - self.credit_outlay
            self.account_instance.credit_outlay = 0

            if chargeback:
                self.account_instance.balance = self.balance + chargeback

        if amount < self.credit_outlay:
            self.account_instance.credit_outlay = self.credit_outlay - amount

    def pay_credit_fees(self, amount):
        if amount >= self.credit_fees:
            remaining = amount - self.credit_fees
            self.account_instance.credit_fees = 0

            if remaining:
                self.pay_credit_outlay(remaining)

        if amount < self.credit_fees:
            self.account_instance.credit_fees = self.credit_fees - amount


TRANSACTIONS = {'deposit': DepositTransaction,
                'withdrawal': WithDrawalTransaction,
                'buy_credit': BuyCreditTransaction,
                'pay_credit': PayCreditTransaction}


class TransactionExecutor:
    def __init__(self, account, amount, transaction_type):
        self.transaction_type = transaction_type
        self.account = account
        self.account_type_status = [hasattr(self.account, account_type)
                                    for account_type in ACCOUNT_TYPES]
        self.amount = amount

    def process(self):
        self.validate_data()
        self.set_account_type()
        return self.execute_transaction()

    def validate_data(self):
        if self.transaction_type not in TRANSACTION_TYPES:
            raise BadRequest('Invalid transaction_type')

        if self.amount < 1 or not str(self.amount).isnumeric():
            raise BadRequest('Invalid amount')

        account_owners = self.account_type_status.count(True)

        if account_owners > 1:
            raise BadRequest("Invalid account. Account can't have more than one owner")

        elif account_owners < 1:
            raise BadRequest('Invalid account. Account need to have an owner')

    def set_account_type(self):
        transaction_type_index = self.account_type_status.index(True)
        account_type = ACCOUNT_TYPES[transaction_type_index]
        self.account_type = account_type

    def execute_transaction(self):
        return TRANSACTIONS[self.transaction_type](self.account, self.amount, self.transaction_type, self.account_type).execute()
