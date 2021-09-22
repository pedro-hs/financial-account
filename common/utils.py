import os

from django.core.validators import RegexValidator
from dotenv import find_dotenv, load_dotenv

IS_NUMERIC = RegexValidator(r'^[0-9+]', 'Only numeric characters.')


def generate_choices(data):
    return [(item, item) for item in data]


def load_env():
    if not os.environ.get('SECRET_KEY'):
        load_dotenv(find_dotenv())
