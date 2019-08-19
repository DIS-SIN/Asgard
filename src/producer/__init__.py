# -*- coding: utf-8 -*-
import traceback
import time
from confluent_kafka import avro, KafkaException
from confluent_kafka.avro import AvroProducer, SerializerError
from queue import SimpleQueue


class Producer:

    def __init__(self, *topics, broker, schema_registry, schema, logger = None):
        """
        Initialization of the Producer which instatiates an AvroProducer class 

        Parameters
        ----------
        broker: str
            The URL of the broker (example: 'localhost:9092')
        schema_registry: str
            The URL of the confluent Schema Registry endpoint (example: 'http://localhost:8081')
        schema: str
            The default AVRO schema to use to serialize messages
        logger: Logger object, optional
            The logger object which will be used to log messages if provided
        topics
            variable length argument list of the string names of topics to produce too
        """
        self.__producer = AvroProducer(
            {
                "bootstrap.servers": broker,
                "schema.registry.url": schema_registry
            },
            default_key_schema=schema
        )
        self.topics = topics
        self.schema = schema
        self.logger = logger
        self.produce_flag = True
        self.production_last_stoped = 0
        self.total_time_producing_stoped = 0
        self.__msg_queue = SimpleQueue()
    
    def produce(self, msg, schema = None, callback = None):
        """
        Write a message to confluent kafka using
        the instatiated AvroProducer to serialize
        
        Parameters
        ----------
        msg: str
            The message to be serialized and sent 
        schema: str, Optional
            An optional schema to overide the default 
            set in the constructor
        callback: Function object, Optional
            An optional callback which will be executed 
            whether the producing of the message fails or
            succeeds. This function must take two parameters
            the first for the error and the second for the message
            (https://docs.confluent.io/current/clients/confluent-kafka-python/#producer)     
        """
        # TODO: function partials for better readability ?
        # SOLVED: created dictionary to expand to parameters
        params = {}
        params["value"] = msg
        if schema is not None:
            params["value_schema"] = schema
        if callback is not None:
            params["on_delivery"] = callback
        for topic in self.topics:
            params["topic"] = topic
            self.__msg_queue.put_nowait(params)
        try:
            while not self.__msg_queue.empty():
                msg = self.__msg_queue.get_nowait()
                self.__producer.produce(**msg)
                self.__producer.flush()
                self.produce_flag = True
                self.production_last_stoped = 0
        
        except SerializerError as e:
            self.__log_msg(
                "ERROR",
                "Message deserialization has failed {}: {} \n".format(msg,e),
                "See the following trace back \n {}".format(traceback.format_exc())
            )
        except BufferError as e:

            if self.produce_flag or (
                self.production_last_stoped != 0 and ((time.time() - self.production_last_stoped) >= 3600)
            ):
                self.produce_flag = False
                self.production_last_stoped = time.time()
                self.total_time_producing_stoped += time.time() - self.production_last_stoped
                self.__log_msg(
                    "Queue Buffer has reached its maximum capacity, unable to deliver message {}: {}".format(msg,e),
                    "Message production will be shut down until messages can be resent",
                    f"Total time message producing has stopped {self.total_time_producing_stoped}",
                    level="CRITICAL",
                    delimeter="\n"
                )
        except KafkaException as e:
            self.__log_msg(
                "An unknown exception has occured specific to Kafka {}: {}".format(msg, e),
                level="ERROR",
                delimeter=""
            )
        except Exception as e:
            self.__log_msg(
                "An unknown exception has occured {}: {}".format(msg, e),
                f"See the following traceback {traceback.format_exc()}",
                level="ERROR",
                delimeter="\n"
            )
    def __enter__(self):
        """
        Context Manager for Producer, to allow custom actions for producing messages
        """
        return self.__producer
    
    def __exit__(self, *args):
        """
        On exit producer is flushed
        """
        self.__producer.flush()

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
        
        
            

    


