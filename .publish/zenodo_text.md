# Integrated Hydrological Model of Skjern Å catchment: MIKE SHE model setup, inputs, outputs and observation data

## Description

**MIKE SHE** is an integrated hydrological modeling system that emerged in the 1980s to represent the physical processes of water flow through the hydrological cycle in a modular way and with relevant scale. The available process modules - evapotranspiration, overland flow, unsaturated zone flow, groundwater flow, channel flow - are each governed by their relevant partial differential equations describing the movement of water through their system. This repository contains an example model setup, inputs, outputs and observation data for a MIKE SHE Integrated Hydrological Model of the Skjern River catchment located on the west coast of Jutland, Denmark. This model is a subset of the DK-model developed by **GEUS** (see [DK-model](https://www.geus.dk/vandressourcer/vandets-kredsloeb/den-nationale-hydrologiske-model)).


This dataset is part of the **WaterBench** series by DHI, supporting open research on water-related challenges. It is intended for **educational and research purposes only**, such as model validation, parameter calibration, and machine learning applications. The model resolution has been reduced from 100m to 500m grid cells compared to the DK-model and is **uncalibrated**. The performance shown here does **not** reflect that of DHI's high-resolution models. **Results must not be used for decision-making.**

Files:

* **README**. Description of dataset with details on citations, data processing, and background information. 
* **WaterBench-MIKESHE-SKjern.zip**: model setup, input data, observational data, and code for data exploration and model validation. 
* **Waterbench-MIKESHE-SKjern-output.zip**: result files (Actual evapotranspiration, head elevation in saturated zone, groundwater flow, etc.) for 20 years of simulation.


## DOI

## Contributors
* Sarah E. Franze
* Henrik Andersson
* Jesper Sandvig Mariegaard

## Publication date


## Funding
This work for compiling this dataset was funded via Novo Nordisk Foundation (NNF) Grant Number NNF23OC0081089, as part of the Global Wetland Center.

## Software
[https://github.com/DHI/WaterBench-MIKESHE-Skjern](https://github.com/DHI/WaterBench-MIKESHE-Skjern)