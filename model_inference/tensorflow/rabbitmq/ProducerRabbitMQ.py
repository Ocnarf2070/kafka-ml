# credentials = pika.PlainCredentials('admin', 'pass')
# connection = pika.BlockingConnection(pika.ConnectionParameters('localhost',
#                                                                5672,
#                                                                '/',
#                                                                credentials))
# channel = connection.channel()
# channel.queue_declare('user-tracker')
#
# def main():
#     for i in range(10):
#         data = {
#             'user_id': fake.random_int(min=20000, max=100000),
#             'user_name': fake.name(),
#             'user_address': fake.street_address() + ' | ' + fake.city() + ' | '
#             + fake.country_code(),
#             'platform': random.choice(['Mobile', 'Laptop', 'Tablet']),
#             'signup_at': str(fake.date_time_this_month())
#         }
#         m = json.dumps(data)
#         channel.basic_publish(exchange='',
#                               routing_key='user-tracker',
#                               body=m.encode('utf-8'))
#         print('Produced message on topic {} with value of {}\n'.format('user-tracker', m))
#         time.sleep(3)
#
#     connection.close()
#
#
# if __name__ == '__main__':
#     main()

import pika
import json
import time
import logging
import sys
import random
import signal

queue_p = ''


class ProducerRabbitMQ:
    def __init__(self, user='guest', password='guest', ip='localhost', port=5672, topic='/', queue='tensorflow', exchange='tensorflow'):
        global queue_p
        queue_p = queue
        credentials = pika.PlainCredentials(user, password)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(ip, port, topic, credentials,heartbeat=0))
        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange=exchange, exchange_type="direct", passive=False, durable=True,
                                      auto_delete=False)
        self.channel.queue_declare(queue, passive=False, durable=True, auto_delete=False)

        self.channel.queue_bind(queue=queue, exchange=exchange, routing_key="standard_key")

    def basic_publish(self, body, header=None):
        self.channel.basic_publish(exchange='', routing_key=queue_p, body=body, properties=header)
