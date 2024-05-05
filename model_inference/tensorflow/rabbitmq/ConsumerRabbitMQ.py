import pika

def queue_callback(channel, method, properties, body):
     if len(method.exchange):
         print("from exchange '{}': {}".format(method.exchange,
                                               body.decode('UTF-8')))
     else:
         print("from queue {}: {}".format(method.routing_key,
                                          body.decode('UTF-8')))

class ConsumerRabbitMQ:
    def __init__(self, user='admin', password='pass', ip='localhost', port=5672, topic='/'):
        credentials = pika.PlainCredentials(user, password)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(ip, port, topic, credentials))
        self.channel = self.connection.channel()

    def start_consumer(self, queue='user-tracker'):
        self.channel.basic_consume(queue, on_message_callback=queue_callback, auto_ack=True)
        self.channel.start_consuming()

