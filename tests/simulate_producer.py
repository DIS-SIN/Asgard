
import sys
import os
import json
import hashlib
import time

from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer

if len(sys.argv) < 5:
    print("Usage: python tests/simulate_producer.py <broker> <schema_registry> <schema_path> <topic>")
else:
    topic = sys.argv[-1]
    schema_path = sys.argv[-2]
    schema_registry = sys.argv[-3]
    broker = sys.argv[-4]

with open(schema_path, "r", encoding = "utf-8") as f:
    schema = json.dumps(json.load(f))

producer = AvroProducer(
    {
        "bootstrap.servers": broker,
        "schema.registry.url": schema_registry
    },
    default_value_schema=avro.loads(schema)
)

poem = [
"""Do not go gentle into that good night,
Old age should burn and rave at close of day;
Rage, rage against the dying of the light.""",
"""Though wise men at their end know dark is right,
Because their words had forked no lightning they
Do not go gentle into that good night
""",
"""Good men, the last wave by, crying how bright
Their frail deeds might have danced in a green bay,
Rage, rage against the dying of the light.
""",
"""Wild men who caught and sang the sun in flight,
And learn, too late, they grieved it on its way,
Do not go gentle into that good nigh
""",
"""Grave men, near death, who see with blinding sight
Blind eyes could blaze like meteors and be gay,
Rage, rage against the dying of the light.
""",
"""And you, my father, there on the sad height,
Curse, bless, me now with your fierce tears, I pray.
Do not go gentle into that good night.
Rage, rage against the dying of the light
"""
]

while True:
    hash = hashlib.sha1()
    hash.update(str(time.time()).encode("utf-8"))
    hash = hash.hexdigest()
    msg = {
        "uid": "hash",
        "data": poem
    }
    producer.produce(
        topic = topic,
        value = msg
    )
    producer.flush()
    time.sleep(1)






