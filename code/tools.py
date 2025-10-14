import re
from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import mikeio
import numpy as np
import rioxarray
import xarray
from mikeio import ItemInfo, EUMType, EUMUnit



def clip_2_box(ds_big, bbox=[0,0,0,0], input_crs=None): # for trimming xarray datasets
    
    xmin, ymin, xmax, ymax = bbox

    if type(ds_big) is mikeio.dataset._dataset.Dataset:
        if input_crs is None:
            raise ValueError("If input is a mikeio dataset, 'input_crs' must be provided.")
        
        # Convert to xarray before trimming
        ds_big = ds_big.to_xarray()
        ds_big.rio.write_crs(input_crs, inplace=True)
        

    if type(ds_big) is xarray.core.dataset.Dataset:
        ds_clip = ds_big.rio.clip_box(
        minx=xmin,
        miny=ymin,
        maxx=xmax,
        maxy=ymax,
    )
    return ds_clip # xarray dataset

def get_box(shp=None, dfs2=None, buffer=5000):
    if shp is None and dfs2 is None:
        raise ValueError("Either 'shp' or 'dfs2' must be provided.")
    if dfs2 is not None:
        xmin = np.min(dfs2.geometry.x)
        ymin = np.min(dfs2.geometry.y)
        xmax = np.max(dfs2.geometry.x)
        ymax = np.max(dfs2.geometry.y)
        return xmin, ymin, xmax, ymax
    if dfs2 is None and shp is not None:
        xmin, ymin, xmax, ymax = shp.total_bounds
        minx=xmin-buffer
        miny=ymin-buffer
        maxx=xmax+buffer
        maxy=ymax+buffer
    return minx, miny, maxx, maxy



def ds_2_dfs2(ds, new_filename, original_dfs2=None, name=None, unit=None,type=None, projection=None, new_dfs2_name=None, domain=None, plot_flag=False):

    if original_dfs2 is not None:
        name = original_dfs2[original_dfs2.items[0]].name
        unit = original_dfs2[original_dfs2.items[0]].unit
        type = original_dfs2[original_dfs2.items[0]].type
        projection = original_dfs2.geometry.projection

    time = pd.DatetimeIndex(ds['time'])
    geometry = mikeio.Grid2D(x=ds.x.values, y=ds.y.values, projection=projection)

    if new_dfs2_name is None:
        new_dfs2_name = name
    dfs2_out = mikeio.DataArray(data=ds[name].values,time=time, geometry=geometry, item=ItemInfo(new_dfs2_name, type, unit))
    mds_out = mikeio.Dataset([dfs2_out])
    mds_out.to_dfs(new_filename)

    if plot_flag:
        fig, ax = plt.subplots(figsize=(6, 6))
        mds_out[0].plot(title=f'DFS2 out {name}, t1',ax=ax)
        if domain is not None:
            domain.plot(facecolor='none', edgecolor='black',ax=ax)
        plt.show()

def read_plot_etv(filepath, variable='LAI', plot=True):
    """
    Built with help from CHATGPT 2025-07-15

    Parse a MIKE SHE .etv vegetation file and plot the selected variable (e.g., LAI, ROOT, Kc)
    
    Parameters:
        filepath (str): Path to the .etv file
        variable (str): Variable to extract and plot (e.g., 'LAI', 'ROOT', 'Kc')
        plot (bool): Whether to plot the results (default: True)
        
    Returns:
        dict of pd.DataFrame: Dictionary of vegetation name -> DataFrame with columns ['Stage', variable]
    """
    veg_data = defaultdict(list)
    current_veg = None
    current_stage = None
    veg_name = None

    with open(filepath, 'r') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        
        # Start of a vegetation block
        veg_match = re.match(r'\[VegNo_(\d+)\]', line)
        if veg_match:
            current_veg = f'VegNo_{veg_match.group(1)}'
            veg_name = None
            continue

        # Get VEGNAME
        if 'VEGNAME' in line and current_veg:
            match = re.search(r"VEGNAME\s*=\s*'([^']+)'", line)
            if match:
                veg_name = match.group(1)

        # Start of a stage
        stage_match = re.match(r'\[Stage_(\d+)\]', line)
        if stage_match and veg_name:
            current_stage = int(stage_match.group(1))
            continue

        # Extract the target variable
        if line.startswith(variable) and current_stage is not None and veg_name:
            try:
                value = float(line.split('=')[1].strip())
                veg_data[veg_name].append({'Stage': current_stage, variable: value})
            except ValueError:
                continue  # Skip malformed lines

    # Create DataFrames
    veg_dfs = {}
    for veg_name, stage_data in veg_data.items():
        df = pd.DataFrame(stage_data).sort_values('Stage')
        veg_dfs[veg_name] = df

    if plot:
        n_veg = len(veg_dfs)
        fig, axes = plt.subplots(n_veg, 1, figsize=(8, 20), sharex=True)
        if n_veg == 1:
            axes = [axes]  # make iterable if only one plot

        color_map = cm.get_cmap('tab20', n_veg)
        colors = [color_map(i) for i in range(n_veg)]

        for ax, (color, (veg_name, df)) in zip(axes, zip(colors, veg_dfs.items())):
            ax.plot(df['Stage'], df[variable], marker='o', color=color)
            ax.set_ylabel(variable)
            ax.set_title(veg_name, fontsize=10)
            ax.grid(True)

        axes[-1].set_xlabel('Development Stage')
        plt.tight_layout()
        plt.show()


    return veg_dfs
def plot_dfs2_output(filepath, varname=None, timeID=0, ax=None, shapefile=None,layerID=None, time1=None, time2=None):
    """
    Plot a dfs2 output file, averaged over a time range if provided, else at a specific time index.
    
    Parameters:
    - filepath: Path to the dfs2 file.
    - ax: Matplotlib axis to plot on (optional).
    - varname: Variable name to plot (optional, if not provided, first variable is used).
    - timeID: Time index to select from the dfs2 file (default is 0).
    - shapefile: Geopandas dataframe of shapefile to overlay (optional).
    - layerID: Layer index to select from dfs3 file (if applicable).
    - time1, time2: Time range to average over (if None, use full range).
    """
    ds = mikeio.read(filepath)
    if varname is None:
        varname = ds.variables[0].name

    
    if ax is None:
        fig, ax = plt.subplots(figsize=(9, 6))

    # check if time1 and time2 are provided for averaging
    if time1 is not None and time2 is not None:
        if len(ds[0].dims) == 4:
            data = ds[varname].sel(time=slice(time1, time2)).mean()[layerID]
            datestr = f"AVG {str(time1)} to {str(time2)}, L{layerID}"
        else:
            data = ds[varname].sel(time=slice(time1, time2)).mean()
            datestr = f"AVG {str(time1)} to {str(time2)}"

    else:
        # Check if dfs3 or dfs2
        if len(ds[0].dims) == 4:
            data = ds[varname][timeID,layerID]
        else:
            data = ds[varname][timeID]
        datestr = str(ds[varname][timeID].time[0])[0:10]

    #capitailize first letter of variable name
    varname_caps = varname.capitalize() if varname else "Variable"

    data.plot(ax=ax, cmap='viridis')
    ax.set_title(f"{varname_caps} {datestr}")

    # Check if shapefile is provided and plot it
    if shapefile is not None:
        shapefile.plot(facecolor='none', edgecolor='black',ax=ax)


    plot_settings(ax)
    
    return ax



def plot_settings(ax):
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel('')
    ax.set_ylabel('')
    # remove plot border
    for spine in ax.spines.values():
        spine.set_visible(False)

def plot_wb_output(filepath,title,varlist=None):
    wb = mikeio.read(filepath)
    wb_df = wb.to_dataframe() # For more plotting options

    if varlist is not None:
        wb_df = wb_df[varlist]

    fig, ax = plt.subplots(figsize=(12, 6))
    wb_df.plot(ax=ax,fontsize=15).legend(loc='center',bbox_to_anchor=(1.15,0.4))
    plt.ylabel('Storage Depth [mm]',fontsize=15)
    plt.title(label=title,fontsize=20)
    plt.show()