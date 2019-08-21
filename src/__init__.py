import os
import json
import time
import logging
import logging.config
from .producer import Producer
from .consumer import Consumer
from .machine_learning_providers import process_text

def create_stream(environment="production", configs_path="./configs", 
                  schemas_path="./schemas"):

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
        
        if "LOGGING_CONFIG" in configs:
            logging.config.dictConfig(configs["LOGGING_CONFIG"])
            logging_enabled = True
        else:
            logging_enabled = False
            
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
        development_config_path = os.path.join(configs_path, "development.json")
        if os.path.isfile(development_config_path):
            with open(development_config_path, "r", encoding="utf-8") as f:
                configs = {**configs, **json.load(f)}

        if "LOGGING_CONFIG" in configs:
            logging.config.dictConfig(configs["LOGGING_CONFIG"])
            logging_enabled = True

        else:
            logging_enabled = False
        
        if environment != "development":
            if not logging_enabled :     
                print("WARNING: development environment not explicitly set "+
                      f"environment set as {environment}")
            else:
                logging.warn("development environment not explicitly set " +
                            f"environment set as {environment}")
        
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
                configs["SCHEMA_REGISTRY"] = "http://localhost:8081"
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
        configs["PRODUCER_SCHEMA"] = json.dumps(json.load(f))
    
    def stream():
        message_consumer = Consumer(
            broker = configs["BROKER_HOST"],
            schema_registry = configs["SCHEMA_REGISTRY"],
            topic = configs["CONSUMER_TOPIC"],
            logging_enabled=logging_enabled,
            autocommit=False
        )
        message_producer = Producer(
            configs["PRODUCER_TOPIC"],
            broker = configs["BROKER_HOST"],
            schema_registry = configs["SCHEMA_REGISTRY"],
            schema = configs["PRODUCER_SCHEMA"],
            logging_enabled=logging_enabled
        )
        while True:
            message = message_consumer.consume()
            if message is not None:
                processed_data = []
                textual_data = message.get("data")
                if isinstance(textual_data, list):
                    incorrect_formats = 0
                    start_time = time.time()
                    for data in textual_data:
                        uid = None
                        correct_format = True
                        if isinstance(data, dict):
                            uid = data.get("uid")
                            text = data.get("text")
                        else:
                            correct_format = False
                        
                        if correct_format and text is not None and isinstance(text, str):
                            processed_text = process_text(text, providers = configs["ML_PROVIDERS"], logging_enabled=logging_enabled)
                            for provider in processed_text:
                                provider["uid"] = uid
                        else:
                            correct_format = False
                        
                        if not correct_format:
                            if logging_enabled:
                                logging.warning(
                                    "A message with an incorrect format was recieved\n{}\nfor message {}".format(data, message)
                                )
                            else:
                                print(
                                    "A message with an incorrect format was recieved\n{}\nfor message {}".format(data, message)
                                )
                            incorrect_formats += 1
                        else:
                            processed_data.append(processed_text)
                        
                    if environment == "development":
                        process_time = time.time() - start_time
                        print(
                            "Time taken to process data {}".format(process_time)
                        )
                if isinstance(textual_data, list) and len(textual_data) >incorrect_formats:
                    data_to_be_sent = {
                        "uid": message.get("uid"),
                        "data": processed_data
                    }

                    message_producer.produce(
                        data_to_be_sent
                    )
                else:
                    if logging_enabled:
                        logging.critical(
                            f"Message {message}\nwill not be sent as a result of none of it's components being the correct format"
                        )
                    else:
                        print(
                            f"Message {message}\nwill not be sent as a result of none of it's components being the correct format"
                        )
                try:
                    message_consumer.commit(asynchronous=False)
                except Exception as e:
                    if logging_enabled:
                        logging.critical(
                            "Message commit as failed with the following error {}".format(e)
                        )
    
    return stream

                




        
                



        