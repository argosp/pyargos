# Experiment Setup API

**Module:** `argos.experimentSetup`

The experiment setup module provides the factory pattern for loading experiments and the data objects that represent the experiment hierarchy.

---

## Module Entry Point

::: argos.experimentSetup.getExperimentSetup
    options:
      show_root_heading: true
      heading_level: 3

---

## Factories

### fileExperimentFactory

::: argos.experimentSetup.dataObjectsFactory.fileExperimentFactory
    options:
      show_root_heading: true
      heading_level: 4
      members:
        - __init__
        - getExperiment

---

### webExperimentFactory

::: argos.experimentSetup.dataObjectsFactory.webExperimentFactory
    options:
      show_root_heading: true
      heading_level: 4
      members:
        - __init__
        - getExperiment
        - getExperimentMetadata
        - getExperimentsDescriptionsList
        - getExperimentsDescriptionsTable
        - getExperimentDescriptor
        - listExperimentsNames
        - url
        - client
        - keys

---

## Data Objects

### Experiment

::: argos.experimentSetup.dataObjects.Experiment
    options:
      show_root_heading: true
      heading_level: 4
      members:
        - __init__
        - refresh
        - setup
        - name
        - description
        - url
        - client
        - trialSet
        - entityType
        - entityTypeTable
        - entitiesTable
        - trialsTableAllSets
        - trialsTable
        - imageMap
        - getImage
        - getImageURL
        - getImageMetadata
        - getImageJSMappingFunction
        - getExperimentEntities
        - getEntitiesTypeByID
        - toJSON

---

### ExperimentZipFile

::: argos.experimentSetup.dataObjects.ExperimentZipFile
    options:
      show_root_heading: true
      heading_level: 4
      members:
        - __init__
        - refresh
        - getImage

---

### webExperiment

::: argos.experimentSetup.dataObjects.webExperiment
    options:
      show_root_heading: true
      heading_level: 4
      members:
        - getImage

---

### TrialSet

::: argos.experimentSetup.dataObjects.TrialSet
    options:
      show_root_heading: true
      heading_level: 4
      members:
        - __init__
        - experiment
        - name
        - description
        - numberOfTrials
        - properties
        - propertiesTable
        - trials
        - trialsTable
        - toJSON

---

### Trial

::: argos.experimentSetup.dataObjects.Trial
    options:
      show_root_heading: true
      heading_level: 4
      members:
        - __init__
        - experiment
        - trialSet
        - name
        - created
        - cloneFrom
        - numberOfEntities
        - properties
        - propertiesTable
        - entities
        - entitiesTable
        - toJSON

---

### EntityType

::: argos.experimentSetup.dataObjects.EntityType
    options:
      show_root_heading: true
      heading_level: 4
      members:
        - __init__
        - experiment
        - name
        - numberOfEntities
        - properties
        - propertiesTable
        - entitiesTable
        - entitiesAllProperties
        - toJSON

---

### Entity

::: argos.experimentSetup.dataObjects.Entity
    options:
      show_root_heading: true
      heading_level: 4
      members:
        - __init__
        - name
        - entityType
        - experiment
        - properties
        - propertiesList
        - propertiesTable
        - allProperties
        - allPropertiesList
        - allPropertiesTable
        - allTrialProperties
        - allTrialPropertiesTable
        - trialProperties
        - toJSON

---

## Utility Functions

### fill_properties_by_contained

::: argos.experimentSetup.fillContained.fill_properties_by_contained
    options:
      show_root_heading: true
      heading_level: 4

::: argos.experimentSetup.fillContained.spread_attributes
    options:
      show_root_heading: true
      heading_level: 4

::: argos.experimentSetup.fillContained.get_parent
    options:
      show_root_heading: true
      heading_level: 4

::: argos.experimentSetup.fillContained.key_from_name
    options:
      show_root_heading: true
      heading_level: 4
