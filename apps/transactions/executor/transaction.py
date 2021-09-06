import logging
from datetime import date
from uuid import uuid4

from common.rabbitmq import send_message
from django.forms import model_to_dict

from .entities.company import CompanyEntity
from .entities.person import PersonEntity

EMAIL_DESCRIPTION_MESSAGE = {'deposit': 'Recebeu um deposito',
                             'withdrawal': 'Fez um saque',
                             'use_credit': 'Gastou o crédito',
                             'pay_credit': 'Pagou o crédito'}


def format_email(transaction, account):
    transaction_type = transaction['transaction_type']
    transaction_status = transaction['status']
    transaction_description = transaction['note']

    owner_id = account['owner_id']
    account_number = account['number']
    account_digit = account['digit']
    account_agency = account['agency']

    message = (f'Subject: Transação executada\n'
               f'A conta {account_number}-{account_digit} da agência {account_agency} do cliente {owner_id}\n')

    if transaction_status and transaction_status == 'canceled':
        message += f'Teve uma transação cancelada pelo motivo: {transaction_description}'

    else:
        message += EMAIL_DESCRIPTION_MESSAGE[transaction_type]

    return message


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
            return self.create('canceled', self.amount, canceled_reason='frozen',
                               note="Account is frozen and can't execute transactions")

        return self.process()

    def create(self, status, amount, canceled_reason=None, note=None):
        transaction_data = {'transaction_type': self.transaction_type,
                            'id': str(uuid4()),
                            'account': self.account,
                            'status': status,
                            'amount': amount}

        for field, field_name in [(canceled_reason, 'canceled_reason'),
                                  (note, 'note')]:
            if field:
                transaction_data[field_name] = field

        new_transaction = self.transaction_model.objects.create(**transaction_data)

        if transaction_data['status'] != 'canceled':
            self.account_instance.save()

        self.notify(new_transaction)

        return new_transaction

    def notify(self, transaction):
        transaction_data = model_to_dict(transaction)
        account_data = {**model_to_dict(self.account),
                        'owner_id': self.owner_id}
        email_message = format_email(transaction_data, account_data)
        send_message(message_type='send_email', to=self.email, message=email_message)

    def calculate_credit_fees(self, credit_expires):
        today = date.today()

        if credit_expires < today:
            fees = 40
            difference = credit_expires - today
            fees = fees * (1 + 60 / 100) ** (difference.days / 365)

            return fees

        return 0
