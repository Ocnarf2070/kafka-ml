from mainTraining import *
from callbacks import *
import logging

class SingleIncrementalTraining(MainTraining):
    """Class for single models incremental training
    
    Attributes:
        boostrap_servers (str): list of boostrap server for the Kafka connection
        result_url (str): URL for downloading the untrained model
        result_id (str): Result ID of the model
        control_topic(str): Control topic
        deployment_id (int): deployment ID of the application
        batch (int): Batch size used for training
        kwargs_fit (:obj:json): JSON with the arguments used for training
        kwargs_val (:obj:json): JSON with the arguments used for validation
        stream_timeout (int): stream timeout to wait for new data
        monitoring_metric (str): metric to track for indefinite training
        change (str): direction in which monitoring metric improves
        improvement (decimal): how many the monitoring metric improves
    """

    def __init__(self):
        """Loads the environment information"""

        super().__init__()

        self.stream_timeout, self.monitoring_metric, self.change, self.improvement = load_incremental_environment_vars()

        logging.info("Received incremental environment information (stream_timeout, monitoring_metric, change, improvement) ([%d], [%s], [%s], [%s])",
                self.stream_timeout, self.monitoring_metric, self.change, str(self.improvement))
    
    def get_models(self):
        """Downloads the model and loads it"""

        super().get_single_model()

    def get_data(self, kafka_topic, decoder):
        """Gets the incremental data from Kafka"""

        return super().get_online_train_data(kafka_topic)
    
    def train(self, splits, kafka_dataset, decoder, validation_rate, start):
        """Trains the model"""

        callback = SingleTrackTrainingCallback(NOT_DISTRIBUTED_INCREMENTAL, self.result_url, self.tensorflow_models)

        return super().train_incremental_model(kafka_dataset, decoder, validation_rate, callback, start)
    
    def saveMetrics(self, model_trained):
        """Saves the metrics of the model"""
        
        return super().saveSingleMetrics(model_trained)
    
    def getConfussionMatrix(self, splits, training_results):
        """Gets the confussion matrix of the model"""

        return super().createConfussionMatrix(training_results['test_dataset'], training_results['test_size'])
    
    def sendMetrics(self, cf_generated, epoch_training_metrics, epoch_validation_metrics, test_metrics, dtime, cf_matrix):
        """Sends the metrics to the control topic"""

        return super().sendSingleMetrics(cf_generated, epoch_training_metrics, epoch_validation_metrics, test_metrics, dtime, cf_matrix)