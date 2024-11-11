
from .sink import KafkaMLSink
import avro.schema
import io
from avro.io import DatumWriter, BinaryEncoder
import pika
class AvroInference():
    """Class representing a sink of Avro inference data to Apache Kafka.

        Args:
            boostrap_servers (str): List of Kafka brokers
            topic (str): Kafka topic 
            data_scheme_filename (str): Filename of the AVRO scheme for training data
            group_id (str): Group ID of the Kafka consumer. Defaults to sink

    """
    # ip = 'localhost', port = 5672, topic = '/', queue = 'pytorch', exchange = 'pytorch'):
    def __init__(self,  boostrap_servers,  queue,
        data_scheme_filename, topic='/', user='guest', password='guest', group_id='sink'):
        
        self.boostrap_servers= boostrap_servers
        self.topic = topic
        self.queue = queue

        self.data_scheme_filename = data_scheme_filename

        self.data_schema = open(self.data_scheme_filename, "r").read()

        self.avro_data_schema = avro.schema.Parse(self.data_schema)
        self.data_writer = DatumWriter(self.avro_data_schema)
      
        self.data_io = io.BytesIO()
        self.data_encoder = BinaryEncoder(self.data_io)

        (HOST, PORT) = boostrap_servers.split(':')

        credentials = pika.PlainCredentials(user, password)
        self.__connection = pika.BlockingConnection(pika.ConnectionParameters(HOST, PORT, topic, credentials, heartbeat=0))
        self.__producer = self.__connection.channel()

        self.__producer.queue_declare(queue, passive=False, durable=True, auto_delete=False)
    
    def send(self, data):
        
        self.data_writer.write(data, self.data_encoder)
        data_bytes = self.data_io.getvalue()

        self.__producer.basic_publish(exchange='', routing_key=self.queue, body=data_bytes)
        self.data_io.seek(0)
        self.data_io.truncate(0)
        """Cleans data buffer"""

    def close(self):
        self.__producer.close()
