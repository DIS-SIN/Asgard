
from confluent_kafka.avro.serializer import SerializerError
from confluent_kafka.avro import AvroConsumer
from confluent_kafka import KafkaError
import traceback

class Consumer:
    def __init__(self, broker, schema_registry, topic, logger = None, groupId = "asgard"):
        """
        Initialiser for Confluent Consumer using AvroConsumer. 
        Each consumer can only be subscribed to one topic 
        Parameters
        ----------
        broker: str
            The URL of the broker (example: 'localhost:9092')
        schema_registry: str
            The URL of the confluent Schema Registry endpoint (example: 'http://localhost:8081')
        topic: str
            The topic to subscribe too
        logger: Logger object, Optional
            The logger object which will be used to log messages if provided
        groupId: str, Optional
            An optional groupId which can be used to loadbalance consumers default is "asgard"
        """
        self.__consumer = AvroConsumer(
            {
                "bootstrap.servers": broker,
                "group.id": groupId,
                "schema.registry.url": schema_registry 
            }
        )
        self.__consumer.subscribe([topic])
        self.logger = logger

    def consume(self):
        """
        Method to consume and return message if exists and can be deserialized

        Returns
        -------
        str
            The recieved message payload as a string
        None
            No message has been recieved or an error has occured
        """
        try:
            msg = self.__consumer.poll(1)
        except SerializerError as e:
            self.__log_msg(
                "Message deserialization has failed {}: {}".format(msg,e),
                "See the following stack trace",
                f"{traceback.format_exc()}",
                delimeter="\n",
                level="ERROR")
        except RuntimeError as e:
            self.__log_msg(
                "The consumer has been closed and cannot recieve messages",
                level = "ERROR"
            )
        except Exception as e:
            self.__log_msg(
                "An unkown error has occured {}".format(e),
                "See the following stack trace",
                f"{traceback.format_exc()}",
                delimeter="\n",
                level= "ERROR"
            )
        if not msg is None:
            if msg.error():
                self.__log_msg(
                    "AvroConsumer error: {}".format(msg.error()),
                    level="ERROR"
                )
            else:
                return msg.value()
 
    def __enter__(self):
        return self.__consumer

    def __exit__(self, *args):
        self.close()
    
    # TODO needs to be implemented properly when application logger is sorted
    def __log_msg(self, *messages, level = None, delimeter= " ", ):
        msg = delimeter.join(messages)
        if self.logger is not None:
            pass
        else:
            if level is not None:
                print(f"LOGGED MESSAGE: {msg}")
            else:
                print(f"{level}: {msg}")

    def close(self):
        """
        Close the consumer, Once called this object cannot be reused
        """
        self.__consumer.close()


