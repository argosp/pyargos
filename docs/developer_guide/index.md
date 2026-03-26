# Developer Guide

This guide covers the internal architecture, design patterns, and API reference for pyArgos. It is intended for developers who want to understand, extend, or contribute to the codebase.

---

## Data Model

- [**Data Model Reference**](data_model.md) - Domain concepts (experiments, trials, entities), ZIP file format, JSON schemas (v1.0.0/v2.0.0/v3.0.0), property types and scopes, version migration, directory structure

## Experiment Setup

The core module of pyArgos. Has its own dedicated section with architecture deep-dive, API reference, and links to the user guide.

- [**Experiment Setup**](experiment_setup_index.md) - Overview, architecture, API, and navigation hub
    - [Architecture](architecture/experiment_setup.md) - Inheritance, object lifecycle, property system, containment resolution
    - [API Reference](api/experiment_setup.md) - Class roles, swimlane workflows, autodoc for all classes

## Architecture

General architecture topics that span the entire system.

- [**Core Concepts**](architecture/core_concepts.md) - Class hierarchy, factory pattern, and design decisions
- [**Data Flow**](architecture/data_flow.md) - How data moves through the system end-to-end

## API Reference

Auto-generated API documentation for all other modules.

- [**Overview**](api/index.md) - Module map and import guide
- [**Experiment Manager**](api/manager.md) - ThingsBoard interface and experiment orchestration
- [**Kafka Consumer**](api/kafka.md) - Topic consumption and Parquet writing
- [**Node-RED**](api/nodered.md) - Custom nodes and flow management
- [**NoSQL (Cassandra & MongoDB)**](api/nosql.md) - Dask-based database interfaces
- [**Utilities**](api/utils.md) - JSON, Parquet, and logging helpers

## Reference

- [**Changelog**](../changelog.md) - Version history and release notes
