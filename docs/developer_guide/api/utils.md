# Utilities API

This page covers the utility modules: JSON parsing, Parquet I/O, and logging.

---

## JSON Utilities

**Module:** `argos.utils.jsonutils`

### `loadJSON(jsonData)`

Flexible JSON loader that accepts multiple input formats.

```python
from argos.utils.jsonutils import loadJSON

data = loadJSON("/path/to/file.json")          # From file path
data = loadJSON('{"key": "value"}')            # From JSON string
data = loadJSON(open("file.json"))             # From file object
data = loadJSON({"key": "value"})              # From dict (passthrough)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `jsonData` | `str`, `dict`, or file-like | JSON source |

**Returns:** `dict`

**Raises:** `ValueError` if format is unrecognized or file not found.

---

### `processJSONToPandas(jsonData, nameColumn, valueColumn)`

Flattens JSON into a 2-column DataFrame.

| Parameter | Type | Description |
|-----------|------|-------------|
| `jsonData` | `dict` | JSON data to flatten |
| `nameColumn` | `str` | Name for the path column |
| `valueColumn` | `str` | Name for the value column |

**Returns:** `DataFrame` with path and value columns. Lists are expanded as `name_0`, `name_1`, etc.

---

### `convertJSONtoPandas(jsonData, nameColumn, valueColumn)`

Deep recursive JSON to Pandas conversion using dot notation.

```python
from argos.utils.jsonutils import convertJSONtoPandas

df = convertJSONtoPandas(
    {"sensor": {"temp": 25.0, "location": {"lat": 32.0}}},
    "path", "value"
)
# path                | value
# sensor.temp         | 25.0
# sensor.location.lat | 32.0
```

Fully flattens all nested dicts and lists until all values are scalars.

---

## Parquet Utilities

**Module:** `argos.utils.parquetUtils`

### `writeToParquet(parquetFile, data, datetimeColumn='datetime')`

Creates a new Parquet file from a DataFrame.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `parquetFile` | `str` | - | Output file path |
| `data` | `DataFrame` | - | Pandas or Dask DataFrame |
| `datetimeColumn` | `str` | `'datetime'` | Column to use as datetime index |

**Returns:** `True` on success.

**Behavior:**

1. Converts to Pandas if needed
2. Creates a Dask DataFrame
3. Sets datetime column as index
4. Writes with fastparquet engine

---

### `appendToParquet(toBeAppended, additionalData, datetimeColumn='datetime')`

Appends data to an existing Parquet file.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `toBeAppended` | `str` | - | Existing Parquet file path |
| `additionalData` | `DataFrame` | - | New data to append |
| `datetimeColumn` | `str` | `'datetime'` | Datetime column name |

**Behavior:**

1. Loads existing file with Dask
2. Concatenates with new data
3. Auto-repartitions if:
    - Last partition exceeds 100MB
    - Total partitions exceed 10
4. Writes to temporary file, then atomic rename

---

## Logging

**Module:** `argos.utils.logging.helpers`

### Custom Log Level

pyArgos defines a custom `EXECUTION` log level:

| Level | Value | Use Case |
|-------|-------|----------|
| DEBUG | 10 | Detailed debugging |
| **EXECUTION** | **15** | **Step-by-step execution progress** |
| INFO | 20 | General information |

```python
logger.execution("Creating experiment directories")
```

---

### `initialize_logging(*logger_overrides, disable_existing_loggers=True)`

Sets up the logging system from configuration.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `*logger_overrides` | `dict` | - | Override configs (from `with_logger()`) |
| `disable_existing_loggers` | `bool` | `True` | Disable pre-existing loggers |

Reads config from `~/.pyargos/log/argosLogging.config`. Creates the directory if needed.

---

### `get_logger(instance, name=None)`

Get a logger for a class instance.

```python
logger = get_logger(self, "myMethod")
```

---

### `get_classMethod_logger(instance, name=None)`

Get a logger for a class method with qualified name.

```python
logger = get_classMethod_logger(self, "loadDevices")
# Logger name: "argos.manager.experimentManager.loadDevices"
```

---

### `with_logger(logger_name, level, handlers, propagate)`

Build a logger configuration dict for use as an override with `initialize_logging()`.

```python
override = with_logger("argos.kafka", level="DEBUG", handlers=["console"])
initialize_logging(override)
```

---

### `unify_all_logs_debug()`

Merges all logs to the root logger at DEBUG level. Useful for debugging.
