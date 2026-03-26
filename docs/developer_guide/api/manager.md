# Experiment Manager API

**Module:** `argos.manager`

The `experimentManager` class is the bridge between experiment metadata (loaded from files via `experimentSetup`) and the ThingsBoard IoT platform.

---

## Role in the System

```
                    experimentSetup
                    (load ZIP/JSON)
                          │
                          ▼
┌──────────────────────────────────────────┐
│          experimentManager               │
│                                          │
│  ┌──────────────┐   ┌────────────────┐   │
│  │  Experiment   │   │  ThingsBoard   │   │
│  │  (from files) │──>│  REST Client   │   │
│  └──────────────┘   └────────────────┘   │
│                            │             │
│                            ▼             │
│                     Create profiles      │
│                     Create devices       │
│                     Upload trial attrs   │
│                     Get credentials      │
│                     Clear devices        │
└──────────────────────────────────────────┘
```

The manager does **not** own the experiment data — it delegates to `fileExperimentFactory` for that. Its job is to orchestrate the ThingsBoard operations that deploy the experiment to the IoT platform.

---

## Class Dependency

![Diagram](../../images/diagrams/developer_guide_api_manager_0_74ee4283.svg)

<!-- mermaid source (for editing, paste into mermaid.live):
```mermaid
classDiagram
    class experimentManager {
        +experimentDirectory : str
        +configuration : dict
        +TBConfiguration : dict
        +restClient : RestClientCE
        +experiment : Experiment
        +loadConfigutation()
        +loadDevicesToThingsboard()
        +loadTrialDesignToThingsboard()
        +loadTrialDeployToThingsboard()
        +loadTrialToThingsboard()
        +getDeviceMap()
        +clearDevicesFromThingsboard()
    }

    class fileExperimentFactory {
        +getExperiment()
    }

    class RestClientCE {
        +login()
        +get_tenant_device_infos()
        +save_device()
        +save_device_profile()
        +save_device_attributes()
        +delete_device()
        +delete_device_attributes()
        +get_device_credentials_by_device_id()
    }

    class Experiment {
        +entitiesTable
        +trialSet
        +entityType
    }

    experimentManager --> fileExperimentFactory : creates on each .experiment access
    experimentManager --> RestClientCE : creates on each .restClient access
    fileExperimentFactory --> Experiment : returns
    experimentManager ..> Experiment : uses
```
-->

**Implementation note:** Both `restClient` and `experiment` are properties that create a **new instance on each access** — the manager does not cache them. This means each method call gets a fresh ThingsBoard connection and a fresh experiment load. This is intentional for correctness (the experiment files may change between calls) but has a performance cost.

---

## Swimlane: Load Devices to ThingsBoard

![Diagram](../../images/diagrams/developer_guide_api_manager_1_3ac72bc3.svg)

<!-- mermaid source (for editing, paste into mermaid.live):
```mermaid
sequenceDiagram
    actor User
    participant Mgr as experimentManager
    participant Exp as Experiment
    participant TB as ThingsBoard

    User->>Mgr: loadDevicesToThingsboard()
    Mgr->>Exp: .experiment (load from files)
    Mgr->>TB: .restClient (login)
    Mgr->>TB: get_device_profile_names()
    TB-->>Mgr: existing profiles

    loop For each entity type
        alt Profile missing
            Mgr->>TB: save_device_profile(name, DEFAULT)
            TB-->>Mgr: new profile ID
        else Profile exists
            Mgr->>TB: get_device_profile_info_by_id()
        end

        loop For each entity of this type
            Mgr->>TB: get_tenant_device_infos(text_search=name)
            alt Device missing
                Mgr->>TB: save_device(name, profile_id)
                TB-->>Mgr: created device
            else Device exists
                Note over Mgr: skip
            end
        end
    end
```
-->

## Swimlane: Upload Trial to ThingsBoard

![Diagram](../../images/diagrams/developer_guide_api_manager_2_5229f075.svg)

<!-- mermaid source (for editing, paste into mermaid.live):
```mermaid
sequenceDiagram
    actor User
    participant Mgr as experimentManager
    participant Exp as Experiment
    participant Trial as Trial
    participant TB as ThingsBoard

    User->>Mgr: loadTrialDesignToThingsboard("design", "trial1")
    Mgr->>Exp: .experiment (load from files)
    Mgr->>TB: .restClient (login)
    Mgr->>Trial: trialSet["design"]["trial1"].entitiesTable()

    loop For each entity in trial
        Mgr->>TB: get_tenant_devices(text_search=deviceName)
        TB-->>Mgr: device object

        loop For each scope (SERVER, SHARED, CLIENT)
            Mgr->>TB: get_attributes(device.id, scope)
            Mgr->>TB: delete_device_attributes(device.id, scope, keys)
        end

        Mgr->>TB: save_device_attributes(device.id, SERVER_SCOPE, data)
    end
```
-->

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
