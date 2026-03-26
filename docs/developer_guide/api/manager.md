# Experiment Manager API

**Module:** `argos.manager`

The `experimentManager` class provides a unified interface to experiment data and ThingsBoard operations.

---

## `experimentManager`

```python
from argos.manager import experimentManager

manager = experimentManager("/path/to/experiment")
```

### `__init__(experimentDirectory)`

| Parameter | Type | Description |
|-----------|------|-------------|
| `experimentDirectory` | `str` | Path to the experiment root directory |

Loads `runtimeExperimentData/Datasources_Configurations.json` on initialization.

---

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `experimentDirectory` | `str` | Path to experiment root |
| `configuration` | `dict` | Loaded configuration |
| `TBConfiguration` | `dict` | ThingsBoard config section |
| `restClient` | `RestClientCE` | Authenticated ThingsBoard REST client |
| `experiment` | `Experiment` | Experiment loaded from files |

!!! note
    `restClient` creates a new authenticated connection on each access.

---

### Methods

#### `loadConfigutation()`

Reloads the configuration from `Datasources_Configurations.json`.

---

#### `loadDevicesToThingsboard()`

Creates all experiment entities as ThingsBoard devices.

**Behavior:**

1. Fetches existing device profiles from ThingsBoard
2. Creates missing device profiles for each entity type
3. Creates devices that don't already exist (skips duplicates)

---

#### `loadTrialDesignToThingsboard(trialSetName, trialName)`

Uploads a trial design to ThingsBoard.

| Parameter | Type | Description |
|-----------|------|-------------|
| `trialSetName` | `str` | Trial set name (e.g., `"design"`) |
| `trialName` | `str` | Trial name |

**Behavior:**

1. For each entity in the trial:
    - Clears existing attributes in all scopes (SERVER, SHARED, CLIENT)
    - Sets new attributes in `SERVER_SCOPE`

---

#### `loadTrialDeployToThingsboard(trialSetName, trialName)`

Same as `loadTrialDesignToThingsboard` - uploads trial data to ThingsBoard.

---

#### `getDeviceMap(deviceType=None)`

Returns a map of device names to their credentials and types.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `deviceType` | `str` | `None` | Filter by device type |

**Returns:** `dict` - `{deviceName: {"credential": str, "type": str}}`

---

#### `clearDevicesFromThingsboard()`

Removes **all** tenant devices from the ThingsBoard server.

!!! danger
    This is destructive and affects all devices, not just those in the current experiment.
