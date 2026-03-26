# Getting Started

## Prerequisites

- Python 3.7+
- [Anaconda](https://www.anaconda.com/) (recommended)

## Installation

### 1. Create a virtual environment

```bash
conda create -n Argos python=3.7
conda activate Argos
```

### 2. Install dependencies

```bash
pip install paho-mqtt numpy pandas urllib3 requests
```

### 3. Add pyargos to your PYTHONPATH

```bash
export PYTHONPATH=$PYTHONPATH:/path/to/pyargos
```

### 4. Activate the environment before use

```bash
conda activate Argos
```

## Setting Up an Experiment

### 1. Create an experiment directory

Create a directory for your experiment (see `ExpExample` for reference). The directory structure:

```
MyExperiment/
  code/
  data/
  runtimeExperimentData/
    Datasources_Configurations.json
```

You can use the CLI to scaffold this:

```bash
python -m argos.bin.trialManager --createExperiment --experimentName MyExperiment --directory .
```

### 2. Configure the experiment

Edit `runtimeExperimentData/Datasources_Configurations.json` to set your environment:

```json
{
    "experimentName": "MyExperiment",
    "kafka": {
        "bootstrap_servers": ["127.0.0.1:9092"]
    },
    "Thingsboard": {
        "restURL": "http://localhost:8080",
        "username": "tenant@thingsboard.org",
        "password": "tenant"
    }
}
```

### 3. Define experiment entities

In `experimentData/ExperimentData.json`, define the devices and assets:

```json
{
    "Entities": [
        {
            "entityType": "DEVICE",
            "Number": 3,
            "Type": "Sensor",
            "nameFormat": "Sensor_{id:02d}"
        }
    ]
}
```

This creates 3 devices: `Sensor_01`, `Sensor_02`, `Sensor_03`.

### 4. Setup the experiment

```bash
cd MyExperiment
python /path/to/pyargos/bin/trialManager.py --expConf experimentConfiguration.json --setup
```

This generates a `trialTemplate.json` file under `experimentData/trials/`.

### 5. Design a trial

1. Copy `trialTemplate.json` to `experimentData/trials/design/`
2. Rename it to your trial name (e.g., `myTrial.json`)
3. Edit the file to add attributes and relations

### 6. Upload the trial to ThingsBoard

```bash
python /path/to/pyargos/bin/trialManager.py --expConf experimentConfiguration.json --load myTrial
```

## Using pyArgos in Python

```python
from argos.experimentSetup import fileExperimentFactory

# Load an experiment from files
experiment = fileExperimentFactory("/path/to/experiment").getExperiment()

# Access entities
print(experiment.entitiesTable)

# Access trial data
print(experiment.trialSet)
```

## Running a Demo Device

Install the paho-mqtt package:

```bash
pip install paho-mqtt
```

Then run the demo device from the CLI to send simulated data.
