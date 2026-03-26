# Testing the System

To test the system, you need to send data to Node-RED (via MQTT/UDP) or directly to the Kafka server. Transmission can be continuous (at the device's frequency) or in bulk for a specific time period.

This section describes how to create mock devices that mimic real devices with randomized data.

## Device Configuration

Mock devices are specified by a JSON configuration file. The configuration can be created from an experiment downloaded from ArgosWEB or manually.

### Configuration Format

```json
{
    "device-type": {
        "number": 3,
        "nameprefix": "Sensor",
        "numberformat": "{:02d}",
        "frequency": 10,
        "transmission": {
            "type": "bulk",
            "bulkTimeUnit": "60s"
        },
        "fields": {
            "timestamp": "datetime",
            "temperature": "float",
            "humidity": "float",
            "status": "str",
            "count": "int"
        }
    }
}
```

### Configuration Fields

| Field | Description |
|-------|-------------|
| `number` | Number of devices to simulate |
| `nameprefix` | Prefix for device names |
| `numberformat` | Python format string for device numbering |
| `frequency` | Sampling frequency in Hz |
| `transmission.type` | `"bulk"` or `"continuous"` |
| `transmission.bulkTimeUnit` | Time duration for bulk transmissions |
| `fields` | Map of field names to types (`datetime`, `int`, `float`, `str`) |

## Transmission Modes

### Continuous

Sends data at the specified frequency, simulating real-time device behavior.

### Bulk

Sends a batch of data covering a specified time period all at once. Useful for testing data processing pipelines without waiting for real-time data.

## Running Mock Devices

### Via MQTT

Mock devices can send data to Node-RED over MQTT, which then forwards it to Kafka:

```
Mock Device --MQTT--> Node-RED ---> Kafka Topic
```

### Direct to Kafka

For testing without Node-RED, mock devices can write directly to Kafka topics:

```
Mock Device ---> Kafka Topic
```
