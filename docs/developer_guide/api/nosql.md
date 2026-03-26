# NoSQL API (Cassandra & MongoDB)

**Module:** `argos.noSQLdask`

Dask-based interfaces for querying time-series data from Cassandra and MongoDB databases. These are used for accessing historical telemetry stored in ThingsBoard's Cassandra backend or in MongoDB collections.

---

## Role in the System

```
ThingsBoard ──stores telemetry──> Cassandra (ts_kv_cf)
                                      │
                                      ▼
                               CassandraBag ──> Dask bag ──> DataFrame
                                  (parallel partitioned reads)

MongoDB ──stores collections──> MongoBag ──> Dask bag ──> DataFrame
                                  (parallel partitioned reads)
```

Both classes follow the same pattern: split a time range into partitions, read each partition in parallel using Dask bags, and return the combined result as a Pandas DataFrame.

---

## Class Dependency

![Diagram](../../images/diagrams/developer_guide_api_nosql_0_7c5ec7e0.svg)

<!-- mermaid source (for editing, paste into mermaid.live):
```mermaid
classDiagram
    class CassandraBag {
        +IP : str
        +db_name : str
        +set_name : str
        +deviceID : str
        +keys : list
        +bag(start_time, end_time, npartitions) Bag
        +getDataFrame(start_time, end_time, npartitions) DataFrame
    }

    class MongoBag {
        +db_name : str
        +collection_name : str
        +timestamp_field : str
        +bag(start_time, end_time, periods, freq) Bag
        +read_datetime_interval_from_collection(args) list
    }

    class Cluster {
        <<cassandra-driver>>
        +connect(keyspace)
    }

    class MongoClient {
        <<pymongo>>
    }

    class dask_bag {
        <<dask>>
        +from_sequence()
        +map()
        +flatten()
        +to_dataframe()
    }

    CassandraBag --> Cluster : connects per partition
    CassandraBag --> dask_bag : creates
    MongoBag --> MongoClient : connects per partition
    MongoBag --> dask_bag : creates
```
-->

---

## Swimlane: Query Cassandra Telemetry

![Diagram](../../images/diagrams/developer_guide_api_nosql_1_e12a03a1.svg)

<!-- mermaid source (for editing, paste into mermaid.live):
```mermaid
sequenceDiagram
    actor User
    participant CB as CassandraBag
    participant Dask as Dask Bag
    participant Cass as Cassandra

    User->>CB: CassandraBag(deviceID, IP)
    CB->>Cass: Query ts_kv_latest_cf for available keys
    Cass-->>CB: keys list (e.g., ["Temperature", "RH"])

    User->>CB: getDataFrame("2024-01-01", "2024-01-31")
    CB->>CB: Convert date strings to ms timestamps
    CB->>CB: Split time range into npartitions intervals
    CB->>CB: Split each interval into monthly Cassandra partitions

    CB->>Dask: from_sequence(partition_times)
    Note over Dask: Parallel execution

    loop For each partition (parallel)
        Dask->>Cass: SELECT ts, key, dbl_v FROM ts_kv_cf<br/>WHERE device_id=X AND key=K<br/>AND partition=P AND ts BETWEEN start, end
        Cass-->>Dask: rows
    end

    Dask-->>CB: combined results
    CB->>CB: pivot_table(index='ts', columns='key', values='dbl_v')
    CB-->>User: DataFrame (rows=timestamps, cols=metrics)
```
-->

## Swimlane: Query MongoDB Collection

![Diagram](../../images/diagrams/developer_guide_api_nosql_2_5e95baf3.svg)

<!-- mermaid source (for editing, paste into mermaid.live):
```mermaid
sequenceDiagram
    actor User
    participant MB as MongoBag
    participant Dask as Dask Bag
    participant Mongo as MongoDB

    User->>MB: MongoBag("mydb", "sensor_data")
    User->>MB: bag("2024-01-01", "2024-01-31", periods=20)

    MB->>MB: Create date_range with 20 intervals (Israel TZ)

    MB->>Dask: from_sequence(partition_intervals)
    Note over Dask: Parallel execution

    loop For each interval (parallel)
        Dask->>Mongo: collection.find({timestamp: {$gte: start, $lte: end}})
        Mongo-->>Dask: document list
    end

    Dask-->>User: Dask bag of documents
    Note over User: .to_dataframe().compute() for DataFrame
```
-->

---

## Implementation Notes

**Cassandra-specific:**

- Designed for ThingsBoard's `ts_kv_cf` table schema: `(entity_type, entity_id, key, partition, ts) → dbl_v`
- Cassandra partitions are monthly — the code splits time ranges at month boundaries to align with partition keys
- A new Cluster/Session is created **per partition read** (no connection pooling)
- Only `dbl_v` (double values) are read; string/boolean/long values are ignored

**MongoDB-specific:**

- Time range queries use string comparison on the timestamp field (format: `%Y-%-m-%-d %-H:%-M:%-S.%f`)
- Additional query filters can be passed as `**kwargs` to `bag()`
- Uses `pymongo.MongoClient()` context manager per partition (default localhost)

**Shared pattern:**

- Both classes use `dask.bag.from_sequence().map().flatten()` for parallelism
- The number of partitions controls parallelism — more partitions = more parallel reads
- Neither class handles connection failures or retries

---

## CassandraBag

::: argos.noSQLdask.cassandraBag.CassandraBag
    options:
      show_root_heading: true
      heading_level: 3
      members:
        - __init__
        - bag
        - getDataFrame

---

## MongoBag

::: argos.noSQLdask.mongoBag.MongoBag
    options:
      show_root_heading: true
      heading_level: 3
      members:
        - __init__
        - db_name
        - collection_name
        - timestamp_field
        - bag
        - read_datetime_interval_from_collection
