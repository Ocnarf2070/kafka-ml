__author__ = 'Franco Emanuel Gonzalez Sanchez'

from .EnumDatasource import Datasource

import pika
import struct
import logging
import json

from .RabbitMQ_sink import RabbitMLSink


class RawSink(RabbitMLSink):
    """Class representing a sink of RAW training data to Apache Kafka.

       Args:
           boostrap_servers (str): List of RabbitMQ brokers
           topic (str): RabbitMQ topic
           deployment_id (str): Deployment ID for sending the training
           data_type (str): Datatype of the training data. Examples: uint8, string, bool, ...
           label_type (str): Datatype of the label data. Examples: uint8, string, bool, ...
           data_reshape (str): Reshape of the training data. Example: '28 28' for a matrix of 28x28.
               Defaults '' for no dimension.
           label_reshape (str): Reshape of the label data. Example: '28 28' for a matrix of 28x28.
               Defaults '' for no dimension.
           validation_rate (float): rate of the training data for validation. Defaults 0
           test_rate (float): rate of the training data for test. Defaults 0
           control_topic (str): Control RabbitMQ topic for sending confirmation after sending training data.
               Defaults to KAFKA_ML_CONTROL_TOPIC
           group_id (str): Group ID of the RabbitMQ consumer. Defaults to sink

       Attributes:
           data_type (str): Datatype of the training data. Examples: uint8, string, bool, ...
           label_type (str): Datatype of the label data. Examples: uint8, string, bool, ...
           data_reshape (str): Reshape of the training data. Example: '28 28' for a matrix of 28x28.
               Defaults '' for no dimension.
           label_reshape (str): Reshape of the label data. Example: '28 28' for a matrix of 28x28.
               Defaults '' for no dimension.
   """

    def __init__(self, boostrap_servers, topic, deployment_id,
                 data_type=None, label_type=None, description='', data_reshape=None, label_reshape=None,
                 validation_rate=0, test_rate=0, control_topic='KAFKA_ML_CONTROL_TOPIC',
                 group_id: Datasource = Datasource.RAW_SINK, user='guest', password='guest'):
        input_format = 'RAW'
        super().__init__(boostrap_servers, topic, deployment_id, input_format, description, {},
                         # {} = no data_restrictions
                         validation_rate, test_rate, control_topic, group_id, user, password)

        self.data_type = data_type
        self.label_type = label_type
        self.data_reshape = data_reshape
        self.label_reshape = label_reshape

        dic = {
            'type': 'init',
            'topic': self.topic,
            'deployment_id': self.deployment_id,
            'test_rate': self.test_rate,
            'validation_rate': self.validation_rate,
            'group_id': self.group_id.name,
            'description': self.description,
            'input_config': self.input_config,
            'data_type': self.data_type,
            'label_type': self.label_type,
            'data_reshape': self.data_reshape,
            'label_reshape': self.label_reshape
        }
        body = json.dumps(dic).encode('utf-8')
        self._producer.basic_publish(exchange=self.group_id.name, routing_key=self.control_topic, body=body)
        logging.info("Sent Init values to RabbitMQ")
