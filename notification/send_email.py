import os
import smtplib

from dotenv import find_dotenv, load_dotenv

from utils import use_local_env


def use_local_env():
    return all(bool(os.environ[key]) for key in ['RABBITMQ_USER', 'RABBITMQ_PASSWORD', 'RABBITMQ_QUEUE', 'SYSTEM_EMAIL'])


if use_local_env():
    load_dotenv(find_dotenv())


def send_email(message, to):
    email_type = message.pop('email_type')
    get_formatter = {'transaction': format_transaction}
    formatted_message = get_formatter[email_type](message)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(os.environ['SYSTEM_EMAIL'], os.environ['SYSTEM_EMAIL_PASSWORD'])
    server.sendmail(os.environ['SYSTEM_EMAIL'], to, formatted_message.encode('utf-8'))


def format_transaction(data):
    owner_id = data['account']['owner_id']
    transaction_type = data['transaction']['transaction_type']
    transaction_status = data['transaction']['status']
    transaction_description = data['transaction']['note']
    account_number = data['account']['number']
    account_digit = data['account']['digit']
    account_agency = data['account']['agency']

    message = (f'Subject: Transação executada\n'
               f'A conta {account_number}-{account_digit} da agência {account_agency} do cliente {owner_id}\n')

    if transaction_status and transaction_status == 'canceled':
        message += f'Teve uma transação cancelada pelo motivo: {transaction_description}'

    else:
        description_message = {'deposit': 'Recebeu um deposito',
                               'withdrawal': 'Fez um saque',
                               'buy_credit': 'Gastou crédito',
                               'pay_credit': 'Quitou o crédito'}
        message += description_message[transaction_type]

    return message
