# Data Notes

This document records the data structure of the real EnergyPlus SQL export file used in this project.

## Data Source

The current sample file is exported from an EnergyPlus / Honeybee / Grasshopper simulation workflow.

The file name is:

run_sql_export.xlsx

This file is a converted Excel version of an EnergyPlus SQL output. It is not a simple wide table. It contains multiple database-like sheets.

## Workbook Structure

The workbook contains 39 sheets.

Important sheets include:

- ReportData_1
- ReportData_2
- ReportData_3
- ReportDataDictionary
- Time
- TabularData
- Surfaces
- Zones
- Materials
- Constructions

## Core Data Relationship

The main simulation result data is stored in:

- ReportData_1
- ReportData_2
- ReportData_3

These sheets have the same columns:

- ReportDataIndex
- TimeIndex
- ReportDataDictionaryIndex
- Value

The TimeIndex column links report data to the Time sheet.

The ReportDataDictionaryIndex column links report data to the ReportDataDictionary sheet.

Therefore, the main analysis workflow should be:

ReportData sheets + Time sheet + ReportDataDictionary sheet -> cleaned analysis table -> energy metrics -> charts and reports.

## Key Output Variables Found

The current file includes useful building performance variables such as:

- Zone Ideal Loads Supply Air Total Cooling Energy
- Zone Ideal Loads Supply Air Total Heating Energy
- Zone Ideal Loads Zone Total Cooling Energy
- Zone Ideal Loads Zone Total Heating Energy
- Enclosure Windows Total Transmitted Solar Radiation Energy
- Zone Lights Total Heating Energy
- Zone Electric Equipment Total Heating Energy
- Zone People Total Heating Energy
- Zone Mean Air Temperature
- Zone Operative Temperature
- Zone Air Relative Humidity
- Surface Window Heat Gain Energy
- Surface Window Heat Loss Energy
- Surface Inside Face Temperature
- Surface Outside Face Temperature

## Units

Many energy variables use J.

For reporting, they should be converted to kWh:

kWh = J / 3,600,000

Temperature variables use C.

Relative humidity uses %.

## Git Note

The original Excel file is large and should not be committed to Git.

The project should keep raw simulation files locally under data/, but Git should only track code, documentation, and small sample files.
## Known Time Data Issue

The Time sheet in the current Excel file is missing TimeIndex 5001.

The ReportData sheets still contain 247 result records for TimeIndex 5001, so these records could not initially be matched with a datetime.

The missing timestamp was confirmed as:

- TimeIndex: 5001
- Date: 2006-07-28
- Hour: 9
- Datetime: 2006-07-28 09:00:00

The analysis script detects missing TimeIndex values and reconstructs the complete hourly time table before merging it with ReportData.

After reconstruction:

- Time rows: 8760
- ReportData rows without datetime: 0