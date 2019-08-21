# ASGARD

<b> This product is still in its infancy </b> 

## Context

The CSPS Digital Innovation Services under the Digital Academy is experimenting with Apache Kafka as part of the [CORTEX](https://github.com/DIS-SIN/Cortex) project. There was a need to create a stream processor from which ML services can be added in a generic way. Asgard was created to fill this need.

## What does it do 

Asgard is a stream processor for [Apache Kafka](https://kafka.apache.org/) which allows machine learning services and natural language processors for textual data to be added in a generic way to any kafka cluster. It listens to a configured topic and consumes messages containing the textual data. Asgard will processes this textual data using the implemented "ML Providers" and then produces a message on a seperate configured topic to be consumed by downstream applications (consumers in kafka speak).

## Using Asgard

### Kafka configuration 

You will obviously need a kafka instance to be able to use Asgard. You will need two topics for Asgard to work. One topic for the data that will be processed to be consumed by Asgard and the other for Asgard to put the processed data in. We recommend that these topics be used for nothing else as Asgard currently is not smart enough to decern on what it should consume and what it should not. 

## Asgard configuration

### Environments

Asgard has a development environment and a production environment. To switch between the production and the development environment set the environment variable ```ASGARD_ENV``` to either ```production``` or ```development```. If the environment variable is not set then the environment will default to production. If the environment variable is set to any other value then production or development, the environment will default to development. 

### Configuration Files and Environment Variables

Asgard contains three main json configuration files. These can be found in the [src/configs](/src/configs) folder. ```default.json``` is optional and is loaded regardless of the environment. ```development.json``` or ```production.json``` will then be loaded based on if the environment is development of production respectively. If there are the same keys in the ```default.json``` file as either the ```development.json``` or ```production.json```, it will be overwritten by the values in either of those files. For example if ```BROKER_HOST``` is set in the ```default.json```, also set in the ```development.json``` and the environment is development then the value for ```BROKER_HOST``` in the development.json will be used to configure the application.

Most configuration values in the json config files can be subsituted for environment variables by adding the prefix ```ASGARD_```  . There are some exceptions to this which will be noted in the configuration values list bellow.

### Configuration Values

#### kafka config values

```BROKER_HOST```  

*Description* : The endpoint for the apache kafka broker in the form of &lt;url>:&lt;port>

*Environment Variable Swappable*: Yes 

*Development Environment Behaviour*: If not in development.json and environment variable is not set. It will default to value ```localhost:9092```

*Production Environment Behanviour*: If not in production.json and environment variable is not set. Application will fail to start

```SCHEMA_REGISTRY```

*Description*: The endpoint for the apache schema registry in the form of https|http://&lt;url>:&lt;port>

*Environment Variable Swappable*: Yes 

*Development Environment Behaviour*: If not in development.json and environment variable is not set. It will default to value ```http://localhost:8081```

*Production Environment Behanviour*: If not in production.json and environment variable is not set. Application will fail to start

```CONSUMER_TOPIC```

*Description*: The topic that asgard will listen to which will contain the data to be processed

*Environment Variable Swappable*: Yes

*Development Environment Behaviour*: If not in development.json and environment variable is not set. It will default to value ```text_data_to_be_processed```

*Production Environment Behanviour*: If not in production.json and environment variable is not set. Application will fail to start

```PRODUCER_TOPIC```

*Description*: The topic that asgard will produce messages containing the processed data 

*Environment Variable Swappable*: Yes

*Development Environment Behaviour*: If not in development.json and environment variable is not set. It will default to value ```text_data_processed```

*Production Environment Behanviour*: If not in production.json and environment variable is not set. Application will fail to start

```PRODUCER_SCHEMA```

*Description*: The name of the file in the [```src/schemas```](/src/schemas) folder which contains the schema that will be used by Apache Avro Producer to serialize the message and downsteam consumers to deserialize it.

*Environment Variable Swappable*: Yes

*Development Environment Behaviour*: If not in development.json and environment variable is not set. It will default to value ```data_input.avsc```

*Production Environment Behanviour*: If not in production.json and environment variable is not set. Application will fail to start



#### Asgard specific configurations

```LOGGING_CONFIG```

*Description*: The configuration for the python logging module. All the default handlers, filters and formatters from the python logging module can be used. A slack handler for posting logs to slack has also been implemented (see logging section). Here is an example logging configuration

```JSON
{
    "version": 1,
    "formatters":{
        "default": {
            "class": "logging.Formatter",
            "format": "LEVEL: %(levelname)s TIME: %(asctime)s FILENAMEL %(filename)s MODULE: %(module)s MESSAGES: %(message)s \n"
        },
        "slackFormatter": {
            "class": "src.utils.logger.SlackFormatter"
        }
    },
    "handlers" : {
        "console": {
            "class": "logging.StreamHandler",
            "level": "NOTSET",
            "formatter": "default"
        },
        "slack": {
            "class": "src.utils.logger.SlackHandler",
            "level": "ERROR",
            "formatter": "slackFormatter"
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "./src/development-logs.log",
            "level": "DEBUG",
            "formatter": "default"
        }
    },
    "loggers": {
        "": {
            "handlers": [
                "console", "slack", "file"
            ],
            "level": "NOTSET"
        }
    }
} 
```
*Environment Variable Swappable*: No

*Development Environment Behaviour*: If not specified, logging will be shut off and messages will be printed to console instead

*Production Environment Behaviour*: If not specified, logging will be shut off and messages will be printed to console instead. It is highly recommended you configure the logging for the production environment (see logging section)

```ML_PROVIDERS```

*Description*: A string list of ML Providers to be used to process the text. The items must be the lower case class names of the implemented MLProvider (See relevant section)

*Environment Variable Swappable*: No

*Development Environment Behaviour*:  The Google Natural Language service is enabled by default if this configuration value isn't set. In this case you will need to set up a projet on GCP, enable this service, create a service account and download the credentials which can be refrenced by the GOOGLE_APPLICATION_CREDENTIALS environment variable. See the [google docs](https://cloud.google.com/natural-language/) on this.

*Production Environment Behaviour*: The application will not start if this configuration is not set 


```ASGARD_SLACK_URL``` (<b> Environment Variable Only </b>)

*Description*: The webhook slack url which will be used by the logging slack handler to post logs to slack (See relavent section)

*Behavior*: There is no specific behavior relevant to the different environments but if the slack handler is configured in the ```LOGGING_CONFIG``` then it must be set or the application will not start 

### Running Asgard

Once you are finished providing the configurations listed above, navigate to the asgard directory and then 

```sh
$ python application.py
```

Asgard is now up and running, listening to the ```CONSUMER_TOPIC``` topic and consuming messages , processing them using the ```ML_PROVIDERS``` and the producing the output using the ```PRODUCER_SCHEMA``` to the ```PRODUCER_TOPIC```

If you are in development mode, time taken to process a message will be printed in the terminal 

### Seeing if it works 

You can see if Asgard is working correctly or not by running the producer simulator. You can do this using this command

```sh
$ python tests/simulate_producer.py <optional: num_messages> <broker> <schema_registry> <schema_path> <topic>
```

For example for an infinite producer 

```sh
$ python tests/simulate_producer.py "localhost:9092" "http://localhost:8081" "./src/schemas/data_input.avsc" "text_data_to_be_processed"
```

or for a producer which only produces 10 messages 

```sh
$ python tests/simulate_producer.py 10 "localhost:9092" "http://localhost:8081" "./src/schemas/data_input.avsc" "text_data_to_be_processed"
```

This producer will produce messages with the poem 

```txt
Do not go gentle into that good night,
Old age should burn and rave at close of day;
Rage, rage against the dying of the light.

Though wise men at their end know dark is right,
Because their words had forked no lightning they
Do not go gentle into that good night.

Good men, the last wave by, crying how bright
Their frail deeds might have danced in a green bay,
Rage, rage against the dying of the light.

Wild men who caught and sang the sun in flight,
And learn, too late, they grieved it on its way,
Do not go gentle into that good night.

Grave men, near death, who see with blinding sight
Blind eyes could blaze like meteors and be gay,
Rage, rage against the dying of the light.

And you, my father, there on the sad height,
Curse, bless, me now with your fierce tears, I pray.
Do not go gentle into that good night.
Rage, rage against the dying of the light.
```

### Sending Data to Asgard 

Asgard currently expects data according to the following Avro Schema 

```JSON
{
    "namespace": "cortex.streamprocessors.asgard",
    "type": "record",
    "name": "InputData",
    "doc": "This schema is used to deserialize asgard data processesing requests",
    "fields": [
        {"name": "uid", "type": ["string", "long"]},
        {"name": "data", "type": {
            "name": "items", "type": "array", "items": {
                "name": "item",
                "type": "record",
                "fields": [
                    {"name": "uid", "type": ["null", "string", "long"], "default": null},
                    {"name": "text", "type": "string"}
                ]
              }
            }
        }
    ]
}
```

This is an example of a valid message to Asgard

```JSON
{
    "uid": "Arbitrary unique identifier which upsteam/downstream producers/consumers can use as a refrence",
    "data": [
        {
            "uid": "Arbitrary unique identifier which the producer can use as a refrence",
            "text": "Text to be processed"
        }
    ] 
}
```

#### What is UID ?

The UID field is not used by Asgard at all. It is there so that the upstream and downstream applications can use it as a foreign key to relate the processed data to whatever arbitrary relationship they have.

### Recieving Data From Asgard

Asgard will produce a message containing the processed data according to the following schema. This can be changed to reflect your needs. However this is the default provided 

```JSON

{
    "namespace": "cortex.streamprocessors.asgard",
    "type": "record",
    "name": "OutputData",
    "doc": "This schema is used to serialize processed data by asgard",
    "fields": [
        {"name": "uid", "type": ["string", "long"]},
        {"name": "data", "type": {
                "name": "processedText",
                "type": "array",
                "items": {
                    "name": "providersProcessedText",
                    "type": "array",
                    "items": {
                        "name": "processedTextProvider",
                        "type": "record",
                        "fields": [
                            { "name": "uid", "type": ["string", "null"]},
                            { "name": "text", "type": "string"},
                            { "name": "language", "type": "string"},
                            { "name": "sentimentScore", "type": "double"},
                            { "name": "magnitudeScore", "type": "double" },
                            { "name": "provider", "type": "string"},
                            { "name": "sentences", "type": {
                                    "name": "processedSentences",
                                    "type": "array",
                                    "items": {
                                        "name": "processedSentence",
                                        "type": "record",
                                        "fields": [
                                            {"name": "text", "type": "string"},
                                            {"name": "sentimentScore", "type": "double"},
                                            {"name": "magnitudeScore", "type": "double"}
                                        ]
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }
    ]
}
```

An example of the structure of a message produced by Asgard according to this schema 

```JSON
{
    "uid": "Arbitrary unique identifier which upsteam/downstream producers/consumers can use as a refrence",
    "data":[
        [ 
            {
                "uid":"Arbitrary unique identifier which upsteam/downstream producers/consumers can use as a refrence",
                "text": "The original text sent to Asgard to process",
                "language": "Detected language of the text",
                "sentimentScore": "Analyze sentiment score",
                "magnitudeScore": "Analyzed magnitude score",
                "provider": "The name of the ML provider who processed this data",
                "sentences":[
                    {
                        "text": "Text of a extracted sentence in the text",
                        "sentimentScore": "The sentiment score analyzed for this sentence",
                        "magnitudeScore": "The magnitude score analyzed for this sentence"
                    }
                ]
           }
        ]
    ]
}
```

#### Understanding this data

Asgard will produce a double array of the processed text. You can think of this as a matrix where the rows are the text provided in the array of the input message and the columns are the outputs different ML Providers which have been enabled to process the data. 

<table>
   <thead>
    <th> Text Index </th>
    <th> ML Provider 1 </th> 
    <th> ML Provider 2 </th>
   </thead>
   <tbody>
     <tr>
       <td>1</td>
       <td>{
                "uid":"Arbitrary unique identifier which upsteam/downstream producers/consumers can use as a refrence",
                "text": "The original text sent to Asgard to process",
                "language": "Detected language of the text",
                "sentimentScore": "Analyze sentiment score",
                "magnitudeScore": "Analyzed magnitude score",
                "provider": "ML Provider 1",
                "sentences":[
                    {
                        "text": "Text of a extracted sentence in the text",
                        "sentimentScore": "The sentiment score analyzed for this sentence",
                        "magnitudeScore": "The magnitude score analyzed for this sentence"
                    }
                ]
           }
        </td>
        <td>
            {
                "uid":"Arbitrary unique identifier which upsteam/downstream producers/consumers can use as a refrence",
                "text": "The original text sent to Asgard to process",
                "language": "Detected language of the text",
                "sentimentScore": "Analyze sentiment score",
                "magnitudeScore": "Analyzed magnitude score",
                "provider": "ML Provider 2",
                "sentences":[
                    {
                        "text": "Text of a extracted sentence in the text",
                        "sentimentScore": "The sentiment score analyzed for this sentence",
                        "magnitudeScore": "The magnitude score analyzed for this sentence"
                    }
                ]
           }
        </td>
     </tr>
   </tbody>
</table>

Translated to a JSON Structure 
```JSON 
[
    [
      {
                "uid":"Arbitrary unique identifier which upsteam/downstream producers/consumers can use as a refrence",
                "text": "The original text sent to Asgard to process",
                "language": "Detected language of the text",
                "sentimentScore": "Analyze sentiment score",
                "magnitudeScore": "Analyzed magnitude score",
                "provider": "ML Provider 1",
                "sentences":[
                    {
                        "text": "Text of a extracted sentence in the text",
                        "sentimentScore": "The sentiment score analyzed for this sentence",
                        "magnitudeScore": "The magnitude score analyzed for this sentence"
                    }
                ]
        },
        {
                "uid":"Arbitrary unique identifier which upsteam/downstream producers/consumers can use as a refrence",
                "text": "The original text sent to Asgard to process",
                "language": "Detected language of the text",
                "sentimentScore": "Analyze sentiment score",
                "magnitudeScore": "Analyzed magnitude score",
                "provider": "ML Provider 2",
                "sentences":[
                    {
                        "text": "Text of a extracted sentence in the text",
                        "sentimentScore": "The sentiment score analyzed for this sentence",
                        "magnitudeScore": "The magnitude score analyzed for this sentence"
                    }
                ]
           }
    ]
]
```


## Implementing an ML Provider 

This can be done in a few simple steps 

Step 1: Implement a class in the [providers folder](/src/machine_learning_providers/providers)

Step 2: Follow the template of the google.py provided which configures a MLProvider for the Google Natural Language API

```python
import traceback
from .base_provider import MLProvider
from google.cloud import language #pylint: disable=no-name-in-module
from google.cloud.language import enums #pylint: disable=no-name-in-module
from google.cloud.language import types #pylint: disable=no-name-in-module
from google.api_core.exceptions import GoogleAPICallError, RetryError #pylint: disable=no-name-in-module
class Google(MLProvider):
    def __init__(self, **kwargs):
        """
        Instatiate the Google Natural Language API ML Providor 
        """
        super().__init__(**kwargs)
        if "logging_enabled" in kwargs:
            del kwargs["logging_enabled"]
        self.__client = language.LanguageServiceClient(
            **kwargs
        )
    def process(self, text):
        """
        Process textual data

        Parameters
        ----------
        text: str
           The textual data to be processed
        
        Returns
        -------
        dict
           The processed data
        """

        document = types.Document( #pylint: disable=no-member
            content = text,
            type = enums.Document.Type.PLAIN_TEXT
        )
        
        try:
            sentiment = self.__client.analyze_sentiment(document=document)
        except GoogleAPICallError as e:
            super().__log_msg(
                "An error occured with the Google Natural Language API Call {}". format(e),
                "Text which was to be processed {}".format(text),
                "Stack trace {}".format(traceback.format_exc()),
                delimeter="\n",
                level="ERROR"
            )
            return e
        except ValueError as e:
            super().__log_msg(
                "Bad arguments provided {}".format(e),
                "Text which was to be processed {}".format(text),
                "Stack trace {}".format(traceback.format_exc()),
                delimeter="\n",
                level="ERROR"
            )
            return e
        except Exception as e:
            super().__log_msg(
                "An unknown error has occured {}".format(e),
                "Text which was to be processed {}".format(text),
                "Stack trace {}".format(traceback.format_exc()),
                delimeter="\n",
                level="ERROR"
            )
            return e
        
        data = {}
        data["text"] = text
        data["language"] = sentiment.language
        data["sentimentScore"] = sentiment.document_sentiment.score
        data["magnitudeScore"] = sentiment.document_sentiment.magnitude
        data["provider"] = "google"
        data["sentences"] = [
            {
            "text": sentence.text.content, 
            "sentimentScore": sentence.sentiment.score,
            "magnitudeScore": sentence.sentiment.magnitude
            } for sentence in sentiment.sentences ]
        
        return data
```

All MLProvider classes must 

1. Inherit the MLProvider base class 
2. Implement a process method which takes a single argument ```text``` produces a structure that is compliant with your producer schema

Step 3: Import it in the [src/machine_learning_providers/providers/__init__.py](/src/machine_learning_providers/providers/__init__.py)

```python
from .base_provider import MLRegistry
from .base_provider import MLProvider
from .google import Google
```

Step 4: Enable it by adding it's lower case name to the ```ML_PROVIDERS``` list configuration

```JSON
{
    "ML_PROVIDERS": [
        "google"
    ]
}
```

That's it ! All Processors which we call ML Providers can be implemented in this way. Nothing to import and no extra code to write to use. Asgard will automatically call this class to process the data. Providers can simply be swapped or added by adding them or removing them from the ```ML_PROVIDERS``` list


## Logging

More information on this soon !


















