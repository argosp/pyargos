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

### Quick install (with Make)

```bash
git clone git@github.com:argosp/pyargos.git
cd pyargos
make install
```

This will:
1. Install Python dependencies from `requirements.txt`
2. Prompt to add `PYTHONPATH` to your `~/.bashrc` (or `~/.zshrc`)

### Manual install

1. Create a virtual environment:
   ```bash
   conda create -n Argos python=3.11
   conda activate Argos
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Add pyargos to your PYTHONPATH:
   ```bash
   export PYTHONPATH="/path/to/pyargos:$PYTHONPATH"
   ```
   To make this permanent, add the line to your `~/.bashrc` or `~/.zshrc`.

4. Verify:
   ```bash
   python -c "import argos; print(argos.__version__)"
   ```

### Optional dependencies

```bash
# Kafka consumers
pip install kafka-python

# ThingsBoard integration
pip install tb_rest_client

# Documentation development
pip install mkdocs-material mkdocstrings mkdocstrings-python
```

## Quick Start

See the [Getting Started](https://argosp.github.io/pyargos/user_guide/installation/) guide for detailed setup instructions.

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

## Make Targets

```
make install             Full install (deps + env vars + prompt for .bashrc)
make install-deps        Install Python dependencies
make install-dev         Install dev + optional dependencies
make env                 Print environment variables needed
make env-persist         Add PYTHONPATH to ~/.bashrc (prompts first)
make docs-build          Build documentation site
make docs-serve          Start local docs preview server
make help                List all targets
```

## Documentation

Full documentation is available at **[argosp.github.io/pyargos](https://argosp.github.io/pyargos/)**:

- [Key Concepts](https://argosp.github.io/pyargos/user_guide/concepts/) - Experiments, trials, devices, and how they connect
- [Installation](https://argosp.github.io/pyargos/user_guide/installation/) - Detailed setup instructions
- [CLI Reference](https://argosp.github.io/pyargos/user_guide/cli/) - All available commands
- [Kafka Integration](https://argosp.github.io/pyargos/user_guide/kafka/) - Streaming data setup
- [ThingsBoard Integration](https://argosp.github.io/pyargos/user_guide/thingsboard/) - Device management
- [Developer Guide](https://argosp.github.io/pyargos/developer_guide/) - Architecture, API reference, data model
- [Changelog](https://argosp.github.io/pyargos/changelog/) - Version history

## Running a Demo Device

Install the [paho-mqtt package](https://anaconda.org/wheeler-microfluidics/paho-mqtt) in your conda environment, then run the demoDevice from the CLI.
