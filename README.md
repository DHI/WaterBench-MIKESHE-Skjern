# Integrated Hydrological Model of Skjern Catchment
This README provides practical and background information on the dataset. The dataset can be cited as:

== Include citation after publishing ==

See the [license](license.txt) for details on data usage.

> ⚠️ **Important Disclaimer**    
> This model is **not calibrated** for operational use. It is intended for **educational and research purposes only**, and the results **must not** be used for decision-making. The performance shown here does **not** reflect that of DHI’s high-resolution models.


## Intended use

This dataset is designed to support educational, research, and exploratory activities, including:

* Experimenting with integrated hydrological modeling with MIKE SHE.
* Changing model parameters and running simulations with the MIKE SHE Python API.
* Validating model outputs with insitu and remote sensing observational data.
* Testing and comparing model parameter calibration methods.
* Exploring how model outputs change with plenty vs. limited calibration data.
* Building data-driven models, including machine learning surrogates of MIKE simulation results.


## Folder structure

The repository is organized in the following way

- README.md
- license
- observations
    + River gauge data
    + Satellite altimetry
- code
    + tutorial notebooks
- figures
- output_sample

Separately from the current repository, you can find the output and input zip files (in Zenodo):

- input (MapsDK.zip)
    + Contains folders for model inputs (MapsDK) and Setup (Skjern_Models)
    + Input dfs2 and dfs0 data files for model setup and forcings
    + MIKE SHE model file (.she)
    + MIKE Hydro model file (.mhydro)

- output
    + MIKE model result data

***To run notebooks in this repository, the MapsDK.zip file should be downloaded and extracted, where the folders MapsDK and Skjern_Models are placed in the main WATERBENCH-MIKESHE-SKJERN directory.***

## Introduction

## MIKE SHE Integrated Hydrological Model

## Model validation

The [ModelSkill Python package](https://dhi.github.io/modelskill/) developed at DHI can be used to validate model outputs by comparing them to observational data.

## Data sources

### Altimetry data

### Dependencies

To run the tutorials and fully explore this waterbench case, the following packages are required:

The user can clone the required packages from the requirements.yaml or requirements.txt files.

With conda:
```
conda env create -f requirements.yml
conda activate waterbench_skjern
```