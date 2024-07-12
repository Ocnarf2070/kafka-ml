import pika
import time
import traceback
import numpy as np
import tensorflow as tf
import logging
import sys
import json

output_producer = None
upper_producer=None
distributed_g=False
limit_g=0
decoder_g = None
model_g = None
commitedMessages = 0
DEBUG=False

MODEL_PATH='model.h5'
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
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(ip, port, topic, credentials))
        self.channel = self.connection.channel()

    def start_consumer(self, queue='pytorch', output=None, decoder=None, model=None, device=None, distributed=False,
                       limit=10000, upper=None):
        global decoder_g
        global output_producer
        global model_g
        global distributed_g
        global limit_g
        global upper_producer
        output_producer = output
        upper_producer = upper
        decoder_g = decoder
        model_g = model
        distributed_g = distributed
        limit_g = limit
        self.channel.queue_declare(queue, passive=False, durable=True, auto_delete=False)
        self.channel.basic_consume(queue, on_message_callback=queue_callback, auto_ack=True)
        self.channel.start_consuming()


def queue_callback(channel, method, properties, body):
    global commitedMessages
    global distributed_g
    distributed = distributed_g
    if output_producer is None or decoder_g is None or model_g is None:
        raise Exception("Some values are empty")

    try:
        start_inference = time.time()

        logging.debug("Message received for prediction")

        input_decoded = decoder_g.decode(body)
        """Decodes the message received"""

        #logging.debug("Message received: "+str(input_decoded))

        if distributed:
            prediction_to_upper, prediction_output = model_g.predict(input_decoded)
        else:
            prediction_output = model_g.predict(input_decoded)
        """Predicts the data received"""

        prediction_value = prediction_output.tolist()[0]
        """Gets the prediction value"""

        logging.debug("Prediction done: %s", str(prediction_value))

        response = {
          'values': prediction_value
        }
        """Creates the object response"""

        response_to_kafka = json.dumps(response).encode()
        """Encodes the object response"""

        commitedMessages += 1

        if distributed and max(prediction_value) < limit_g:
            upper_producer.basic_publish(response_to_kafka)
                                   #headers=msg.headers())

        else:
            output_producer.basic_publish(response_to_kafka)
                                   #headers=msg.headers())

        logging.debug("Prediction sent to Kafka")

        end_inference = time.time()
        logging.debug("Total inference time: %s", str(end_inference - start_inference))
    except Exception as e:
        traceback.print_exc()
        logging.error("Error with the received data [%s]. Waiting for new a new prediction.", str(e))