# Experiment Manager API

**Module:** `argos.manager`

The `experimentManager` class provides a unified interface to experiment data and ThingsBoard operations.

---

## Module Constants

::: argos.manager.SERVER_SCOPE
    options:
      show_root_heading: true
      heading_level: 4

::: argos.manager.SHARED_SCOPE
    options:
      show_root_heading: true
      heading_level: 4

::: argos.manager.CLIENT_SCOPE
    options:
      show_root_heading: true
      heading_level: 4

---

## experimentManager

::: argos.manager.experimentManager
    options:
      show_root_heading: true
      heading_level: 3
      members:
        - __init__
        - experimentDirectory
        - configuration
        - TBConfiguration
        - restClient
        - experiment
        - loadConfigutation
        - loadDevicesToThingsboard
        - loadTrialDesignToThingsboard
        - loadTrialDeployToThingsboard
        - loadTrialToThingsboard
        - getDeviceMap
        - clearDevicesFromThingsboard
