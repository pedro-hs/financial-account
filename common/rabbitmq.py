import os
from json import dumps, loads

import pika
from django.core.serializers.json import DjangoJSONEncoder
from dotenv import find_dotenv, load_dotenv

from common.utils import load_env


def send_message(**kwargs):
    load_env()

    credentials = pika.PlainCredentials(os.environ['RABBITMQ_USER'], os.environ['RABBITMQ_PASSWORD'])
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.environ['RABBITMQ_HOST'], port=os.environ['RABBITMQ_PORT'],
                                                                   credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue=os.environ['RABBITMQ_QUEUE'])
    channel.basic_publish(exchange='', routing_key=os.environ['RABBITMQ_QUEUE'],
                          body=dumps({**kwargs}, cls=DjangoJSONEncoder))
    connection.close()
