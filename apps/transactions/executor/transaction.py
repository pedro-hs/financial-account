import logging
from datetime import date
from uuid import uuid4

from apps.accounts.models import CompanyAccount, PersonAccount
from common.rabbitmq import send_message
from django.forms import model_to_dict

from .entities.company import CompanyEntity
from .entities.person import PersonEntity


class Transaction:
    def __init__(self, account, amount, transaction_type, account_type):
        self.account = account
        self.amount = amount
        self.transaction_type = transaction_type
        self.account_type = account_type
        self.owner = getattr(account, account_type)
        self.load_entity()

    def load_entity(self):
        get_entity = {'user': PersonEntity,
                      'company': CompanyEntity}
        entity = get_entity[self.account_type](self.account)

        self.account_instance = entity.get_account_instance()
        self.email = entity.get_email()
        self.owner_id = entity.get_owner_id()
        self.user_data = entity.get_user_data()
        self.transaction_model = entity.get_transaction_model()

    def execute(self):
        if self.account_instance.status == 'frozen':
            logging.info("%s transaction canceled. Account is frozen and can't execute transactions",
                         self.transaction_type)
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

    def calculate_credit_fees(self, credit_expires):
        today = date.today()

        if credit_expires < today:
            fees = 40
            difference = credit_expires - today
            fees = fees * (1 + 60 / 100) ** (difference.days / 365)

            return fees

        return 0
