#!/usr/bin/env python

import pika


def callback(ch, method, properties, body):
    print(" [x] Received %r" % (body,))

connection = pika.BlockingConnection(pika.ConnectionParameters('127.0.0.1', port=18888,
                                                 credentials=pika.PlainCredentials('admin', 'admin')))

channel = connection.channel()
channel.queue_declare(queue='hello')

print(" [*] Waiting for messages...")

channel.basic_consume(callback, queue='hello', no_ack=True)

channel.start_consuming()
