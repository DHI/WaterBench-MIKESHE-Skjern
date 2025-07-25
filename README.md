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
- earth_observation
    + Satellite altimetry
    + Sentinel-2 water masks
- code
    + tutorial notebooks
- MapsDK
    + \* Sample input data (*.dfs2, *.dfs0)
    + Domain shapefiles (/DKDomains2013)
    + \* Geological layer data (/dkmj2019)
    + River discharge observations (/Qdata)
    + Well water table depth observations (/Hdata)
    + MIKE Hydro river cross sections (/Mhydro/*.xns11)
- Skjern_Models/Setup
    + MIKE SHE model (.she)
    + MIKE Hydro model (.myhdro)
    + \* Model setup data (*.dfs2)
    + \* Results folder (/HIP_500m_Skjern_DHI.she - Result Files/)
- figures
- waterbalance_output

> \* Folders and/or files in this location are not all included in the current github repository due to large files sizes. Some sample files are included to run notebooks, but not everything for running a full MIKE SHE model is here. To be able to run the Skjern MIKE SHE model and calibration scripts, the following zip file should be downloaded from Zenodo: :construction:

- MapsDK.zip
    + Contains complete folders for model inputs (MapsDK) and setup (Skjern_Models)

:exclamation: :exclamation: ***The MapsDK.zip file should be downloaded and extracted, where the folders MapsDK and Skjern_Models are placed in the main WATERBENCH-MIKESHE-SKJERN directory. These contain the remaining input files needed for simulation and full use of this repository.***

## Introduction

## MIKE SHE Integrated Hydrological Model

## Model validation

The [ModelSkill Python package](https://dhi.github.io/modelskill/) developed at DHI can be used to validate model outputs by comparing them to observational data.

## Data sources

### Altimetry data

## Dependencies

To run the tutorials and fully explore this waterbench case, the following packages are required:

The user can clone the required packages from the requirements.yaml or requirements.txt files.

With conda:
```
conda env create -f requirements.yml
conda activate waterbench_skjern
```