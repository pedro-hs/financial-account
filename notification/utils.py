import os


def use_local_env():
    return all(bool(os.environ[key]) for key in ['RABBITMQ_USER', 'RABBITMQ_PASSWORD', 'RABBITMQ_QUEUE', 'SYSTEM_EMAIL'])
