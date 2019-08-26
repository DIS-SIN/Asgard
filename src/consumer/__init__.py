
import logging
import traceback
from queue import SimpleQueue
from confluent_kafka.avro.serializer import SerializerError
# from confluent_kafka.avro import AvroConsumer
import json
from confluent_kafka import KafkaError, Consumer as KafkaConsumer 


class Consumer:
    def __init__(self, broker, schema_registry, topic, logging_enabled = False, groupId = "asgardConsumer", autocommit = True):
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
        """self.__consumer = AvroConsumer(
            {
                "bootstrap.servers": broker,
                "group.id": groupId,
                "schema.registry.url": schema_registry,
                "enable.auto.commit": autocommit 
            }
        )"""
        self.__consumer = KafkaConsumer(
            {
                "bootstrap.servers": broker,
                "group.id": groupId,
                "enable.auto.commit": autocommit,
                "auto.offset.reset": "earliest"
            }
        )
        self.autocommit = autocommit
        if not autocommit:
            self.consumed_messages= SimpleQueue()
        self.__consumer.subscribe([topic])
        if logging_enabled:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = None

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
        msg = None
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
        logging.debug(msg)   
        if not msg is None:
            if msg.error():
                self.__log_msg(
                    "AvroConsumer error: {}".format(msg.error()),
                    level="ERROR"
                )
            else:
                if not self.autocommit:
                    self.consumed_messages.put_nowait(
                        msg
                    )
                logging.debug("Message Value " + msg.value().decode())
                return json.loads(msg.value().decode())
 
    def __enter__(self):
        return self.__consumer

    def __exit__(self, *args):
        self.close()
    
    def __log_msg(self, *messages, level="NOTSET", delimeter= " ", ):
        levels = {
            "CRITICAL": logging.CRITICAL,
            "ERROR": logging.ERROR,
            "WARNING": logging.WARNING,
            "INFO": logging.INFO,
            "DEBUG": logging.DEBUG,
            "NOTSET": logging.NOTSET
        }
        msg = delimeter.join(messages)
        if self.logger is not None:
            if level not in levels:
                raise ValueError(
                    f"level {level} is not valid must be one of {list(levels.keys())}"
                )
            self.logger.log(
                levels[level],
                msg
            )
        else:
            if level is not None:
                print(f"LOGGED MESSAGE: {msg}")
            else:
                print(f"{level}: {msg}")
    def commit(self, asynchronous = True):
        if not self.autocommit and not self.consumed_messages.empty():
            msg = self.consumed_messages.get_nowait()
            self.__consumer.commit(
                msg, asynchronous = asynchronous
            )
    def close(self):
        """
        Close the consumer, Once called this object cannot be reused
        """
        self.__consumer.close()


