__author__ = 'Franco Emanuel Gonzalez Sanchez'

from .EnumDatasource import Datasource

import pika
import struct
import logging
import json

from .RabbitMQ_sink import RabbitMLSink


class AvroSink(RabbitMLSink):
    """Class representing a sink of Avro training data to Apache Kafka.

        Args:
            boostrap_servers (str): List of Kafka brokers
            topic (str): Kafka topic
            deployment_id (str): Deployment ID for sending the training
            data_scheme_filename (str): Filename of the AVRO scheme for training data
            label_scheme_filename (str): Filename of the AVRO scheme for label data
            validation_rate (float): rate of the training data for evaluation. Defaults 0
            test_rate (float): rate of the training data for test. Defaults 0
            control_topic (str): Control Kafka topic for sending confirmation after sending training data.
                Defaults to KAFKA_ML_CONTROL_TOPIC
            group_id (str): Group ID of the Kafka consumer. Defaults to sink

    """

    def __init__(self, boostrap_servers, topic, deployment_id,
                 data_scheme_filename, label_scheme_filename, description='', validation_rate=0, test_rate=0,
                 control_topic='KAFKA_ML_CONTROL_TOPIC',
                 group_id: Datasource = Datasource.RAW_SINK, user='guest', password='guest'):
        input_format = 'AVRO'
        super().__init__(boostrap_servers, topic, deployment_id, input_format, description, {},
                         # {} = no data_restrictions
                         validation_rate, test_rate, control_topic, group_id, user, password)

        self.data_scheme_filename = data_scheme_filename
        self.label_scheme_filename = label_scheme_filename

        dic = {
            'type': 'init',
            'topic': self.topic,
            'deployment_id': self.deployment_id,
            'test_rate': self.test_rate,
            'validation_rate': self.validation_rate,
            'group_id': self.group_id.name,
            'description': self.description,
            'input_config': self.input_config,
            'data_scheme_filename': self.data_scheme_filename,
            'label_scheme_filename': self.label_scheme_filename
        }
        body = json.dumps(dic).encode('utf-8')
        self._producer.basic_publish(exchange=self.group_id.name, routing_key=self.control_topic, body=body)
        logging.info("Sent Init values to RabbitMQ")

    def send_avro(self, data, label):
        self.send(data, label)
