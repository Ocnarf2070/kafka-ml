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

class ProducerRabbitMQ:
    def __init__(self, user='admin', password='pass', ip='localhost', port=5672, topic='/', queue='user-tracker'):
        credentials = pika.PlainCredentials(user, password)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(ip, port, topic, credentials))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue)
        None