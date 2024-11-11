__author__ = 'Franco Emanuel Gonzalez Sanchez'

import json_numpy

from .EnumDatasource import Datasource

import pika
import struct
import logging
import json


class RabbitMLSink(object):
    """Class representing a sink of training data to Rabbit MQ. This class will allow to receive
        training data in the send methods and will send it through Rabbit MQ for the training and
        validation purposes. Once all data would have been sent to Kafka the `close` is invoked.

    Args:
        boostrap_servers (str): List of Rabbit MQ servers
        topic (str): Rabbit MQ topic
        deployment_id (str): Deployment ID for sending the training
        input_format (str): Input format of the training data. Expected values are RAW and AVRO
        data_type (str): Datatype of the training data. Examples: uint8, string, bool, ...
        label_type (str): Datatype of the label data. Examples: uint8, string, bool, ...
        data_reshape (str): Reshape of the training data. Example: '28 28' for a matrix of 28x28.
            Defaults '' for no dimension.
        label_reshape (str): Reshape of the label data. Example: '28 28' for a matrix of 28x28.
            Defaults '' for no dimension.
        validation_rate (float): rate of the training data for evaluation. Defaults 0.2
        test_rate (float): rate of the training data for test. Defaults 0.1
        control_topic (str): Control Rabbit MQ topic for sending confirmation after sending training data.
            Defaults to control
        group_id (str): Group ID of the Rabbit MQ. Defaults to sink
        user (str): Rabbit MQ user. Default guess
        password (str): Rabbit MQ password. Default guess


    Attributes:
        boostrap_servers (str): List of Rabbit MQ servers
        topic (str): Rabbit MQ topic
        deployment_id (str): Deployment ID for sending the training
        input_format (str): Input format of the training data. Expected values are RAW and AVRO
        data_type (str): Datatype of the training data. Examples: uint8, string, bool, ...
        label_type (str): Datatype of the label data. Examples: uint8, string, bool, ...
        data_reshape (str): Reshape of the training data. Example: '28 28' for a matrix of 28x28.
            Defaults '' for no dimension.
        label_reshape (str): Reshape of the label data. Example: '28 28' for a matrix of 28x28.
            Defaults '' for no dimension.
        validation_rate (float): rate of the training data for evaluation. Defaults 0.2
        test_rate (float): rate of the training data for test. Defaults 0.1
        control_topic (str): Control Rabbit MQ topic for sending confirmation after sending training data.
            Defaults to KAFKA_ML_CONTROL_TOPIC
        group_id (str): Group ID of the Rabbit MQ consumer. Defaults to sink
        __producer (:obj:KafkaProducer): Kafka producer
    """

    def __init__(self, boostrap_servers, topic, deployment_id,
                 input_format, description='', dataset_restrictions={},
                 validation_rate=0, test_rate=0, control_topic='KAFKA_ML_CONTROL_TOPIC',
                 group_id: Datasource = Datasource.SINK, user='guest',
                 password='guest'):
        self.boostrap_servers = boostrap_servers
        self.topic = topic
        self.deployment_id = deployment_id
        self.input_format = input_format
        self.description = description
        self.dataset_restrictions = dataset_restrictions
        self.validation_rate = validation_rate
        self.test_rate = test_rate
        self.control_topic = control_topic
        self.group_id: Datasource = group_id
        self.input_config = {}
        self.online = None

        (HOST, PORT) = self.boostrap_servers.split(':')

        credentials = pika.PlainCredentials(user, password)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(HOST, int(PORT), '/', credentials,
                                                                            heartbeat=0))
        self._producer = self.connection.channel()

        self._producer.exchange_declare(exchange=group_id.name, exchange_type="direct", passive=False, durable=True,
                                        auto_delete=False)
        self._producer.queue_declare(control_topic, passive=False, durable=True, auto_delete=False)

        self._producer.queue_bind(queue=control_topic, exchange=group_id.name, routing_key=control_topic)

        if group_id == Datasource.SINK:
            dic = {
                'type': 'init',
                'topic': self.topic,
                'input_format': self.input_format,
                'deployment_id': self.deployment_id,
                'validation_rate': self.validation_rate,
                'test_rate': self.test_rate,
                'group_id': self.group_id.name,
                'description': self.description,
                'dataset_restrictions': self.dataset_restrictions,
                'input_config': self.input_config
            }
            body = json.dumps(dic).encode('utf-8')
            self._producer.basic_publish(exchange=self.group_id.name, routing_key=self.control_topic, body=body)
            logging.info("Sent Init values to RabbitMQ")

    def __send(self, data, label):

        dic = {
            'type': 'send',
            'group_id': self.group_id.name,
            'data': data,
            'label': label
        }
        body = json_numpy.dumps(dic).encode('utf-8')
        self._producer.basic_publish(exchange=self.group_id.name, routing_key=self.control_topic, body=body)
        # logging.info("Sent Key-value to RabbitMQ")

    def __close(self):
        if self.online is not None:
            dic = {'group_id': self.group_id.name, 'type': 'close'}
        else:
            dic = {'group_id': self.group_id.name, 'type': 'online_close'}
        body = json.dumps(dic).encode('utf-8')
        self._producer.basic_publish(exchange=self.group_id.name, routing_key=self.control_topic, body=body)
        logging.info("Closing Producer")
        self._producer.close()

    def send(self, data, label):
        """Sends data and label to Apache Kafka"""

        self.__send(data, label)

    def send_value(self, data):
        """Sends data to Apache Kafka"""

        self.__send(data, None)

    def close(self):
        self.__close()

    def online_close(self):
        self.__close()