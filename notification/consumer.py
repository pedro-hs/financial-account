#!/usr/bin/env python
import os
import sys
from json import loads

import pika

from send_email import send_email

MESSAGE_TYPES = {'send_email': send_email}


def callback(ch, method, properties, body):
    data = loads(body)
    message_type = data.pop('message_type')
    process = MESSAGE_TYPES[message_type]
    process(**data)


def get_connection():
    credentials = pika.PlainCredentials(os.environ['RABBITMQ_USER'], os.environ['RABBITMQ_PASSWORD'])
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.environ['RABBITMQ_HOST'], port=os.environ['RABBITMQ_PORT'],
                                                                   credentials=credentials))

    return connection


def main():
    channel = get_connection().channel()
    channel.queue_declare(queue=os.environ['RABBITMQ_QUEUE'])
    channel.basic_consume(queue=os.environ['RABBITMQ_QUEUE'], on_message_callback=callback, auto_ack=True)

    print('# NOTIFICATION: Waiting for messages...')
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
