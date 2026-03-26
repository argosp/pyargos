# Developer Guide

This guide covers the internal architecture, design patterns, and API reference for pyArgos. It is intended for developers who want to understand, extend, or contribute to the codebase.

---

## Architecture

- [**Core Concepts**](architecture/core_concepts.md) - Class hierarchy, factory pattern, and design decisions
- [**Data Flow**](architecture/data_flow.md) - How data moves through the system end-to-end
- [**Experiment Setup**](architecture/experiment_setup.md) - Deep dive: inheritance, object lifecycle, property system, containment resolution

## API Reference

- [**Overview**](api/index.md) - Module map and import guide
- [**Experiment Setup**](api/experiment_setup.md) - Factories, data objects, entities, trials
- [**Experiment Manager**](api/manager.md) - ThingsBoard interface and experiment orchestration
- [**Kafka Consumer**](api/kafka.md) - Topic consumption and Parquet writing
- [**Node-RED**](api/nodered.md) - Custom nodes and flow management
- [**NoSQL (Cassandra & MongoDB)**](api/nosql.md) - Dask-based database interfaces
- [**Utilities**](api/utils.md) - JSON, Parquet, and logging helpers

## Reference

- [**Changelog**](../changelog.md) - Version history and release notes
