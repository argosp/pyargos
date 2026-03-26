# Changelog

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
