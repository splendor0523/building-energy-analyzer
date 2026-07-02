# Building Energy Result Analyzer

A Python-based analysis tool for building energy simulation results.

This project is designed for analyzing output data from EnergyPlus, Honeybee, and Grasshopper workflows. It will gradually support energy result cleaning, metric calculation, visualization, Streamlit dashboard display, Docker deployment, and automated report generation.

## Project Background

This project is built from an architecture and building performance simulation workflow. The target use case is to process building energy simulation result files and convert them into clear indicators, charts, and reports.

Typical indicators may include:

- Cooling load
- Heating load
- Solar heat gain
- Lighting load
- Equipment load
- Indoor air temperature
- Monthly energy use
- Peak load time
- Baseline vs shading strategy comparison

## Current Status

Day 15: Project initialization.

The current version only includes the basic project structure. Data reading and analysis scripts will be added in the following days.

## Project Structure

```text
building-energy-analyzer/
├── data/       # Raw or sample simulation result files
├── scripts/    # Python analysis scripts
├── output/     # Generated charts, CSV files, and reports
├── docs/       # Project notes and documentation
├── summary/    # Daily learning summaries
└── README.md
