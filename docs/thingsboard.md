# ThingsBoard Integration

pyArgos integrates with [ThingsBoard](https://thingsboard.io/) for IoT device management, telemetry, and experiment orchestration.

## Configuration

Add ThingsBoard settings to your `Datasources_Configurations.json`:

```json
{
    "Thingsboard": {
        "restURL": "http://localhost:8080",
        "username": "tenant@thingsboard.org",
        "password": "tenant"
    }
}
```

!!! note
    The ThingsBoard REST client (`tb_rest_client`) is an optional dependency. Install it with:
    ```bash
    pip install tb_rest_client
    ```

## Experiment Manager

The `experimentManager` class provides the main interface to ThingsBoard:

```python
from argos.manager import experimentManager

manager = experimentManager("/path/to/experiment")

# Access the ThingsBoard REST client
client = manager.restClient

# Load the experiment description
experiment = manager.experiment
```

## Device Management

### Load devices to ThingsBoard

Creates device profiles and devices based on the experiment configuration:

```python
manager.loadDevicesToThingsboard()
```

This will:

1. Check existing device profiles on the server
2. Create missing device profiles for each entity type
3. Create devices that don't already exist

### Get device map

Retrieve device credentials and types:

```python
device_map = manager.getDeviceMap(deviceType="Sensor")
# Returns: {"Sensor_01": {"credential": "...", "type": "Sensor"}, ...}
```

### Clear all devices

```python
manager.clearDevicesFromThingsboard()
```

!!! warning
    This removes **all** tenant devices from the server.

## Trial Management

### Loading a trial design

Upload trial attributes to ThingsBoard devices:

```python
manager.loadTrialDesignToThingsboard("design", "myTrial")
```

This sets `SERVER_SCOPE` attributes on each device defined in the trial. Existing attributes are cleared before loading.

### Workflow

1. **Setup** - Create devices on ThingsBoard
2. **Design** - Upload trial design with device attributes
3. **Deploy** - Upload deployment configuration
4. **Run** - Execute the experiment with Kafka consumers

## Attribute Scopes

ThingsBoard supports three attribute scopes:

| Scope | Description |
|-------|-------------|
| `SERVER_SCOPE` | Server-side attributes managed by pyArgos |
| `SHARED_SCOPE` | Shared between server and device |
| `CLIENT_SCOPE` | Device-side attributes |

When loading a trial, pyArgos clears all scopes before writing new `SERVER_SCOPE` attributes.
