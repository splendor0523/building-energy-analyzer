# Data Notes

This document records the expected data structure for the Building Energy Result Analyzer project.

## Data Source

The target data source will come from building performance simulation workflows, such as:

- EnergyPlus SQL output
- Honeybee simulation results
- Grasshopper-exported tables
- Excel or CSV files converted from simulation outputs

## Expected File Types

The project will first support:

- `.xlsx`
- `.csv`

SQL files may be processed later after the basic workflow becomes stable.

## Expected Fields

The exact field names will be decided after checking the real exported sample data.

Potential fields may include:

- datetime
- cooling_load
- heating_load
- solar_gain
- lighting_load
- equipment_load
- indoor_temperature
- case_name

## Day 15 Notes

No real data has been imported yet.

The focus of Day 15 is to initialize the project structure and prepare for real simulation result analysis.
