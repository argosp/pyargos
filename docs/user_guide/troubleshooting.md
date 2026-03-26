# Troubleshooting

Common issues and their solutions.

---

## Installation Issues

### `tb_rest_client` import error

**Symptom:** `Thingsboard interface not installed. Use pip install tb_rest_client.`

**Solution:** This is a warning, not an error. pyArgos works without `tb_rest_client` but ThingsBoard features will be unavailable. Install it if you need ThingsBoard integration:

```bash
pip install tb_rest_client
```

### Module not found: `argos`

**Symptom:** `ModuleNotFoundError: No module named 'argos'`

**Solution:** Add pyargos to your PYTHONPATH:

```bash
export PYTHONPATH=$PYTHONPATH:/path/to/pyargos
```

---

## Kafka Issues

### Not an experiment directory

**Symptom:** `<path> is not an experiment directory`

**Solution:** Kafka commands must be run from an experiment directory containing `runtimeExperimentData/`. Either `cd` to the experiment directory or use the `--directory` flag.

### Configuration file not found

**Symptom:** `Datasources_Configurations.json does not exist!`

**Solution:** Ensure the experiment directory has been properly set up with `--createExperiment` or that `runtimeExperimentData/Datasources_Configurations.json` exists.

### Kafka connection refused

**Symptom:** `NoBrokersAvailable` or connection errors

**Solution:** Verify that Kafka and Zookeeper are running and that the `bootstrap_servers` in your configuration matches:

```bash
# Check if Kafka is running
<path-to-confluent>/bin/kafka-topics.sh --list --bootstrap-server 127.0.0.1:9092
```

---

## ThingsBoard Issues

### Authentication failure

**Symptom:** REST client login fails

**Solution:** Verify the credentials in `Datasources_Configurations.json`:

- `restURL` should include the protocol (e.g., `http://localhost:8080`)
- `username` and `password` must be valid ThingsBoard tenant credentials

### Device not found during trial upload

**Symptom:** Index error when loading a trial

**Solution:** Devices must exist on ThingsBoard before uploading a trial. Run the experiment setup first:

```python
manager = experimentManager("/path/to/experiment")
manager.loadDevicesToThingsboard()  # Create devices first
manager.loadTrialDesignToThingsboard("design", "myTrial")  # Then load trial
```

---

## Data Issues

### Empty Parquet files

**Symptom:** Parquet files are created but contain no data

**Solution:** Check that:

1. Kafka topics have data (use `kafka-console-consumer.sh` to verify)
2. The consumer is connecting to the correct bootstrap server
3. The consumer group hasn't already consumed all messages (try `auto_offset_reset='earliest'`)

### Duplicate timestamps

**Solution:** pyArgos automatically removes duplicate timestamps during Kafka consumption. If you see duplicates in existing files, re-run the consumer - the deduplication applies to the append operation.
