# Installation & Setup

## Prerequisites

- Python 3.7+
- [Anaconda](https://www.anaconda.com/) (recommended)

## Installation

### 1. Create a virtual environment

```bash
conda create -n Argos python=3.7
conda activate Argos
```

### 2. Install dependencies

```bash
pip install paho-mqtt numpy pandas urllib3 requests
```

### 3. Optional dependencies

Depending on your use case, install additional packages:

=== "ThingsBoard"

    ```bash
    pip install tb_rest_client
    ```

=== "Kafka"

    ```bash
    pip install kafka-python
    ```

=== "NoSQL (Cassandra)"

    ```bash
    pip install cassandra-driver dask
    ```

=== "NoSQL (MongoDB)"

    ```bash
    pip install pymongo dask
    ```

=== "Node-RED Parquet nodes"

    ```bash
    pip install dask fastparquet
    ```

### 4. Add pyargos to your PYTHONPATH

```bash
export PYTHONPATH=$PYTHONPATH:/path/to/pyargos
```

!!! tip
    Add this line to your `~/.bashrc` or `~/.zshrc` to make it permanent.

### 5. Activate the environment

```bash
conda activate Argos
```

## Logging Configuration

pyArgos uses a custom logging system with an `EXECUTION` log level (between DEBUG and INFO). The default configuration is loaded from:

```
~/.pyargos/log/argosLogging.config
```

If this file doesn't exist, pyArgos uses a sensible default configuration. See [Configuration Reference](configuration.md) for details on customizing logging.

## Verifying the Installation

```python
import argos
print(argos.__version__)  # Should print 1.2.3
```
