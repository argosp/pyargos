# Changelog

## Version 1.3.0

### Documentation
- Added MkDocs documentation site with Material theme, deployed to GitHub Pages
- Structured as User Guide (11 pages) and Developer Guide (12 pages)
- Added mkdocstrings autodoc for all modules — API docs auto-generated from Python docstrings
- Added comprehensive numpy-style docstrings to all public classes, methods, and properties across all modules
- Added Data Model Reference: domain concepts (experiments, trials, entities), ZIP file format, JSON schemas (v1.0.0, v2.0.0, v3.0.0), property types and scopes
- Added Key Concepts page: ArgosWEB UI introduction, experiments vs trials, devices and device types, three kinds of property values, containment, image maps, experiment lifecycle (planning → execution → post-processing)
- Added Experiment Setup Architecture: inheritance diagrams, factory pattern, object lifecycle, property system, containment resolution, DataFrame generation map
- Added architecture, class dependency diagrams, and swimlane diagrams for all API modules (manager, kafka, nodered, nosql, utils)
- Expanded Core Concepts with system-wide module map, dependency matrix, full deployment swimlane, CLI command routing

### Tooling
- Added `render_diagrams.py` — pre-renders mermaid diagrams to SVG via Docker (minlag/mermaid-cli) with incremental content-hash based caching
- Added `serve_docs.sh` for local docs development
- Added `Makefile` with install, env, and docs targets
- Added `make install` — installs deps and prompts to add PYTHONPATH to shell profile
- Added `make env-persist` — adds PYTHONPATH to `~/.bashrc` or `~/.zshrc` with confirmation prompt
- Added GitHub Actions workflow for automatic docs deployment to GitHub Pages

### Fixes
- Fixed CI docs workflow: removed `requirements.txt` install that failed on Python 3.14 (pillow build)
- Updated README with correct Python version, make workflow, and fixed documentation links
- Updated Installation guide with make workflow, conda/venv tabs, and verification step

## Version 1.2.3

- Added the ThingsBoard interface
- Removed dependency on the ThingsBoard interface library
- Fixed the case when maps do not appear

## Version 1.2.2

- Minor changes to support the old version of the configuration file

## Version 1.2.1

- Fixed a bug reading the ZIP file

## Version 1.2.0

- Added write to Parquet and append to Parquet
- Refactored the argos-experiment-manager:
    - Build new experiment
    - Kafka-to-Parquet Python utility (works independently by command or by message from a different topic)
- Added logging utility
- Fixed the data object: parses the type of the object (text, number, location)
- Fixed loading trial: removes old attributes before loading
- Added the argos-experiment-manager to setup and load trials to ThingsBoard
- Fixed the data object with the new DB structure

## Version 1.1.0

- Added factory to handle JSON version 2.0.0 and all experiment data in ZIP file

## Version 1.0.0

- Changed devices to entities

## Version 0.4.0

- Added default assets (windows and device groups)
- Loading device properties for the requested release

## Version 0.2.0

- Refactored the GraphQL interface
- Removed the report

## Version 0.1.0

- Added GraphQL interface
- Started using Kafka consumers (processors)

## Version 0.0.2

- Switched to the new Swagger wrapping

## Version 0.0.1

- Addition/removal of devices and assets
- Updating attributes
- Adding relations
