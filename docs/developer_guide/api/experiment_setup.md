# Experiment Setup API

**Module:** `argos.experimentSetup`

The experiment setup module provides the factory pattern for loading experiments and the data objects that represent the experiment hierarchy.

---

## Factories

### `fileExperimentFactory`

**Module:** `argos.experimentSetup.dataObjectsFactory`

Loads experiments from the local filesystem.

```python
from argos.experimentSetup.dataObjectsFactory import fileExperimentFactory

factory = fileExperimentFactory("/path/to/experiment")
experiment = factory.getExperiment()
```

#### `__init__(experimentPath=None)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `experimentPath` | `str` | Current directory | Path to the experiment root directory |

#### `getExperiment() -> Experiment`

Scans `runtimeExperimentData/` for experiment data:

- If a `.zip` file is found, returns an `ExperimentZipFile`
- If extracted JSON is found, returns an `Experiment`
- Handles version migrations automatically (1.0.0 - 3.0.0)

---

### `webExperimentFactory`

**Module:** `argos.experimentSetup.dataObjectsFactory`

Fetches experiments from ArgosWEB via GraphQL.

```python
from argos.experimentSetup.dataObjectsFactory import webExperimentFactory

factory = webExperimentFactory(url="http://server/graphql", token="auth-token")
experiment = factory.getExperiment("MyExperiment")
```

#### `__init__(url, token)`

| Parameter | Type | Description |
|-----------|------|-------------|
| `url` | `str` | GraphQL endpoint URL |
| `token` | `str` | Authentication token |

#### Key Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `getExperiment(name)` | `webExperiment` | Full experiment object |
| `getExperimentMetadata(name)` | `dict` | Raw experiment metadata |
| `listExperimentsNames()` | `list` | All experiment names |
| `getExperimentsDescriptionsList()` | `list` | All experiment descriptors |

---

## Data Objects

### `Experiment`

**Module:** `argos.experimentSetup.dataObjects`

Base class for experiment data. All properties return data derived from the experiment setup dictionary.

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `setup` | `dict` | Raw experiment configuration |
| `name` | `str` | Experiment name |
| `description` | `str` | Experiment description |
| `trialSet` | `dict[str, TrialSet]` | Trial sets by name |
| `entityType` | `dict[str, EntityType]` | Entity types by name |
| `imageMap` | `dict` | Map of embedded images |
| `entitiesTable` | `DataFrame` | All entities flattened |
| `entityTypeTable` | `DataFrame` | Entity type summary |
| `trialsTableAllSets` | `DataFrame` | All trials across all sets |

#### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `refresh()` | `None` | Reload experiment data |
| `trialsTable(trialsetName)` | `DataFrame` | Trials for a specific set |
| `getImage(name)` | `bytes` | Image data |
| `getImageURL(name)` | `str` | Image URL |
| `getImageMetadata(name)` | `dict` | Image mapping coordinates |
| `getImageJSMappingFunction(name)` | `str` | JavaScript coordinate transform |
| `toJSON()` | `dict` | Export to nested dict |

#### Subclasses

- **`ExperimentZipFile`** - Handles ZIP-packaged experiments. Overrides `refresh()` to parse `data.json` from archive. Includes version migration methods.
- **`webExperiment`** - Handles web-sourced experiments. Overrides `getImage()` to fetch via HTTP.

---

### `TrialSet`

Extends `dict`. Container of trials for a specific set.

```python
trial_set = experiment.trialSet["design"]
trial = trial_set["myTrial"]  # Dict-like access
```

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | Trial set name |
| `description` | `str` | Trial set description |
| `experiment` | `Experiment` | Parent experiment |
| `numberOfTrials` | `int` | Number of trials |
| `properties` | `dict` | Attribute definitions |
| `propertiesTable` | `DataFrame` | Properties as DataFrame |
| `trialsTable` | `DataFrame` | All trials as DataFrame |

---

### `Trial`

Represents a single experimental trial with associated entity data.

```python
trial = experiment.trialSet["design"]["myTrial"]
entities = trial.entitiesTable()  # Dict of entity_name -> attributes
```

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | Trial name |
| `created` | `str` | Creation timestamp |
| `cloneFrom` | `str` | Source trial if cloned |
| `trialSet` | `TrialSet` | Parent trial set |
| `experiment` | `Experiment` | Root experiment |
| `properties` | `dict` | Trial-level attributes |
| `propertiesTable` | `DataFrame` | Properties as DataFrame |
| `entities` | `dict` | Per-entity data |

#### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `entitiesTable()` | `dict` | Entity name -> parsed attributes |

---

### `EntityType`

Extends `dict`. Metadata and collection of entities of the same type.

```python
sensor_type = experiment.entityType["Sensor"]
entity = sensor_type["Sensor_01"]  # Dict-like access
```

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | Type name |
| `experiment` | `Experiment` | Parent experiment |
| `numberOfEntities` | `int` | Entity count |
| `properties` | `dict` | Type-level attributes |
| `propertiesTable` | `DataFrame` | Properties as DataFrame |
| `entitiesTable` | `DataFrame` | All entities |
| `entitiesAllProperties` | `DataFrame` | Including trial-specific |

---

### `Entity`

Represents a single device or asset instance.

```python
entity = experiment.entityType["Sensor"]["Sensor_01"]
print(entity.propertiesTable)
```

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | Entity name |
| `entityType` | `str` | Type name |
| `properties` | `dict` | Constant attributes |
| `propertiesList` | `list` | Property dicts with scope |
| `allProperties` | `dict` | All including trial-specific |
| `propertiesTable` | `DataFrame` | Constant properties |
| `allPropertiesTable` | `DataFrame` | All properties |
| `allTrialProperties` | `dict` | Trial-specific only |
| `allTrialPropertiesTable` | `DataFrame` | Trial properties as DataFrame |

#### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `trialProperties(trialSetName, trialName)` | `dict` | Properties for a specific trial |
| `toJSON()` | `dict` | Export entity definition |

---

## Utility Functions

### `fill_properties_by_contained`

**Module:** `argos.experimentSetup.fillContained`

```python
fill_properties_by_contained(entities_types_dict, meta_entities)
```

Resolves entity hierarchies by inheriting parent properties to child entities. Handles property type conversion and location attribute spreading.
