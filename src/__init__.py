import os
import json
import time
from .producer import Producer
from .consumer import Consumer
from .machine_learning_providers import process_text

def create_stream(environment="production", configs_path="./configs", 
                  schemas_path="./schemas", logger = None):

    # pull default configuration if it exists 
    default_config_path = os.path.join(configs_path, "default.json")
    if os.path.isfile(default_config_path):
        with open(default_config_path,"r", encoding="utf-8") as f:
            configs = json.load(f)
    else:
        configs = {}
    
    # configure production environment
    if environment == "production":
        configuration_successful = True
        configuration_issues = []

        production_config_path = os.path.join(configs_path, "production.json")
        if os.path.isfile(production_config_path):
            with open(production_config_path, "r", encoding="utf-8") as f:
                configs = {**configs, **json.load(f)}
        
        if "BROKER_HOST" not in configs:
            broker_host_environ = os.environ.get("ASGARD_BROKER_HOST")
            if broker_host_environ is None:
                configuration_successful = False
                configuration_issues.append(
                    "BROKER_HOST is not set, either add it to the production.json or " +
                    "set environment variable ASGARD_BROKER_HOST"
                )
            else:
                configs["BROKER_HOST"] = broker_host_environ
        
        if "SCHEMA_REGISTRY" not in configs:
            scheme_registry_environ = os.environ.get("ASGARD_SCHEMA_REGISTRY")
            if scheme_registry_environ is None:
                configuration_successful = False
                configuration_issues.append(
                    "SCHEMA_REGISTRY is not set, either add it to the prduction.json or " +
                    "set envirtonment variable ASGARD_SCHEMA_REGISTRY"
                )
            else:
                configs["SCHEMA_REGISTRY"] = scheme_registry_environ
        
        if "CONSUMER_TOPIC" not in configs:
            consumer_topic_environ = os.environ.get("ASGARD_CONSUMER_TOPIC")
            if consumer_topic_environ is None:
                configuration_successful = False
                configuration_issues.append(
                    "CONSUMER_TOPIC is not set, either add it to the production.json or " +
                    "set environment variable ASGARD_CONSUMER_TOPIC"
                )
            else:
                configs["CONSUMER_TOPIC"] = consumer_topic_environ
        
        if "PRODUCER_TOPIC" not in configs:
            producer_topic_environ = os.environ.get("ASGARD_PRODUCER_TOPIC")
            if producer_topic_environ is None:
                configuration_successful = False
                configuration_issues.append(
                    "PRODUCER_TOPIC is not set, either add it to the production.json or " +
                    "set environment variable ASGARD_PRODUCER_TOPIC"
                )
            else:
                configs["PRODUCER_TOPIC"] =  producer_topic_environ
        
        if "ML_PROVIDERS" not in configs:
            configuration_successful = False
            configuration_issues.append(
                "ML_PROVIDERS is not set, must be set in " +
                "either the production.json or default.json"
            )
        if "PRODUCER_SCHEMA" not in configs:
            producer_schema_environ = os.environ.get("ASGARD_PRODUCER_SCHEMA")
            if producer_schema_environ is None:
                configuration_successful = False
                configuration_issues.append(
                    "PRODUCER_SCHEMA is not set, must be set in " +
                    "either the production.json, default.json or set " +
                    "environment variable ASGARD_PRODUCER_SCHEMA"
                )
            else:
                configs["PRODUCER_SCHEMA"] = producer_schema_environ

        if not configuration_successful:
            raise ValueError(
                "The following exceptions occured {}".format(
                    "\n".join(configuration_issues)
                )
            )
    # default to development environment if not production
    else:
        if environment != "development":
            if logger is None:     
                print("WARNING: development environment not explicitly set "+
                      f"environment set as {environment}")
            else:
                logger.warn("development environment not explicitly set " +
                            f"environment set as {environment}")
        development_config_path = os.path.join(configs_path, "development.json")
        if os.path.isfile(development_config_path):
            with open(default_config_path, "r", encoding="utf-8") as f:
                configs = {**configs, **json.load(f)}
        
        if "BROKER_HOST" not in configs:
            broker_host_environ = os.environ.get("ASGARD_BROKER_HOST")
            if broker_host_environ is None:
                configs["BROKER_HOST"] = "localhost:9092"
            else:
                configs["BROKER_HOST"] = broker_host_environ
        
        if "PRODUCER_SCHEMA" not in configs:
            producer_schema_environ = os.environ.get("ASGARD_PRODUCER_SCHEMA")
            if producer_schema_environ is None:
                configs["PRODUCER_SCHEMA"] = "data_output.avsc"
            else:
                configs["PRODUCER_SCHEMA"] = producer_schema_environ
        
        if "SCHEMA_REGISTRY" not in configs:
            scheme_registry_environ = os.environ.get("ASGARD_SCHEMA_REGISTRY")
            if scheme_registry_environ is None:
                configs["SCHEMA_REGISRTY"] = "http://localhost:8081"
            else:
                configs["SCHEMA_REGISTRY"] = scheme_registry_environ
        
        if "CONSUMER_TOPIC" not in configs:
            consumer_topic_environ = os.environ.get("ASGARD_CONSUMER_TOPIC")
            if consumer_topic_environ is None:
                configs["CONSUMER_TOPIC"] = "text_data_to_be_processed"
            else:
                configs["CONSUMER_TOPIC"] = consumer_topic_environ
        
        if "PRODUCER_TOPIC" not in configs:
            producer_topic_environ = os.environ.get("ASGARD_PRODUCER_TOPIC")
            if producer_topic_environ is None:
                configs["PRODUCER_TOPIC"] = "text_data_processed"
            else:
                configs["PRODUCER_TOPIC"] =  producer_topic_environ
        
        if "ML_PROVIDERS" not in configs:
            configs["ML_PROVIDERS"] = [
                "google"
            ]

    producer_schema_path = os.path.join(schemas_path, configs["PRODUCER_SCHEMA"])
    with open(producer_schema_path, "r", encoding="utf-8") as f:
        configs["PRODUCER_SCHEMA"] = str(json.load(f))

    def stream():
        message_consumer = Consumer(
            broker = configs["BROKER_HOST"],
            schema_registry = configs["SCHEMA_REGISTRY"],
            topic = configs["CONSUMER_TOPIC"],
            logger= logger
        )
        message_producer = Producer(
            configs["PRODUCER_TOPIC"],
            broker = configs["BROKER_HOST"],
            schema_registry = configs["SCHEMA_REGISTRY"],
            schema = configs["PRODUCER_SCHEMA"],
            logger = logger
        )
        while True:
            message = message_consumer.consume()
            if message is not None:
                processed_data = []
                textual_data = message.get("data")
                if isinstance(textual_data, list):
                    for text in textual_data:
                        if isinstance(text, str):
                            start_time = time.time()
                            processed_data.append(
                              process_text(text, providers = configs["ML_PROVIDERS"])
                            )
                            if environment == "development":
                                process_time = time.time() - start_time
                                print(
                                    "Time taken to process data {}".format(process_time)
                                )
                        # TODO: cases where not string ?
                data_to_be_sent = {
                    "uid": message.get("uid"),
                    "data": processed_data
                }

                message_producer.produce(
                    data_to_be_sent
                )
    
    return stream

                




        
                



        