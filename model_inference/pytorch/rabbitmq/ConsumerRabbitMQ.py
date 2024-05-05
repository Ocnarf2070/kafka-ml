import pika
import time

from decoders import *

output_producer = None
decoder_g = None
model_g = None
commitedMessages = 0


class ConsumerRabbitMQ:

    def __init__(self, user='admin', password='pass', ip='localhost', port=5672, topic='/'):
        credentials = pika.PlainCredentials(user, password)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(ip, port, topic, credentials))
        self.channel = self.connection.channel()

    def start_consumer(self, queue='pytorch', output=None, decoder=None, model=None):
        global decoder_g
        global output_producer
        global model_g
        output_producer = output
        decoder_g = decoder
        model_g = model
        self.channel.basic_consume(queue, on_message_callback=queue_callback, auto_ack=True)
        self.channel.start_consuming()


def queue_callback(channel, method, properties, body):
    global commitedMessages
    if output_producer is None or decoder_g is None or model_g is None:
        raise Exception("Some values are empty")

    if len(method.exchange):
        print("from exchange '{}': {}".format(method.exchange,
                                              body.decode('UTF-8')))
    else:
        print("from queue {}: {}".format(method.routing_key,
                                         body.decode('UTF-8')))

    try:
        start_inference = time.time()

        logging.debug("Message received for prediction")

        input_decoded = decoder_g.decode(body)
        """Decodes the message received"""

        if input_decoded.shape[0] == 1 and len(input_decoded.shape) == 4:
          input_decoded = input_decoded[0]
        """Outwrapping the input data"""

        tensored_input = ToTensor()(input_decoded)

        tensored_input = torch.unsqueeze(tensored_input, 0)

        tensored_input = tensored_input.to(device)

        prediction_output = model(tensored_input)
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


        output_producer.produce(output_topic, response_to_kafka, headers=msg.headers())
        output_producer.flush()
        """Flush the message to be sent now"""
        """Sends the message to Kafka"""

        logging.debug("Prediction sent to Kafka")

        commitedMessages += 1
        if commitedMessages >= MAX_MESSAGES_TO_COMMIT:
          consumer.commit()
          commitedMessages = 0
          """Commits the message to Kafka"""
          logging.debug("Commited messages to Kafka")

        end_inference = time.time()
        logging.debug("Total inference time: %s", str(end_inference - start_inference))

    except Exception as e:
        traceback.print_exc()
        logging.error("Error with the received data [%s]. Waiting for new a new prediction.", str(e))