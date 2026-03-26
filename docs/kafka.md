# Kafka Integration

pyArgos uses Apache Kafka for streaming data from IoT devices to storage.

## Prerequisites

### Install Kafka and Zookeeper

Follow the [Apache Kafka quickstart](https://kafka.apache.org/quickstart) to install and start Kafka with Zookeeper.

### Install ksqlDB (optional)

[ksqlDB](https://docs.ksqldb.io/en/latest/operate-and-deploy/installation/installing/) provides SQL-like stream processing:

```bash
docker pull confluentinc/ksqldb-server
```

Optionally install the CLI:

```bash
docker pull confluentinc/ksqldb-cli
```

## Verifying the Installation

### Create the management topic

```bash
<path-to-confluent>/bin/kafka-topics.sh \
    --create --topic argosManagement \
    --bootstrap-server 127.0.0.1:9092
```

### List topics

```bash
<path-to-confluent>/bin/kafka-topics.sh \
    --list --bootstrap-server 127.0.0.1:9092
```

## Sending and Receiving Messages

### Send messages via command line

```bash
<path-to-confluent>/bin/kafka-console-producer.sh \
    --bootstrap-server localhost:9092 \
    --topic argosManagement
```

Send from a file:

```bash
<path-to-confluent>/bin/kafka-console-producer.sh \
    --bootstrap-server localhost:9092 \
    --topic argosManagement < inFile
```

### Receive messages

```bash
<path-to-confluent>/bin/kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic argosManagement
```

## Using Kafka with pyArgos

### Creating Topics

pyArgos automatically creates Kafka topics for each device type:

```bash
python -m argos.bin.trialManager --kafkaCreateTopics
```

This reads the experiment configuration and creates one topic per entity type.

### Consuming Data

#### Single topic consumer

```python
from argos.kafka.consumer import consume_topic

consume_topic("Sensor", "/path/to/data")
```

#### Multi-threaded consumers

The CLI starts a consumer thread per device type:

```bash
python -m argos.bin.trialManager --kafkaRunConsumers
```

#### Server-mode consumers

For continuous operation with periodic polling:

```bash
python -m argos.bin.trialManager --kafkaRunConsumersServer --delay 5min
```

### Data Flow

```
IoT Devices
    |
    v (MQTT/UDP)
Node-RED
    |
    v
Kafka Topics (one per device type)
    |
    v
pyArgos Consumer
    |
    v
Parquet Files (in data/ directory)
```

Messages are consumed from Kafka and written to Parquet files in the experiment's `data/` directory, organized by device type.
