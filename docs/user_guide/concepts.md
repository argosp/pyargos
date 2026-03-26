# Key Concepts

Understanding the core concepts behind pyArgos will help you work with the platform effectively.

**Table of Contents**

1. [Experiments and Trials](#1-experiments-and-trials)
2. [Trials as a Table](#2-trials-as-a-table)
3. [Devices and Device Types](#3-devices-and-device-types)
4. [Devices as a Table](#4-devices-as-a-table)
5. [The Three Kinds of Property Values](#5-the-three-kinds-of-property-values)
6. [How It All Fits Together in the JSON](#6-how-it-all-fits-together-in-the-json)
7. [Containment — Devices Inside Devices](#7-containment-devices-inside-devices)
8. [A Note on Terminology](#8-a-note-on-terminology)
9. [Data Flow](#9-data-flow)
10. [Experiment Directory Structure](#10-experiment-directory-structure)

---

## 1. Experiments and Trials

An **experiment** is the overall study — it defines the scientific question,
the devices involved, and the protocol being followed.

A **trial** is one complete execution of that protocol. An experiment contains
many trials, and trials differ from each other by their conditions and
configuration.

Two common reasons to run multiple trials within the same experiment:

**Preliminary vs. real trials.** Early trials may explore different device
configurations, placement, or sensor thresholds before the real measurement
conditions are fixed. Once the setup is validated, the real trials begin.

**Varying a parameter.** The real trials may hold the device configuration
constant but vary something about the experimental condition — the amount of
a substance released, the speed of a vehicle, the time of day.

```
Experiment: "Dispersion study under varying wind conditions"
│
├── Preliminary Trial 1  — test sensor placement, threshold=10.0
├── Preliminary Trial 2  — adjust placement, threshold=15.0
├── Trial 1 (real)       — fixed placement, amount_released=50g
├── Trial 2 (real)       — fixed placement, amount_released=100g
└── Trial 3 (real)       — fixed placement, amount_released=200g
```

Each trial is independent. It has a precise start time and end time, a fixed
set of conditions, and produces its own self-contained dataset.

---

## 2. Trials as a Table

The most natural way to think about trials is as rows in a table, where each
column is a property of the trial.

| Trial | Type | threshold | amount_released | wind_speed |
|---|---|---|---|---|
| Preliminary 1 | preliminary | 10.0 | — | 3 m/s |
| Preliminary 2 | preliminary | 15.0 | — | 4 m/s |
| Trial 1 | real | 15.0 | 50 g | 3 m/s |
| Trial 2 | real | 15.0 | 100 g | 3 m/s |
| Trial 3 | real | 15.0 | 200 g | 3 m/s |

Each row is one trial. Each column is a property that may differ between
trials. Some properties are the same across all trials (e.g. `wind_speed`
held constant in the real trials), while others change systematically (e.g.
`amount_released`).

In the JSON, trials are organized under **trial types** (groups of similar
trials) and each trial carries the properties that distinguish it:

```json
"trialTypes": [
    {
        "name": "Preliminary",
        "trials": [
            {
                "name": "Preliminary_01",
                "properties": [
                    { "name": "threshold",        "value": "10.0" },
                    { "name": "wind_speed_ms",    "value": "3"    }
                ]
            },
            {
                "name": "Preliminary_02",
                "properties": [
                    { "name": "threshold",        "value": "15.0" },
                    { "name": "wind_speed_ms",    "value": "4"    }
                ]
            }
        ]
    },
    {
        "name": "RealTrials",
        "trials": [
            {
                "name": "Trial_01",
                "properties": [
                    { "name": "threshold",        "value": "15.0" },
                    { "name": "amount_released_g","value": "50"   },
                    { "name": "wind_speed_ms",    "value": "3"    }
                ]
            },
            {
                "name": "Trial_02",
                "properties": [
                    { "name": "threshold",        "value": "15.0" },
                    { "name": "amount_released_g","value": "100"  },
                    { "name": "wind_speed_ms",    "value": "3"    }
                ]
            }
        ]
    }
]
```

---

## 3. Devices and Device Types

An experiment involves physical devices — sensors, detectors, cameras, markers,
or any instrumented object. These are organized at two levels.

### Device Type — the schema

A **device type** defines a class of device. It specifies:

- What the device is called (e.g. `"Sensor"`)
- What properties it has (e.g. `threshold`, `location`)
- Whether each property is a fixed constant or a per-trial value
- Which specific device instances belong to this type

```json
"deviceTypes": [
    {
        "name": "Sensor",
        "attributeTypes": [
            {
                "name":         "StoreDataPerDevice",
                "type":         "Boolean",
                "defaultValue": false,
                "scope":        "Constant"
            },
            {
                "name": "threshold",
                "type": "Number"
            },
            {
                "name": "location",
                "type": "location"
            }
        ],
        "devices": [
            { "name": "Sensor_01" },
            { "name": "Sensor_02" }
        ]
    }
]
```

This says: *There is a type called Sensor. It has three properties. There are
two individual sensors: Sensor_01 and Sensor_02.*

### Device Instance — the individual

A **device instance** is one physical item of a given type. In the example
above, `Sensor_01` and `Sensor_02` are both instances of the `Sensor` type.
They share the same property schema but may have different property values in
each trial.

---

## 4. Devices as a Table

Just as trials form a table of rows and columns, so do devices. Each **row**
is one device instance and each **column** is a property of that device.

| Device | Type | StoreDataPerDevice | threshold | location |
|---|---|---|---|---|
| Sensor_01 | Sensor | false *(type default)* | 25.0 | [32.08, 34.94] |
| Sensor_02 | Sensor | false *(type default)* | 30.0 | [32.09, 34.95] |
| Pole_01 | Pole | — | — | [32.08, 34.94] |

However — and this is the key distinction — **not all columns have the same
kind of value**. Some properties are fixed for the entire experiment, while
others change from trial to trial. This leads to the three kinds of property
values described in the next section.

---

## 5. The Three Kinds of Property Values

A single device property can come from three different places, depending on
how it is defined and whether it varies by trial.

### Kind 1 — Type-level constant

Defined once on the device type and applies identically to every instance of
that type in every trial. It never changes.

**Where in the JSON:** `deviceTypes[].attributeTypes[]` with
`"scope": "Constant"`.

```json
{
    "name":         "StoreDataPerDevice",
    "type":         "Boolean",
    "defaultValue": false,
    "scope":        "Constant"
}
```

*Every `Sensor` instance, in every trial, has `StoreDataPerDevice = false`
unless explicitly overridden.*

### Kind 2 — Instance-level constant

A value that is fixed for a specific device instance but may differ between
instances. It does not change across trials — once set, it stays the same
for the life of the experiment.

**Example:** The serial number or hardware ID of a physical sensor.
Sensor_01 always has its own hardware ID, Sensor_02 has a different one, and
neither changes between trials.

**Where in the JSON:** `deviceTypes[].devices[]` — properties attached
directly to the instance definition.

### Kind 3 — Trial-level value

A value that is configured specifically for each trial. The same device may
have different property values in Trial_01 vs Trial_02 — for example, a
different threshold, a different physical placement, or a different operational
mode.

**Where in the JSON:** `trialTypes[].trials[].devicesOnTrial[].attributes[]`.

```json
"devicesOnTrial": [
    {
        "deviceTypeName": "Sensor",
        "deviceItemName": "Sensor_01",
        "location": {
            "name":        "OSMMap",
            "coordinates": [32.08, 34.94]
        },
        "attributes": [
            { "name": "threshold", "value": "25.0" }
        ]
    }
]
```

*In this trial, Sensor_01 is placed at [32.08, 34.94] and has threshold 25.0.
In the next trial, it might be placed somewhere different with threshold 30.0.*

### Summary table

| Kind | Varies by trial? | Varies by device? | Where in JSON |
|---|---|---|---|
| Type-level constant | No | No | `deviceTypes[].attributeTypes[]` with `scope: "Constant"` |
| Instance-level constant | No | Yes | `deviceTypes[].devices[]` |
| Trial-level value | **Yes** | Yes | `trialTypes[].trials[].devicesOnTrial[].attributes[]` |

---

## 6. How It All Fits Together in the JSON

The complete JSON structure connects these concepts through a set of
cross-references. Here is the full relationship map:

```
deviceTypes[]                      <- type definitions (the schema)
  |-- name: "Sensor"
  |-- attributeTypes[]             <- property schema for this type
  |     |-- { name, type, scope: "Constant", defaultValue }
  |     |     \-- type-level constant -- same for all instances, all trials
  |     \-- { name, type }
  |           \-- no scope -- value is set per trial
  \-- devices[]                    <- instances of this type
        |-- { name: "Sensor_01" }
        \-- { name: "Sensor_02" }

trialTypes[]                       <- groupings of related trials
  \-- trials[]                     <- individual trials
        |-- name: "Trial_01"
        \-- devicesOnTrial[]       <- per-trial configuration of each device
              |-- deviceTypeName   -> links to deviceTypes[].name
              |-- deviceItemName   -> links to devices[].name
              |-- location         <- where this device is placed in this trial
              |-- attributes[]     <- trial-specific property values
              \-- containedIn      <- optional: this device is inside another
```

A concrete reading of one `devicesOnTrial` entry:

```json
{
    "deviceTypeName": "Sensor",
    "deviceItemName": "Sensor_01",
    "location": {
        "name":        "OSMMap",
        "coordinates": [32.08, 34.94]
    },
    "attributes": [
        { "name": "threshold", "value": "25.0" }
    ],
    "containedIn": {
        "deviceTypeName": "Pole",
        "deviceItemName": "Pole_01"
    }
}
```

Reading this entry in plain language:

> *In this trial, the device Sensor_01 (which is of type Sensor) is placed at
> coordinates [32.08, 34.94], has its threshold set to 25.0, and is physically
> mounted on Pole_01.*

To get the complete property set for Sensor_01 in this trial, three sources
are combined in order:

1. Start with type defaults — `StoreDataPerDevice = false` (from
   `deviceTypes[].attributeTypes[]` where `scope: "Constant"`)
2. Apply instance-level constants — any properties fixed to Sensor_01
   specifically
3. Apply trial-level values — `threshold = 25.0` and
   `location = [32.08, 34.94]` (from `devicesOnTrial[].attributes[]`)

Later sources override earlier ones. A trial-level value always wins over a
type default.

---

## 7. Containment — Devices Inside Devices

Physical devices are often arranged hierarchically. A sensor may be mounted
on a pole; the pole is anchored at a location; several poles form a cluster.
The JSON represents this with the `containedIn` field.

```json
"containedIn": {
    "deviceTypeName": "Pole",
    "deviceItemName": "Pole_01"
}
```

This says: *Sensor_01 is physically contained within Pole_01.*

Containment has two practical effects:

**Location inheritance.** If a device has no location of its own, it inherits
its parent's location. If Sensor_01 has no `location` entry in
`devicesOnTrial` but Pole_01 does, Sensor_01 is considered to be at Pole_01's
coordinates. This chain walks upward as many levels as needed —
child -> parent -> grandparent — until a location is found.

**Attribute inheritance.** Missing attributes are similarly resolved upward
through the containment chain.

```
Containment hierarchy example:

Cluster_A  (location: [32.10, 34.90])
\-- Pole_01  (no location -- inherits from Cluster_A)
    \-- Sensor_01  (no location -- inherits from Pole_01 -> Cluster_A)
        \-- threshold: 25.0  (set directly on Sensor_01 in this trial)
```

This means you only need to specify a location once — on the outermost
container — and all devices mounted on it automatically resolve to that
location unless they define their own.

---

## 8. A Note on Terminology

The terms **device** and **entity** refer to the same concept. The terminology
changed between versions of the format:

| Concept | v3.0.0 (current) | v2.0.0 | Internal (pyArgos) |
|---|---|---|---|
| Type definition | `deviceTypes` | `entityTypes` | `entityTypes` |
| Instance | `devices` | `entities` | `entities` |
| Trial entity data | `devicesOnTrial` | `entities` (in trial) | `entities` |
| Trial set | `trialTypes` | `trialSets` | `trialSets` |

When reading documentation, code comments, or older JSON files: **device and
entity mean the same thing.** v3.0.0 uses device terminology throughout.
pyArgos normalizes everything to entity terminology internally regardless
of which version of the JSON it reads.

---

## 9. Data Flow

The typical data flow in a pyArgos experiment:

![Diagram](../images/diagrams/user_guide_concepts_0_504f7274.svg)

<!-- mermaid source (for editing, paste into mermaid.live):
```mermaid
graph LR
    A[Configure Experiment] --> B[Setup on ThingsBoard]
    B --> C[Deploy Devices]
    C --> D[Stream Data via Kafka]
    D --> E[Store in Parquet]
    E --> F[Analyze with Pandas]
```
-->

1. **Configure** - Define entities and trials in JSON or via ArgosWEB
2. **Setup** - Upload device profiles and entities to ThingsBoard
3. **Deploy** - Load trial attributes to devices
4. **Stream** - Consume device data from Kafka topics
5. **Store** - Write data to Parquet files (partitioned by time)
6. **Analyze** - Load Parquet files into Pandas DataFrames

---

## 10. Experiment Directory Structure

Every pyArgos experiment follows a standard directory layout:

```
MyExperiment/
  code/                         # Analysis scripts
    argos_basic.py              # Auto-generated experiment loader
  data/                         # Parquet data files (one per device type)
  runtimeExperimentData/        # Configuration and metadata
    Datasources_Configurations.json   # Main config (Kafka, ThingsBoard)
    deviceMap.json              # Node-RED device mapping
    <experimentName>.zip        # Experiment definition (from ArgosWEB)
    trials/
      design/                   # Trial design files
        myTrial.json
      trialTemplate.json        # Generated template
```

---

## Quick Reference

| Term | What it is | Analogy |
|---|---|---|
| Experiment | The overall study | A spreadsheet workbook |
| Trial | One execution of the protocol | A row in the trials table |
| Trial type | A group of similar trials | A sheet within the workbook |
| Device type | The schema for a class of device | A column header definition |
| Device instance | One physical device | A row in the devices table |
| Property (Constant scope) | Same value for all instances, all trials | A fixed column default |
| Property (Instance-level) | Fixed per device, same across trials | A cell that never changes |
| Property (Trial-level) | Configured per trial | A cell that changes row by row |
| Containment | A device physically inside another | A parent-child relationship |
