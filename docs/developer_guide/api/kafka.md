# Kafka Consumer API

**Module:** `argos.kafka.consumer`

The Kafka consumer module reads device telemetry from Kafka topics and persists it as Parquet files — the primary data ingestion path during experiment execution.

---

## Role in the System

```
Devices ──> Node-RED ──> Kafka ──> [this module] ──> Parquet files
                                   consume_topic()
                                   consume_topic_server()
```

Each device type gets its own Kafka topic (created by the CLI's `kafka_createTopics`). This module provides two consumer functions:

- `consume_topic` — one-shot: drain all available messages, write to Parquet, exit
- `consume_topic_server` — continuous: poll in an infinite loop with configurable delay

---

## Class Dependency

![Diagram](../../images/diagrams/developer_guide_api_kafka_0_c0ec7f85.svg)

<!-- mermaid source (for editing, paste into mermaid.live):
```mermaid
classDiagram
    class consume_topic {
        +topic : str
        +dataDirectory : str
    }
    class consume_topic_server {
        +topic : str
        +dataDirectory : str
        +delayInSeconds : float
    }
    class KafkaConsumer {
        +poll()
        +commit()
        +close()
    }
    class writeToParquet {
        +parquetFile
        +data
    }
    class appendToParquet {
        +toBeAppended
        +additionalData
    }

    consume_topic --> KafkaConsumer : creates
    consume_topic --> writeToParquet : new file
    consume_topic --> appendToParquet : existing file
    consume_topic_server --> KafkaConsumer : creates
    consume_topic_server --> writeToParquet : new file
    consume_topic_server --> appendToParquet : existing file
```
-->

---

## Swimlane: One-Shot Consumption

![Diagram](../../images/diagrams/developer_guide_api_kafka_1_edb3ed5c.svg)

<!-- mermaid source (for editing, paste into mermaid.live):
```mermaid
sequenceDiagram
    actor CLI
    participant Fn as consume_topic()
    participant KC as KafkaConsumer
    participant PQ as Parquet Utils

    CLI->>Fn: consume_topic("Sensor", "data/")
    Fn->>KC: KafkaConsumer("Sensor", bootstrap=127.0.0.1:9092)

    loop Until no messages
        Fn->>KC: poll(timeout_ms=12000)
        KC-->>Fn: message batch (up to 5000)
        Note over Fn: Append to list L
    end

    Fn->>KC: close()

    alt L is not empty
        Note over Fn: DataFrame(L)
        Note over Fn: Add datetime column (Israel TZ)
        Note over Fn: Cast Temperature, RH to float64
        Note over Fn: Sort by timestamp, drop duplicates

        alt data/Sensor.parquet exists
            Fn->>PQ: appendToParquet(file, data)
        else New file
            Fn->>PQ: writeToParquet(file, data)
        end
    end
```
-->

## Swimlane: Server-Mode Consumption

![Diagram](../../images/diagrams/developer_guide_api_kafka_2_5d2a613a.svg)

<!-- mermaid source (for editing, paste into mermaid.live):
```mermaid
sequenceDiagram
    actor CLI
    participant Fn as consume_topic_server()
    participant KC as KafkaConsumer
    participant PQ as Parquet Utils

    CLI->>Fn: consume_topic_server("Sensor", "data/", 300)
    Fn->>KC: KafkaConsumer("Sensor", bootstrap=127.0.0.1:9092)

    loop Forever
        Note over Fn: Poll cycle

        loop Until no messages or >10000 total
            Fn->>KC: poll(timeout_ms=12000)
            KC-->>Fn: message batch
        end

        Fn->>KC: commit()

        alt Messages received
            Note over Fn: DataFrame → datetime → sort
            Fn->>PQ: write or append to Parquet
        end

        alt Received >= max_poll_records
            Note over Fn: More data available, poll again immediately
        else Received < max_poll_records
            Note over Fn: Wait delayInSeconds (check every 5s)
        end
    end
```
-->

---

## Implementation Notes

**Consumer configuration** (hardcoded):

| Setting | Value | Notes |
|---------|-------|-------|
| `bootstrap_servers` | `127.0.0.1:9092` | Single broker |
| `group_id` | `'1'` | All consumers share one group |
| `auto_offset_reset` | `'earliest'` | Start from beginning on first run |
| `max_poll_records` | `5000` | Batch size per poll |
| `value_deserializer` | JSON (ASCII) | Messages are JSON strings |

**Data transformations:**

1. JSON messages → Pandas DataFrame
2. `timestamp` (ms since epoch) → `datetime` column (Israel timezone)
3. `Temperature`, `RH` fields → `float64` (if present)
4. Sort by timestamp, drop duplicates (one-shot mode only)

**Known limitations:**

- Broker address and group ID are hardcoded
- Deduplication only works within a single consumer run, not across restarts
- No handling of out-of-order messages across partitions
- Server mode checks every 5 seconds during delay, but does not react to new messages during the wait

---

## Functions

### consume_topic

::: argos.kafka.consumer.consume_topic
    options:
      show_root_heading: true
      heading_level: 4

---

### consume_topic_server

::: argos.kafka.consumer.consume_topic_server
    options:
      show_root_heading: true
      heading_level: 4
