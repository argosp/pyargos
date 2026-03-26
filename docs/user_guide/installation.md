# Installation & Setup

## Prerequisites

- Python 3.9+
- [Anaconda](https://www.anaconda.com/) or any Python virtual environment manager

## Quick Install (with Make)

```bash
git clone git@github.com:argosp/pyargos.git
cd pyargos
make install
```

This will:

1. Install all Python dependencies from `requirements.txt`
2. Prompt to add `PYTHONPATH` to your `~/.bashrc` (or `~/.zshrc` for zsh users)

After installation, open a new terminal or run `source ~/.bashrc` to activate.

## Manual Install

### 1. Clone the repository

```bash
git clone git@github.com:argosp/pyargos.git
cd pyargos
```

### 2. Create a virtual environment

=== "Conda"

    ```bash
    conda create -n Argos python=3.11
    conda activate Argos
    ```

=== "venv"

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add pyargos to your PYTHONPATH

```bash
export PYTHONPATH="/path/to/pyargos:$PYTHONPATH"
```

To make this permanent, use the Makefile helper:

```bash
make env-persist
```

This will prompt to add the export line to your `~/.bashrc` or `~/.zshrc`.

Alternatively, add it manually:

```bash
echo 'export PYTHONPATH="/path/to/pyargos:$PYTHONPATH"  # pyArgos' >> ~/.bashrc
```

### 5. Verify the installation

```bash
python -c "import argos; print(argos.__version__)"
```

This should print the current version (e.g., `1.2.3`).

## Optional Dependencies

pyArgos works with several external systems. Install only what you need:

=== "Kafka"

    ```bash
    pip install kafka-python
    ```
    Required for: Kafka topic creation and data consumption.

=== "ThingsBoard"

    ```bash
    pip install tb_rest_client
    ```
    Required for: Device management and trial deployment via ThingsBoard REST API.

=== "Cassandra"

    ```bash
    pip install cassandra-driver dask
    ```
    Required for: Querying ThingsBoard's Cassandra telemetry backend.

=== "MongoDB"

    ```bash
    pip install pymongo dask
    ```
    Required for: Querying MongoDB time-series collections.

=== "Node-RED Parquet nodes"

    ```bash
    pip install dask fastparquet
    ```
    Required for: The `to_parquet` custom Node-RED node.

=== "All optional"

    ```bash
    make install-dev
    ```
    Installs Kafka, ThingsBoard, and documentation dependencies.

## Make Targets Reference

| Target | Description |
|--------|-------------|
| `make install` | Full install: deps + prompt to add PYTHONPATH |
| `make install-deps` | Install dependencies from `requirements.txt` |
| `make install-dev` | Install optional + dev dependencies |
| `make env` | Check if PYTHONPATH is configured correctly |
| `make env-persist` | Add PYTHONPATH to `~/.bashrc` or `~/.zshrc` |

## Logging Configuration

pyArgos uses a custom logging system with an `EXECUTION` log level (15, between DEBUG and INFO). The default configuration is loaded from:

```
~/.pyargos/log/argosLogging.config
```

If this file doesn't exist, pyArgos creates it automatically from package defaults on first import. See [Configuration Reference](configuration.md) for details on customizing logging.

## What's Next?

- [Key Concepts](concepts.md) -- understand experiments, trials, devices, and how they connect
- [Experiment Setup](experiment_setup.md) -- create and configure your first experiment
- [CLI Reference](cli.md) -- all available command-line commands
