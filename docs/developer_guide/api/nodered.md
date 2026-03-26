# Node-RED API

**Module:** `argos.nodered`

The Node-RED module provides a flow manager for interacting with Node-RED servers and custom nodes for data processing.

---

## Flow Manager

### `flowManagerHome`

**Module:** `argos.nodered.manager.flowManagerHome`

REST interface to a Node-RED server.

```python
from argos.nodered.manager.flowManagerHome import flowManagerHome

manager = flowManagerHome()
flows = manager.getFlows()
```

#### Properties

| Property | Default | Description |
|----------|---------|-------------|
| `_noderedServer` | `'127.0.0.1'` | Node-RED server hostname |
| `_noderedPort` | `1880` | Node-RED server port |

#### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `getConnectionString(task)` | `str` | Build endpoint URL for a given task |
| `getFlows()` | `dict` | GET `/flows` - retrieve current flow definitions |

---

## Custom Nodes

### `to_parquet` Node

**Module:** `argos.nodered.nodes.heraNodes`

A Node-RED node that writes message data to Parquet files.

**Category:** `argos`

#### Node Properties

| Property | Label | Default | Description |
|----------|-------|---------|-------------|
| `outputDirectory` | Output Directory | - | Directory for Parquet output |
| `timestampField` | Timestamp field | `"timestamp"` | Name of the timestamp field |
| `fileNameField` | Filename field | - | Field to use for per-entity file naming |
| `partitionaFields` | Partition on | - | Fields to partition by |

#### Behavior

```python
@node_red(category="argos", properties=...)
def to_parquet(node, msgList):
    ...
```

1. Receives a list of messages with `payload` data
2. Converts to a Pandas DataFrame
3. Partitions by year/month (or custom fields)
4. Writes per-entity Parquet files using Dask with fastparquet engine
5. Appends to existing files or creates new ones

---

### `add_document` Node

**Module:** `argos.nodered.nodes.tbNodes`

A simple ThingsBoard document transformation node.

**Category:** `argos`

#### Node Properties

| Property | Label | Description |
|----------|-------|-------------|
| `ProjectName` | Project Name | ThingsBoard project name |

#### Behavior

Converts the incoming payload to a lowercase string.
