# CLI Reference

pyArgos provides a command-line interface via `argos.bin.trialManager` for managing experiments, Kafka topics, and ThingsBoard integration.

---

## Experiment Commands

### Create Experiment Directory

```bash
python -m argos.bin.trialManager --createExperiment \
    --experimentName <name> \
    --directory <path>
```

Creates a new experiment with the standard directory structure including `code/`, `data/`, and `runtimeExperimentData/`.

### Setup Experiment

```bash
cd <experiment-directory>
python /path/to/pyargos/bin/trialManager.py \
    --expConf experimentConfiguration.json --setup
```

Generates `experimentData/trials/trialTemplate.json` from the experiment configuration.

---

## Kafka Commands

### Create Topics

```bash
python -m argos.bin.trialManager --kafkaCreateTopics
```

Creates one Kafka topic per entity type plus a `kafkaConsumerServer` management topic. Must be run from an experiment directory.

### Run Consumer (Single Topic)

```bash
python -m argos.bin.trialManager --kafkaRunConsumerTopic <topic>
```

Consumes messages from a specific topic and writes to `data/<topic>.parquet`.

### Run All Consumers

```bash
python -m argos.bin.trialManager --kafkaRunConsumers
```

Starts a consumer thread for each device type. Automatically creates topics if needed.

### Run Consumers (Server Mode)

```bash
python -m argos.bin.trialManager --kafkaRunConsumersServer --delay <duration>
```

Runs consumers in a continuous loop with periodic polling. The `delay` accepts pandas timedelta strings (e.g., `5min`, `30s`, `1h`).

---

## ThingsBoard Commands

### Load Trial Design

```bash
python -m argos.bin.trialManager --tbLoadTrial <trialName> \
    [--directory <experiment-dir>]
```

Uploads trial attributes to ThingsBoard devices.

### Setup Experiment on ThingsBoard

```bash
python -m argos.bin.trialManager --tbSetupExperiment \
    --directory <experiment-dir>
```

Creates devices and assets on ThingsBoard.

### Clean Devices

```bash
python -m argos.bin.trialManager --tbCleanDevices \
    [--directory <experiment-dir>]
```

!!! warning
    Removes **all** tenant devices from ThingsBoard.

---

## Node-RED Commands

### Create Device Map

```bash
python -m argos.bin.trialManager --noderedCreateDeviceMap [--fullNumber]
```

Generates `runtimeExperimentData/deviceMap.json` for Node-RED routing.

| Flag | Description |
|------|-------------|
| *(default)* | Simplifies names to integer form (e.g., `Sonic_0010` -> `Sonic 10`) |
| `--fullNumber` | Keeps original device names |
