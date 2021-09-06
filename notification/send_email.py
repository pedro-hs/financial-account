import os
import smtplib

from dotenv import find_dotenv, load_dotenv


def use_local_env():
    env_variables = ['RABBITMQ_USER', 'RABBITMQ_PASSWORD', 'RABBITMQ_QUEUE', 'SYSTEM_EMAIL']
    return all(bool(os.environ[key]) for key in env_variables)


if use_local_env():
    load_dotenv(find_dotenv())


def send_email(message, to):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(os.environ['SYSTEM_EMAIL'], os.environ['SYSTEM_EMAIL_PASSWORD'])
    server.sendmail(os.environ['SYSTEM_EMAIL'], to, message.encode('utf-8'))
