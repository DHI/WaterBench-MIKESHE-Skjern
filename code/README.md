# Libraries used in these notebooks

To run the tutorials and fully explore this waterbench case, the following packages are required:

The user can clone the required packages from the requirements.yaml or requirements.txt files.

With conda:
```
conda env create -f requirements.yml
conda activate waterbench_skjern
```

# Where to start?

The example notebooks in this folder are meant to help the user navigate what the inputs and outputs of a MIKE SHE model might look like and how they can validate their model with observation data.

- **explore_input_data.ipynb** — *Exploring example input data files*
- **view_mikeshe_results.ipynb** — *Description and plots of example output files from MIKE SHE simulation and water balance post-processing tool*
- **model_validation.ipynb** — *Perform model validation of MIKE SHE outputs with river discharge and water table depth timeseries data*
- **tools.py** — *Helper module containing useful functions for above notebooks*
- **WellStats.py** — *Well statistics tool - used to estimate model performance at wells separated by well layer (depth levels below ground). Script provided by GEUS, see script header for more details.*
- **WS_config.xml** — *Configuration file for running well statistics tool.*

