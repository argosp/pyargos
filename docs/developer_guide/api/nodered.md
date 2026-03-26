# Node-RED API

**Module:** `argos.nodered`

The Node-RED module provides integration with [Node-RED](https://nodered.org/) for device data routing and normalization.

---

## Role in the System

Node-RED sits between physical devices and Kafka in the data pipeline:

```
Devices ──MQTT/UDP──> Node-RED ──> Kafka topics
                         │
                    ┌────┴─────┐
                    │ pyArgos  │
                    │ nodered  │
                    │ module   │
                    ├──────────┤
                    │ manager/ │  REST client to query flows
                    │ nodes/   │  Custom Node-RED nodes:
                    │          │  - to_parquet (write data)
                    │          │  - add_document (TB transform)
                    └──────────┘
```

Node-RED performs the **normalization** step:

- Adds a consistent timestamp to each message
- Parses device-specific raw data formats
- Routes messages to the correct Kafka topic by device type

---

## Module Structure

```
argos/nodered/
    manager/
        flowManagerHome.py    # REST client to Node-RED server
    nodes/
        heraNodes.py          # to_parquet: write messages to Parquet
        tbNodes.py            # add_document: ThingsBoard payload transform
```

## Class Dependency

![Diagram](../../images/diagrams/developer_guide_api_nodered_0_9b48df29.svg)

<!-- mermaid source (for editing, paste into mermaid.live):
```mermaid
classDiagram
    class flowManagerHome {
        -_noderedServer : str
        -_noderedPort : int
        +__init__(nodeRedServer)
        +getConnectionString(task) str
        +getFlows() dict
    }

    class requests {
        <<external>>
        +get(url) Response
    }

    flowManagerHome --> requests : HTTP GET

    note for flowManagerHome "Connects to Node-RED REST API\nDefault: 127.0.0.1:1880"
```
-->

---

## Swimlane: Get Flows from Node-RED

![Diagram](../../images/diagrams/developer_guide_api_nodered_1_9f4a9064.svg)

<!-- mermaid source (for editing, paste into mermaid.live):
```mermaid
sequenceDiagram
    actor User
    participant FM as flowManagerHome
    participant NR as Node-RED Server

    User->>FM: flowManagerHome("192.168.1.10")
    User->>FM: getFlows()
    FM->>FM: getConnectionString("flows")
    Note over FM: "http://192.168.1.10:1880/flows"
    FM->>NR: HTTP GET /flows
    alt Status 200
        NR-->>FM: JSON flow definitions
        FM-->>User: dict
    else Status != 200
        FM-->>User: raise ValueError
    end
```
-->

---

## Implementation Notes

- The flow manager is a **read-only** client — it queries flows but does not modify them
- The Node-RED server address is configurable; port is hardcoded to **1880**
- The `to_parquet` custom node uses **Dask with fastparquet** for efficient writes
- The `add_document` node is a simple payload transformation (currently converts to lowercase)

---

## Flow Manager

### flowManagerHome

::: argos.nodered.manager.flowManagerHome.flowManagerHome
    options:
      show_root_heading: true
      heading_level: 4
      members:
        - __init__
        - getConnectionString
        - getFlows
