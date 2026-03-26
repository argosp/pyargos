# pyArgos

Python wrappings for the [Argos](https://github.com/argosp) IoT experiment management platform.

## Overview

pyArgos is a comprehensive toolkit for managing IoT experiments with support for:

- **Experiment Management** - Create, configure, and run IoT experiments
- **Kafka Integration** - Stream data with Kafka consumers and producers
- **ThingsBoard Integration** - Manage devices and assets via ThingsBoard
- **Node-RED Support** - Device mapping for Node-RED workflows
- **Data Processing** - Convert Kafka messages to Parquet format for analysis

## Quick Start

```bash
# Install dependencies
pip install paho-mqtt numpy pandas urllib3 requests

# Add pyargos to your PYTHONPATH
export PYTHONPATH=$PYTHONPATH:/path/to/pyargos

# Create a new experiment
python -m argos.bin.trialManager --expConf experimentConfiguration.json --setup
```

See the [Getting Started](getting-started.md) guide for detailed installation and setup instructions.

## Architecture

pyArgos integrates several systems to provide a complete IoT experiment workflow:

```
ArgosWEB / File Config
        |
        v
   pyArgos CLI
   /    |     \
  v     v      v
Kafka  TB   Node-RED
  |     |
  v     v
Parquet  Devices & Assets
```

## Project Structure

```
pyargos/
  argos/
    CLI.py                  # Command-line interface
    manager.py              # Experiment manager
    experimentSetup/        # Experiment data objects and factories
    kafka/                  # Kafka consumer/producer
    thingsboard/            # ThingsBoard integration
    nodered/                # Node-RED integration
    noSQLdask/              # NoSQL database support (Cassandra, MongoDB)
    utils/                  # Logging, JSON, and Parquet utilities
    examples/               # Example configurations
```
