# ASGARD (NLP Stream Processor)

Asgard is an NLP stream processor providing a sentiment analysis service for the CSPS [Cortex](https://github.com/DIS-SIN/CORTEX) project.

Kafka messages containing the textual data to be processed by the Asgard service can be sent to any topic of choosing and the processed data will
be sent as a message to any other topic of choosing to be used by downstream consumers.

Messages are to be sent in the following format 

```JSON
{
    "uid": "Unique identifier which the upstream producer sets",
    "data": [
        "A list of textual data to be processed. This may be in french or english"
    ] 
}
```

Asgard will produce a message on the selected topic
```JSON
{
    "uid": "The unique identifyer set in the consumed message",
    "data":[
        {
            "text": "The original text",
            "sentimentScore": "The overall sentiment score",
            "magnitudeScore": "The overall magnitude score",
            "language": "The detected language of the text",
            "sentences" : [
                {
                    "text": "A sentence",
                    "sentimentScore": "It's sentiment score",
                    "magnitudeScore": "It's magnitude score"
                }
            ] 
        }
    ]
}
```
Messages are deserialized and serialized using Apache Avro and the Confluent Schema Registry. 

More documentation on configuration coming soon!
