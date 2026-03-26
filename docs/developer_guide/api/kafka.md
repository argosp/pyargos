# Kafka Consumer API

**Module:** `argos.kafka.consumer`

The Kafka consumer module provides functions for reading messages from Kafka topics and writing them to Parquet files.

---

## Functions

### `consume_topic`

```python
from argos.kafka.consumer import consume_topic

consume_topic(topic, dataDirectory)
```

Consumes all available messages from a Kafka topic and writes them to a Parquet file.

| Parameter | Type | Description |
|-----------|------|-------------|
| `topic` | `str` | Kafka topic name to consume from |
| `dataDirectory` | `str` | Directory to save the Parquet file |

**Behavior:**

1. Creates a `KafkaConsumer` connected to `127.0.0.1:9092`
2. Polls with `max_poll_records=5000` and 12-second timeout
3. Reads until no messages are returned
4. Converts messages from JSON to a Pandas DataFrame
5. Adds timezone-aware datetime column (Israel timezone)
6. Casts numeric fields (Temperature, RH)
7. Removes duplicate timestamps
8. Writes to `{dataDirectory}/{topic}.parquet`

**Output:** Creates or appends to `{topic}.parquet` in the data directory.

---

### `consume_topic_server`

```python
from argos.kafka.consumer import consume_topic_server

consume_topic_server(topic, dataDirectory, delayInSeconds)
```

Continuous server-mode consumer that polls periodically.

| Parameter | Type | Description |
|-----------|------|-------------|
| `topic` | `str` | Kafka topic name |
| `dataDirectory` | `str` | Directory for Parquet output |
| `delayInSeconds` | `float` | Pause between poll cycles |

**Behavior:**

- Runs in an infinite loop
- Each cycle polls and accumulates messages
- Breaks the inner loop when:
    - No new messages (0 received)
    - Total exceeds 10,000 messages
- Commits offsets after each batch
- Waits `delayInSeconds` between cycles (checks every 5s)
- Ideal for continuous data ingestion in production

---

## Consumer Configuration

| Setting | Value | Description |
|---------|-------|-------------|
| `bootstrap_servers` | `127.0.0.1:9092` | Kafka broker address |
| `group_id` | `'1'` | Consumer group ID |
| `auto_offset_reset` | `'earliest'` | Start from beginning if no offset |
| `max_poll_records` | `5000` / `12000` | Batch size per poll |

---

## Data Transformation Pipeline

```
Raw Kafka Message (bytes)
    → JSON decode
    → Pandas DataFrame
    → Add 'datetime' column (Israel timezone)
    → Cast 'Temperature', 'RH' to float
    → Drop duplicate timestamps
    → Write/Append to Parquet
```
