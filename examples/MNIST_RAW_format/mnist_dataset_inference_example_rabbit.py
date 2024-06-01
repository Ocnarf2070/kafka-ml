import pika
import tensorflow as tf
import logging
import sys
import signal

logging.basicConfig(level=logging.INFO)

INPUT_TOPIC = 'in_topic'
OUTPUT_TOPIC = 'out_topic'
BOOTSTRAP_SERVERS= '127.0.0.1:30672'
(HOST, PORT) = BOOTSTRAP_SERVERS.split(':')
ITEMS_TO_PREDICT = 10

(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
print("Datasize minst: ", x_test.shape)

credentials=pika.PlainCredentials('guest','guest')
connection = pika.BlockingConnection(pika.ConnectionParameters(HOST,
                                                               int(PORT),
                                                               '/',
                                                               credentials))
channel = connection.channel()

connection_in = pika.BlockingConnection(pika.ConnectionParameters(HOST,
                                                                  int(PORT),
                                                                  '/',
                                                                  credentials))
channel_in = connection.channel()
channel_in.queue_declare(INPUT_TOPIC)


#########################
def queue_callback(channel, method, properties, body):
  if len(method.exchange):
    print("from exchange '{}': {}".format(method.exchange,
                                          body.decode()))
  else:
    print("from queue {}: {}".format(method.routing_key,
                                     body.decode('UTF-8')))


def signal_handler(signal, frame):
  print("\nCTRL-C handler, cleaning up rabbitmq connection and quitting")
  connection.close()
  sys.exit(0)

#######################

for i in range (0, ITEMS_TO_PREDICT):
  channel_in.basic_publish(exchange='',routing_key=INPUT_TOPIC,body=x_test[i].tobytes())
  """Sends the value to predict to RabbitMQ"""

channel.basic_consume(queue=OUTPUT_TOPIC,
                          on_message_callback=queue_callback, auto_ack=True)
# capture CTRL-C
signal.signal(signal.SIGINT, signal_handler)

print("Waiting for messages, CTRL-C to quit...")
print("")
print('\n')


