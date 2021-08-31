import os


def generate_choices(data):
    return[(item, item) for item in data]


def use_local_env():
    return not os.environ.get('SECRET_KEY')
