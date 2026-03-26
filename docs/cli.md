# CLI Reference

pyArgos provides a command-line interface for managing experiments, Kafka topics, and ThingsBoard integration.

## Experiment Commands

### Create Experiment Directory

Creates a new experiment directory with the standard structure.

```bash
python -m argos.bin.trialManager --createExperiment \
    --experimentName <name> \
    --directory <path>
```

Creates:

- `<name>/code/` - Code directory with a basic `argos_basic.py` file
- `<name>/data/` - Data storage directory
- `<name>/runtimeExperimentData/` - Runtime configuration with `Datasources_Configurations.json`

### Setup Experiment

Generates a trial template from the experiment configuration.

```bash
cd <experiment-directory>
python /path/to/pyargos/bin/trialManager.py \
    --expConf experimentConfiguration.json \
    --setup
```

Output: `experimentData/trials/trialTemplate.json`

## Kafka Commands

### Create Topics

Creates Kafka topics for each device type in the experiment.

```bash
python -m argos.bin.trialManager --kafkaCreateTopics
```

Reads device types from the experiment configuration and creates a topic per type plus a `kafkaConsumerServer` topic.

### Run Consumer for a Single Topic

Consumes messages from a specific Kafka topic and writes them to Parquet files.

```bash
python -m argos.bin.trialManager --kafkaRunConsumerTopic <topic>
```

### Run All Consumers

Starts a consumer thread for each device type topic.

```bash
python -m argos.bin.trialManager --kafkaRunConsumers
```

### Run Consumers in Server Mode

Runs consumers with periodic polling.

```bash
python -m argos.bin.trialManager --kafkaRunConsumersServer --delay <duration>
```

The `delay` parameter accepts pandas timedelta strings (e.g., `5min`, `30s`).

## ThingsBoard Commands

### Load Trial Design

Uploads a trial design to ThingsBoard, setting device attributes.

```bash
python -m argos.bin.trialManager --tbLoadTrial <trialName> \
    [--directory <experiment-dir>]
```

### Setup Experiment on ThingsBoard

Creates devices and assets on ThingsBoard based on the experiment configuration.

```bash
python -m argos.bin.trialManager --tbSetupExperiment \
    --directory <experiment-dir>
```

### Clean Devices

Removes all devices from ThingsBoard.

```bash
python -m argos.bin.trialManager --tbCleanDevices \
    [--directory <experiment-dir>]
```

!!! warning
    This removes **all** tenant devices from the ThingsBoard server. Use with caution.

## Node-RED Commands

### Create Device Map

Generates a device map JSON file for Node-RED integration.

```bash
python -m argos.bin.trialManager --noderedCreateDeviceMap [--fullNumber]
```

The device map translates device names to their types. By default, device names are simplified to integer form (e.g., `Sonic_0010` becomes `Sonic 10`). Use `--fullNumber` to keep original names.

Output: `runtimeExperimentData/deviceMap.json`
