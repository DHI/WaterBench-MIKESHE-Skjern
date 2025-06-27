# Integrated Hydrological Model of Skjern Catchment
This README provides practical and background information on the dataset. The dataset can be cited as:

== Include citation after publishing ==

See the [license](license.txt) for details on data usage.

> ⚠️ **Important Disclaimer**    
> This model is **not calibrated** for operational use. It is intended for **educational and research purposes only**, and the results **must not** be used for decision-making. The performance shown here does **not** reflect that of DHI’s high-resolution models.


## Intended use

This dataset is designed to support educational, research, and exploratory activities, including:

* Experimenting with integrated hydrological modeling with MIKE SHE.
* Validating model outputs with insitu and remote sensing observational data.
* Testing and comparing model parameter calibration methods.
* Exploring how model outputs change with plenty vs. limited calibration data.
* Building data-driven models, including machine learning surrogates of MIKE simulation results.


## Folder structure

The repository is organized in the following way

- README.md
- license
- model
- input
- observations
- code
- figures
- output_sample

Separately from the current repository, you can find the output zip file (in Zenodo):

- output
    + MIKE model result data


## Introduction

## The MIKE 21 Flow Model FM

## Model validation

The [ModelSkill Python package](https://dhi.github.io/modelskill/) developed at DHI can be used to validate model outputs by comparing them to observational data.

## Data sources

### Altimetry data
