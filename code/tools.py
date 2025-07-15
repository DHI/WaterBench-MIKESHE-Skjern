import re
from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm

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