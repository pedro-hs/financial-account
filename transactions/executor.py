import logging
from datetime import timedelta
from uuid import uuid4

from accounts.constants import ACCOUNT_TYPES
from accounts.models import CompanyAccount, PersonAccount
from common.errors import BadRequest
from common.rabbitmq import send_message
from django.forms import model_to_dict

from .constants import CANCELED_REASONS, TRANSACTION_STATUS, TRANSACTION_TYPES
from .models import CompanyTransaction, PersonTransaction


class Transaction:

    def __init__(self, account, amount, transaction_type, account_type):
        self.account = account
        self.amount = amount
        self.transaction_type = transaction_type
        self.account_type = account_type
        self.load_data()

    def load_data(self):
        get_instance = {'user': PersonAccount.objects.filter(pk=self.account.number).first(),
                        'company': CompanyAccount.objects.filter(pk=self.account.number).first()}
        self.account_instance = get_instance[self.account_type]

        get_email = {'user': (self.account_instance.user.email
                              if hasattr(self.account_instance, 'user') else None),
                     'company': (self.account_instance.company.user.email
                                 if hasattr(self.account_instance, 'company') else None)}
        self.email = get_email[self.account_type]

        get_owner_id = {'user': (self.account_instance.user.cpf
                                 if hasattr(self.account_instance, 'user') else None),
                        'company': (self.account_instance.company.cnpj
                                    if hasattr(self.account_instance, 'company') else None)}
        self.owner_id = get_owner_id[self.account_type]

        get_user = {'user': (self.account_instance.user
                             if hasattr(self.account_instance, 'user') else None),
                    'company': (self.account_instance.company
                                if hasattr(self.account_instance, 'company') else None)}
        self.user_data = get_user[self.account_type]

        get_model = {'user': PersonTransaction,
                     'company': CompanyTransaction}
        self.transaction_model = get_model[self.account_type]

        self.owner = getattr(self.account, self.account_type)

    def execute(self):
        if self.account_instance.status == 'frozen':
            logging.info("%s transaction canceled. Account is frozen and can't execute transactions", self.transaction_type)
            return self.create({'status': 'canceled',
                                'transaction_type': self.transaction_type,
                                'canceled_reason': 'frozen',
                                'note': "Account is frozen and can't execute transactions",
                                'amount': self.amount})

        return self.process()

    def create(self, transaction_data):
        transaction_data = {**transaction_data,
                            'id': str(uuid4()),
                            'account': self.account}
        new_transaction = self.transaction_model.objects.create(**transaction_data)

        if transaction_data['status'] != 'canceled':
            self.account_instance.save()

        message = {'transaction': model_to_dict(new_transaction),
                   'account': {**model_to_dict(self.account),
                               'owner_id': self.owner_id},
                   'email_type': 'transaction'}
        send_message(message_type='send_email', to=self.email, message=message)

        return new_transaction


class DepositTransaction(Transaction):
    def process(self):
        self.account_instance.balance = self.account_instance.balance + self.amount

        logging.info('Deposit transaction done')
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
            logging.info('WithDrawal transaction canceled. Fund is lower than balance')
            return self.create({**transaction_canceled_data,
                                'canceled_reason': 'insufficient_fund',
                                'note': 'Fund is lower than balance'})

        if self.amount > self.account_instance.withdrawal_limit:
            logging.info('WithDrawal transaction canceled. Limit of withdrawal achieved')
            return self.create({**transaction_canceled_data,
                                'canceled_reason': 'limit',
                                'note': 'Limit of withdrawal achieved'})

        self.account_instance.balance = balance - self.amount

        logging.info('WithDrawal transaction done')
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
            logging.info('BuyCredit transaction canceled. Is need to pay the credit outlay and fees in order to use credit again')
            return self.create({**transaction_canceled_data,
                                'canceled_reason': 'debitor',
                                'note': 'Is need to pay the credit outlay and fees in order to use credit again'})

        if (credit_outlay + self.amount) > self.account_instance.credit_limit:
            logging.info('BuyCredit transaction canceled. Limit of credit achieved')
            return self.create({**transaction_canceled_data,
                                'canceled_reason': 'limit',
                                'note': 'Limit of credit achieved'})

        self.account_instance.credit_outlay = + self.amount

        logging.info('BuyCredit transaction done')
        return self.create({'status': 'done',
                            'transaction_type': self.transaction_type,
                            'amount': self.amount})


class PayCreditTransaction(Transaction):
    def __init__(self, account, amount, transaction_type, account_type):
        super().__init__(account, amount, transaction_type, account_type)
        self.balance = self.account_instance.balance
        self.credit_outlay = self.account_instance.credit_outlay
        self.credit_fees = self.account_instance.credit_fees
        self.credit_expires = self.account_instance.credit_expires

    def process(self):
        if not self.credit_outlay and not self.credit_fees:
            logging.info('PayCredit transaction canceled. Nothing to pay')
            return self.create({'status': 'canceled',
                                'canceled_reason': 'no_pay',
                                'note': 'Nothing to pay',
                                'transaction_type': self.transaction_type,
                                'amount': self.amount})

        if self.credit_fees:
            self.pay_credit_fees(self.amount)

        else:
            self.pay_credit_outlay(self.amount)

        if not self.account_instance.credit_outlay:
            self.account_instance.credit_expires = self.credit_expires + timedelta(days=30)

        logging.info('PayCredit transaction done')
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
        self.account_type = self.get_account_type()
        self.amount = amount

        logging.info('Processing %s transaction for %s', transaction_type, self.account_type)

    def process(self):
        self.validate_data()
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

    def get_account_type(self):
        transaction_type_index = self.account_type_status.index(True)
        return ACCOUNT_TYPES[transaction_type_index]

    def execute_transaction(self):
        return TRANSACTIONS[self.transaction_type](self.account, self.amount, self.transaction_type, self.account_type).execute()
