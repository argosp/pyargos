# pyArgos

Python wrappings for the [Argos](https://github.com/argosp) IoT experiment management platform.

**[Full Documentation](https://argosp.github.io/pyargos/)**

## Features

- **Experiment Management** - Create, configure, and run IoT experiments
- **Kafka Integration** - Stream data with Kafka consumers and producers
- **ThingsBoard Integration** - Manage devices and assets via ThingsBoard
- **Node-RED Support** - Device mapping for Node-RED workflows
- **Data Processing** - Convert Kafka messages to Parquet format for analysis

## Install

- Install Anaconda 3 with Python 3.7
- Create a virtual environment:
  ```bash
  conda create -n Argos python=3.6.5
  conda activate Argos
  pip install paho-mqtt numpy pandas urllib3 requests
  ```
- Add pyargos to the PYTHONPATH
- Activate the environment before executing:
  ```bash
  conda activate Argos
  ```

## Quick Start

See the [Getting Started](https://argosp.github.io/pyargos/getting-started/) guide for detailed setup instructions.

## Loading a Trial Using the CLI

1. Create a directory for your experiment (see `ExpExample`).

2. Edit `experimentConfiguration.json` to configure your ThingsBoard connection (IP, port, account).

3. In `experimentData/ExperimentData.json`, define the entities (devices/assets) to create:
   - `entityType`: `"DEVICE"` or `"ASSET"`
   - `Number`: How many entities to create
   - `Type`: The device/asset type
   - `nameFormat`: Name format string (`{id}` is replaced by the running number, starting at 1).
     For example, `Number=3` and `nameFormat="name_{id:02d}"` creates: `name_01`, `name_02`, `name_03`

4. Setup the experiment:
   ```bash
   python yourpath/pyargos/bin/trialManager.py --expConf experimentConfiguration.json --setup
   ```
   This creates `trialTemplate.json` under `experimentData/trials/`.

5. Copy `trialTemplate.json` to `experimentData/trials/design/` and rename it to your trial name. Edit it to add attributes and relations.

6. Upload the trial to ThingsBoard:
   ```bash
   python yourpath/pyargos/bin/trialManager.py --expConf experimentConfiguration.json --load trialName
   ```

## Documentation

Full documentation is available at **[argosp.github.io/pyargos](https://argosp.github.io/pyargos/)**:

- [Getting Started](https://argosp.github.io/pyargos/getting-started/) - Installation and setup
- [CLI Reference](https://argosp.github.io/pyargos/cli/) - All available commands
- [Kafka Integration](https://argosp.github.io/pyargos/kafka/) - Streaming data setup
- [ThingsBoard Integration](https://argosp.github.io/pyargos/thingsboard/) - Device management
- [Testing](https://argosp.github.io/pyargos/testing/) - Mock devices and testing
- [Changelog](https://argosp.github.io/pyargos/changelog/) - Version history

## Running a Demo Device

Install the [paho-mqtt package](https://anaconda.org/wheeler-microfluidics/paho-mqtt) in your conda environment, then run the demoDevice from the CLI.
