from kafka import KafkaProducer
from backend.modules.exportMethods.exportClass import ExportType, ExportMethod
import json

#############################################################################
#
# Kafka export method
#
# Connect to a kafka server on init and send data to a topic
#
#############################################################################


class KafkaExportType(ExportType):
    def __init__(self):
        super().__init__()

        self.name = "kafka"
        # Expected parameters: [server, topic]
        self.parameters_definition = ["server", "topic"]

        self.export_method_class = KafkaExportMethod


class KafkaExportMethod(ExportMethod):
    up = False

    def __init__(self, name, parameters):
        super().__init__(KafkaExportType(), name, parameters)

        # Expected parameters: [server, topic]
        # Check parameters
        if len(parameters) != 2:
            raise Exception(
                "Kafka export type requires 2 parameters : server and topic"
            )

        # Create producer
        self.server = parameters[0]
        self.topic = parameters[1]

        # Create Kafka producer
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.server,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
            self.up = True
        except Exception as e:
            print("Kafka producer creation failed : " + str(e))
            print("server : '" + self.server + "'")
            raise Exception(
                "Kafka producer creation on server '"
                + self.server
                + "' failed with error : "
                + str(e)
            )

    def export(self, data):
        print("Kafka export method : Sending data to kafka", self.server, self.topic)
        print(data)

        if not self.up:
            raise Exception("Kafka producer is not up")

        try:
            print(self.producer.send(self.topic, data))
            print("Kafka export method : Data sent")
        except Exception as e:
            print("Kafka export method : Error sending data to kafka", e)
            raise "Kafka export method : Error sending data to kafka"
