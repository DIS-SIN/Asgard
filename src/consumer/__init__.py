
from confluent_kafka.avro.serializer import SerializerError
from confluent_kafka.avro import AvroConsumer
from confluent_kafka import KafkaError

class Consumer:
    def __init__(self, broker, schema_registry, topic, logger):
        self.__consumer = AvroConsumer(
            {
                "bootstrap.servers": broker,
                "group.id": "asgard",
                "schema.registry.url": schema_registry 
            }
        )
        self.__consumer.subscribe([topic])
        self.logger = logger

    def consume_data(self):
        try:
            msg = self.__consumer.poll(1)
        except SerializerError as e:
            self.__log_msg("Message deserialization has failed {}: {}".format(msg,e))
        except Exception as e:
            self.__log_msg("An unkown error has occured {}".format(e))
        if not msg is None:
            if msg.error():
                self.__log_msg("AvroConsumer error: {}".format(msg.error()))
            else:
                return msg.value()
        return msg
 
    def __enter__(self):
        return self.__consumer

    def __exit__(self, *args):
        self.close()
    
    # TODO needs to be implemented properly when application logger is sorted
    def __log_msg(self, msg, level = None):
        if self.logger is not None:
            pass
        else:
            if level is not None:
                print(f"LOGGED MESSAGE: {msg}")
            else:
                print(f"{level}: {msg}")

    def close(self):
        self.__consumer.close()


