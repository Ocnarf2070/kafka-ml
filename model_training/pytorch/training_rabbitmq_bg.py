import os
import pika
import sys
import logging
import json_numpy

sys.path.append(sys.path[0] + "/datasources")
"""To allow importing datasources"""
from datasources.EnumDatasource import Datasource
from config import *
from utils import *
from datasources.sink import KafkaMLSink
from datasources.raw_sink import RawSink
from datasources.avro_sink import AvroSink
from datasources.online_raw_sink import OnlineRawSink
from datasources.federated_raw_sink import FederatedRawSink
from datasources.federated_online_raw_sink import OnlineFederatedRawSink
import traceback

producer: KafkaMLSink = None

def load_environment_vars():
    """Loads the environment information receivedfrom dockers
    boostrap_servers, result_url, result_update_url, control_topic, deployment_id, batch, kwargs_fit
    Returns:
        boostrap_servers (str): list of boostrap server for the Kafka connection
        boostrap_servers (str): list of boostrap server for the Kafka connection
        control_topic(str): Control topic
    """
    bootstrap_servers_kafka = os.environ.get('BOOTSTRAP_SERVERS')
    bootstrap_servers_rabbitmq = os.environ.get('BOOTSTRAP_SERVERS_RABBITMQ')
    control_topic = os.environ.get('CONTROL_TOPIC')

    return bootstrap_servers_kafka, bootstrap_servers_rabbitmq, control_topic


def close():
    consumer.close()


def queue_callback(channel, method, properties, body):
    global producer
    dic = json_numpy.loads(body.decode('UTF-8'))
    dic_params = {}
    _type = dic['type']
    group = dic['group_id']
    if _type == 'init':
        dic_params['group_id'] = dic['group_id'].lower()
        dic_params['topic'] = dic['topic']
        dic_params['deployment_id'] = dic['deployment_id']
        if dic['description'] is not None:
            dic_params['description'] = dic['description']
        if dic['validation_rate'] is not None:
            dic_params['validation_rate'] = dic['validation_rate']

        if group != Datasource.SINK.name:
            if dic['data_type'] is not None:
                dic_params['data_type'] = dic['data_type']
            if dic['label_type'] is not None:
                dic_params['label_type'] = dic['label_type']
            if dic['data_reshape'] is not None:
                dic_params['data_reshape'] = dic['data_reshape']
            if dic['label_reshape'] is not None:
                dic_params['label_reshape'] = dic['label_reshape']

        if group == Datasource.SINK.name:
            dic_params['input_format'] = dic['input_format']
            if dic['dataset_restrictions'] is not None:
                dic_params['dataset_restrictions'] = dic['dataset_restrictions']
            if dic['test_rate'] is not None:
                dic_params['test_rate'] = dic['test_rate']

            producer = KafkaMLSink(bootstrap_servers_kafka, **dic_params)

        elif group == Datasource.RAW_SINK.name or group == Datasource.ONLINE_RAW_SINK.name:
            if group == Datasource.RAW_SINK.name:
                if dic['test_rate'] is not None:
                    dic_params['test_rate'] = dic['test_rate']
                producer = RawSink(bootstrap_servers_kafka, **dic_params)
            else:
                producer = OnlineRawSink(bootstrap_servers_kafka, **dic_params)

        elif group == Datasource.AVRO_SINK.name:
            dic_params['data_scheme_filename'] = dic['data_scheme_filename']
            dic_params['label_scheme_filename'] = dic['label_scheme_filename']
            if dic['test_rate'] is not None:
                dic_params['test_rate'] = dic['test_rate']

            producer = AvroSink(bootstrap_servers_kafka, **dic_params)
        else:
            raise Exception("There is no implementation of this type of Dataset")

    elif _type == 'send':
        _data = dic['data']
        _label = dic['label']
        if group == Datasource.AVRO_SINK.name:
            producer.send_avro(_data, _label)
        else:
            if _label is not None:
                producer.send(_data, _label)
            else:
                producer.send_value(_data)
    elif _type == 'send_control':
        producer.send_online_control_msg()
    elif _type == 'close' and producer:
        producer.close()
    elif _type == 'close_online' and producer:
        producer.online_close()

    else:
        raise Exception("There is no implementation of this type of Dataset")


if __name__ == '__main__':
    try:
        if DEBUG:
            logging.basicConfig(
                stream=sys.stdout,
                level=logging.DEBUG,
                format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
            )
        else:
            logging.basicConfig(
                stream=sys.stdout,
                level=logging.INFO,
                format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
            )
        """Configures the logging"""

        bootstrap_servers_kafka, bootstrap_servers_rabbitmq, control_topic = load_environment_vars()
        """Loads the environment information"""
        (HOST, PORT) = bootstrap_servers_rabbitmq.split(':')
        credentials = pika.PlainCredentials("guest", "guest")
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(HOST, int(PORT), '/', credentials, heartbeat=0))
        consumer = connection.channel()

        consumer.queue_declare(control_topic, passive=False, durable=True, auto_delete=False)

        consumer.basic_consume(queue=control_topic,
                               on_message_callback=queue_callback, auto_ack=True)
        consumer.start_consuming()

    except Exception as e:
        traceback.print_exc()
        logging.error("Error in main [%s]. Service will be restarted.", str(e))
