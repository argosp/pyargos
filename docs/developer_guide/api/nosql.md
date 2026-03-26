# NoSQL API (Cassandra & MongoDB)

**Module:** `argos.noSQLdask`

Dask-based interfaces for querying time-series data from Cassandra and MongoDB databases.

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
