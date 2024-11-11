from enum import Enum


class Datasource(Enum):
    SINK = 1
    RAW_SINK = 2
    ONLINE_RAW_SINK = 3
    FEDERATED_RAW_SINK = 4
    FEDERATED_ONLINE_RAW_SINK = 5
    AVRO_SINK = 6

