import pika
import time
import traceback

import torch
from torch import nn
from torch.optim import optimizer
from torch.utils.data import DataLoader
from torchvision.transforms import ToTensor

from ignite.engine import Engine, Events, create_supervised_trainer, create_supervised_evaluator
from ignite.metrics import *
from ignite.handlers import ModelCheckpoint
from ignite.contrib.handlers import TensorboardLogger, global_step_from_engine
import torchvision.models as models

from decoders import *

output_producer = None
decoder_g = None
model_g = None
device_g = None
commitedMessages = 0

WEIGHTS_PATH='weights.pth'
'''Path of the trained model'''

RETRIES = 10
'''Number of retries for requests'''

SLEEP_BETWEEN_REQUESTS = 5
'''Number of seconds between failed requests'''

MAX_MESSAGES_TO_COMMIT = 16
'''Maximum number of messages to commit at a time'''

class ConsumerRabbitMQ:

    def __init__(self, user='guest', password='guest', ip='localhost', port=5672, topic='/'):
        credentials = pika.PlainCredentials(user, password)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(ip, port, topic, credentials, heartbeat=0))
        self.channel = self.connection.channel()

    def start_consumer(self, queue='pytorch', exchange='pytorch', output=None, decoder=None, model=None, device=None):
        global decoder_g
        global output_producer
        global model_g
        global device_g
        output_producer = output

        decoder_g = decoder
        model_g = model
        device_g = device

        self.channel.exchange_declare(exchange=exchange, exchange_type="direct", passive=False, durable=True,
                                      auto_delete=False)
        self.channel.queue_declare(queue, passive=False, durable=True, auto_delete=False)

        self.channel.queue_bind(queue=queue, exchange=exchange, routing_key="standard_key")

        self.channel.basic_consume(queue, on_message_callback=queue_callback, auto_ack=True)


self.channel.start_consuming()


def queue_callback(channel, method, properties, body):
    global commitedMessages
    if output_producer is None or decoder_g is None or model_g is None:
        raise Exception("Some values are empty")

    try:
        start_inference = time.time()

        logging.debug("Message received for prediction")

        input_decoded = decoder_g.decode(body)
        """Decodes the message received"""

        #logging.debug("Message received: "+str(input_decoded))

        if input_decoded.shape[0] == 1 and len(input_decoded.shape) == 4:
          input_decoded = input_decoded[0]
        """Outwrapping the input data"""

        tensored_input = ToTensor()(input_decoded)

        tensored_input = torch.unsqueeze(tensored_input, 0)

        tensored_input = tensored_input.to(device_g)

        prediction_output = model_g(tensored_input)
        """Predicts the data received"""

        print(prediction_output) if DEBUG else None

        prediction_value = prediction_output.tolist()[0]
        """Gets the prediction value"""

        logging.debug("Prediction done: %s", str(prediction_value))

        response = {
          'values': prediction_value
        }
        """Creates the object response"""

        response_to_kafka = json.dumps(response).encode()
        """Encodes the object response"""

        output_producer.basic_publish(response_to_kafka)
        """Sends the message to RabbitMQ"""

        logging.debug("Prediction sent to RabbitMQ")

        # commitedMessages += 1
        # if commitedMessages >= MAX_MESSAGES_TO_COMMIT:
        #   consumer.commit()
        #   commitedMessages = 0
        #   """Commits the message to Kafka"""
        #   logging.debug("Commited messages to RabbitMQ")

        end_inference = time.time()
        logging.debug("Total inference time: %s", str(end_inference - start_inference))

    except Exception as e:
        traceback.print_exc()
        logging.error("Error with the received data [%s]. Waiting for new a new prediction.", str(e))