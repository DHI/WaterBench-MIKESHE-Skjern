# -*- coding: utf-8 -*-
"""
WellStats

Tool to extract groundwater level statistics in observation wells
(as a replacement for LayerStatistics)
Can be used - as before - with head elevation in saturated zone output, but new 
also can be used with depth to phreatic output
Detailed documentation: http://geuswikihydro.geus.dk/w/index.php/Groundwater_level_scripts

NOTE: Requires mikeio v2.0.0 or above!

Usage: WellStats.py <WS_config.xml>
Output: groundwater statistics in 
    _observations.txt   : results per individual observation
    _wells.txt          : results per well
    _layers.txt         : results per layer
    _warnings.txt       : warnings (e.g. bottom below model)
    
WS_config.xml is a xml file of following format
    <?xml version="1.0"?>
    <Configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
      <PreProcessedDFS2>[path to PreProcessed.dfs2 file]</PreProcessedDFS2>
      <PreProcessedDFS3>[path to PreProcessed_3DSZ.dfs3 file]</PreProcessedDFS3>
      <ObservationFile>[path to WS_input observation file]</ObservationFile>
      <ResultFile>[path to 3DZS.dfs3 result file]</ResultFile>
      <HeadItemText>['head elevation in saturated zone' or 'depth to <top/bottom> phreatic surface (negative)']</HeadItemText>
      <PhreaticUseLayerBelow>[true/false]</PhreaticUseLayerBelow>
       <EpsilonForPhreatic>[threshold to determine dry layer]</EpsilonForPhreatic>
    </Configuration>

WS input observation file is of format (same as LS_input):
    ID          XUTM       YUTM        DEPTH   PEJL/WTDEPTH    DATO
    96.640_1    557799.5   6101940.4   14.5    41.32   01-01-2007
    107.153_2   586261     6201233     73.95   9.8     02-01-2007
    107.159_1   586310     6195354     22.56   11.31   02-01-2007
    ...         ...        ...         ...     ...     ...
with one line per individual observation, where
    'ID'                unique ID for each intake (combination of well and filter) (but there can be multiple observations per ID!)
    'XUTM' 'YUTM'       coordinates of the well (in same coordinate system as used by MIKE SHE)
    'DEPTH'             filter depth (depth from the surface to the middle or bottom of the filter) [m]
    'PEJL' / 'WTDEPTH'  absolute observed water level [m] / depth to water table (POSITIVE below surface) [m]
    'DATO'              date of observation (dd-mm-yyyy)


TODO: What to do about multiple coordinates / depths per Well ID? NOTE: Right 
now, there is a warning generated; but stats are still extracted, at MEDIAN 
value of x, y, z per well ID
TODO: Add interpolation in time to sim_cell? Right now, nearest in x, y, z, time
TODO: Avoid interpolation in time if result files are daily (faster/less memory), 
but just use nearest

Raphael Schneider, rs@geus.dk, Sep 2024
"""

import sys, os, gc
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
import xarray as xr

import mikeio
import warnings
# ignore unnecessary mikeio warning
warnings.filterwarnings('ignore', message='Time step is 0.0 seconds. This must be a positive number. Setting to 1 second.')


def main():
    #%% STEP 0: command line handling - could be extended (getopt?). Or: handle everything in WS_config.xml
    if len(sys.argv) != 2:
        sys.exit('Usage: WellStats.py <WS_config.xml>')
    fp_config = sys.argv[1]
    # IF TESTING FROM IDE
    # fp_config=r'\\geodata.geus.dk\Dkmodel-hydro\Hdata\jup_pej2024\WSinput\obs_DKMNret500m_comparison\DK1_2024_conf.xml'
    # fp_config = r'\\geodata.geus.dk\DKmodel_users\FloodWarning\GWH_emulator\ed-LSTM\GWH_obs\WSInput\DK1_2024_conf_dtp.xml'
    
    
    #%% STEP 1: Load everything
    # Parse the XML config file
    xml = ET.parse(fp_config).getroot()
    conf = {}
    for el in xml:
        conf[el.tag] = el.text
    conf['EpsilonForPhreatic'] = float(conf['EpsilonForPhreatic'])
    # file path handling - can be absolute and relative (to fp_config!)
    def obtain_filepath(fp_xml):
        if os.path.isabs(fp_xml):
            return fp_xml
        else:
            return os.path.join(os.path.dirname(fp_config), fp_xml)
    fp_obsin = obtain_filepath(conf['ObservationFile'])
    fp_pp2d = obtain_filepath(conf['PreProcessedDFS2'])
    fp_pp3d = obtain_filepath(conf['PreProcessedDFS3'])
    fp_res = obtain_filepath(conf['ResultFile'])
    # "normal" WellStats or depth to phreatic top or bottom?
    if (conf['HeadItemText'] == 'depth to top phreatic surface (negative)') | (conf['HeadItemText'] == 'depth to phreatic surface (negative)'):
        stat_type = 'dtp'
    elif (conf['HeadItemText'] == 'depth to bottom phreatic surface (negative)'):
        stat_type = 'dtb'
    elif (conf['HeadItemText'] == 'head elevation in saturated zone'):
        stat_type = 'head'
    else:
        sys.exit(""""ERROR: 'HeadItemText' must be one of
                         head elevation in saturated zone
                         depth to top phreatic surface (negative)
                         depth to bottom phreatic surface (negative)
                         depth to phreatic surface (negative)!""")
    # dictionary with 'osbervation' column headings
    obs_col = {'dtp':   'WTDEPTH', 
               'dtb':   'WTDEPTH', 
               'head':  'PEJL'}
    # initialize list of warnings
    out_warn = []
    
    # Load the WS input file (observation data)
    WS = pd.read_csv(fp_obsin, sep='\t', index_col=0, parse_dates=['DATO'], date_format='%d-%m-%Y', 
                     dtype={'XUTM':np.float32, 'YUTM':np.float32, 'DEPTH':np.float32, obs_col[stat_type]:np.float32})
    if ((stat_type=='dtp') | (stat_type=='dtb')) & (WS.columns.isin(['WTDEPTH']).sum()==0):
        sys.exit("ERROR: Specified dtp as HeadItemText (stats type), but no column 'WTDEPTH' in observations input file!")
    if (stat_type=='head') & (WS.columns.isin(['PEJL']).sum()==0):
        sys.exit("ERROR: Specified head as HeadItemText (stats type), but no column 'PEJL' in observations input file!")
    if 'comment' not in WS.columns:
        WS['comment'] = pd.NA
    WS = WS.astype({'comment':'str'}) #convert to string[pandas] to allow easier handling later
    WS['comment'] = WS['comment'].apply(lambda x: pd.NA if x=='nan' else x)
    
    # Get the topo, layer boundaries etc from PreProcessed files
    # model boundaries
    mb_ds = mikeio.read(fp_pp2d, items='Model domain and grid', time=0).to_xarray()
    szb_ds = mikeio.read(fp_pp3d, items='Boundary conditions for the saturated zone', time=0, layers=-1).to_xarray() #layers=1: uppermost
    # surface topography
    top_ds = mikeio.read(fp_pp2d, items='Surface topography', time=0).to_xarray() #time=0 obtains dataset as 2D instead of 3D
    # lower level of comp layers
    ll_ds = mikeio.read(fp_pp3d, items='Lower level of computational layers in the saturated zone', time=0).to_xarray()
    
    # find timesteps to fully include period covered by result file
    gwl_temp = mikeio.open(fp_res)
    ts_s = WS['DATO'].min(); ts_e = WS['DATO'].max()
    ti_s = gwl_temp.time.get_indexer([ts_s], method='pad')[0] - 1
    if ti_s < 0:
        # accept 14 days missing overlap - if more, print warning
        if (gwl_temp.time[0]-ts_s)>timedelta(days=14):
            warning = f"WARNING: First timestep in observations {ts_s} more than 14 days before first timestep in results {gwl_temp.time[0]}"
            out_warn.append(warning)
            print(warning)
        ts_s = gwl_temp.time[0]
    else:
        ts_s = gwl_temp.time[ti_s]
    ti_e = gwl_temp.time.get_indexer([ts_e], method='backfill')[0]
    if ti_e < 0:
        # accept 14 days missing overlap - if more, print warning
        if (ts_e-gwl_temp.time[-1])>timedelta(days=14):
            warning = f"WARNING: Last timestep in observations {ts_e} more than 14 days after last timestep in results {gwl_temp.time[-1]}"
            out_warn.append(warning)
            print(warning)
        ts_e = gwl_temp.time[-1]
    else:
        ts_e = gwl_temp.time[ti_e]
    del gwl_temp; gc.collect() #release memory
    
    # read simulated groundwater heads
    gwl = mikeio.read(fp_res, items=conf['HeadItemText'], 
                     time=slice(ts_s, ts_e))[conf['HeadItemText']].to_xarray()
    # allow for "extrapolation" of sim_intp using .interp() by adding (repeating) missing timestep
    if ti_s < -1: #add new first timestep to cover obs period
        added = gwl.isel(time=0).expand_dims(time=[WS['DATO'].min() - timedelta(days=1)])
        gwl = xr.concat([added, gwl], dim='time')
    if ti_e < 0: #add new last timestep to cover obs period
        added = gwl.isel(time=-1).expand_dims(time=[WS['DATO'].max() + timedelta(days=1)])
        gwl = xr.concat([gwl, added], dim='time')
    
    
    #%% STEP 2: Obtain all metadata
    # warn if non-uniqe values per intake exist - should not happen!
    for col in ['XUTM', 'YUTM', 'DEPTH']:
        temp = WS.groupby(WS.index)[col].nunique()
        problems = temp[temp > 1]
        if len(problems) > 0:
            for prob_wid, _ in problems.items():
                warning = f"WARNING: Multiple unique values for {col} found in well {prob_wid}: {WS.loc[prob_wid,col].unique()}"
                out_warn.append(warning)
                print(warning)
            
    # initialize out_well: data per intake
    out_well = WS[['XUTM', 'YUTM', 'DEPTH']].groupby(WS.index).median()
    out_well.rename(columns={'XUTM':'x', 'YUTM':'y', 'DEPTH':'depth'}, inplace=True)
    # add new and re-arrange columns to final order
    out_well = out_well.reindex(columns=['obs_mean','sim_mean','ME','MSE','x','y',
                                         'depth','layer','topo','z_bottoms','ix',
                                         'iy','nobs','boundary','comment'])
    #Set the type to object to allow storing of lists and strings
    out_well[['ix','iy','layer','nobs','boundary']] = out_well[['ix','iy','layer','nobs','boundary']].fillna(-99)
    out_well = out_well.astype({'layer':'int', 'z_bottoms':'object', 'ix':'int', 
                                'iy':'int', 'nobs':'int', 'comment':'string', 'boundary':'int'})
    
    # initialize out_obs: data per individual observation
    out_obs = WS.copy(deep=True)
    out_obs.rename(columns={'XUTM':'x', 'YUTM':'y', 'DEPTH':'depth', 
                            obs_col[stat_type]:'obs_value', 'DATO':'dato', 'BERELAG':'layer'}, 
                   inplace=True)
    # add new and re-arrange columns to final order
    out_obs = out_obs.reindex(columns=['dato','obs_value','sim_intp','sim_cell',
                                       'err','err2','x','y','depth','layer',
                                       'z_bottoms','dry','boundary','ix','iy',
                                       'nobs','comment'])
    #Set the type to object to allow storing of lists and strings
    out_obs[['ix','iy','layer','nobs','boundary']] = out_obs[['ix','iy','layer','nobs','boundary']].fillna(-99)
    out_obs = out_obs.astype({'layer':'int', 'z_bottoms':'object', 'dry':'string', 
                              'ix':'int', 'iy':'int', 'nobs':'int', 'boundary':'int'})
    """
    Get more metadata:
    * comments (in out_well: all unique combinations from WS input, ';' separated)
    * IX, IY, IZ
    * nobs per well, obs_mean
    * obtain computational layer per intake, and all layer bottoms to allow 
      "jumping down" in case of drying out
    """
    out_obs.loc[:,'nobs'] = WS.groupby(WS.index).count()['DATO'].astype(int)
    out_well['nobs'] = WS.groupby(WS.index).count()['DATO'].astype(int)
    out_well['obs_mean'] = WS.groupby(WS.index)[obs_col[stat_type]].mean()
    out_well['comment'] = WS.groupby(WS.index)['comment'].apply(lambda x: ';'.join(x.dropna().unique()) if x.dropna().size > 0 else pd.NA)
    # topography and lower levels of computational layers (nearest; no interpolation)
    temp_xr = xr.Dataset({'x': (['index'], out_well['x'].values), 
                            'y': (['index'], out_well['y'].values)}, 
                      coords={'index': out_well.index.values})
    # check if well outside model domain (and remove if it is!)
    mb = mb_ds['Model domain and grid'].sel(temp_xr, method='nearest')
    problems = out_well[(mb!=1).values]
    if len(problems) > 0:
        for prob_wid, prob in problems.iterrows():
            warning = f"ERROR: Well {prob_wid} at X {prob.x} Y {prob.y} outside model boundary! Will be ignored."
            out_warn.append(warning)
            print(warning)
        # remove wells outside model boundary
        out_well.drop(index=problems.index, inplace=True)
        out_obs.drop(index=problems.index, inplace=True)
        temp_xr = xr.Dataset({'x': (['index'], out_well['x'].values), 
                                'y': (['index'], out_well['y'].values)}, 
                          coords={'index': out_well.index.values})
    # check if well in SZ boundary condition
    szb = szb_ds['Boundary conditions for the saturated zone'].sel(temp_xr, method='nearest')
    problems = out_well[(szb!=1).values]
    if len(problems) > 0:
        for prob_wid, prob in problems.iterrows():
            warning = f"WARNING: Well {prob_wid} at X {prob.x} Y {prob.y} not in 'normal' SZ boundary 1 but in {szb.loc[prob_wid].values:.0f}!"
            out_warn.append(warning)
            print(warning)
    out_well['boundary'] = szb.astype(int)
    top = top_ds['Surface topography'].sel(temp_xr, method='nearest')
    out_well['topo'] = top
    #get coordinate list
    xgrids = top_ds.x.values; ygrids = top_ds.y.values
    if not ( (np.all(xgrids[:-1] < xgrids[1:])) & (np.all(ygrids[:-1] < ygrids[1:])) ):
        sys.exit('ERROR: Grid coordinates of model output not sorted.')
    xws = top.x.values; yws = top.y.values #x and y of nearest cell (to get ix and iy)
    out_well['ix'] = np.searchsorted(xgrids, xws)
    out_well['iy'] = np.searchsorted(ygrids, yws)
    ll = ll_ds['Lower level of computational layers in the saturated zone'].sel(temp_xr, method='nearest').values
    # check that all layer bottoms are strictly decreasing
    if np.all(np.diff(ll, axis=0) < 0, axis=0).sum() > 0:
        sys.exit('ERROR: Lower levels of computational layers not strictly decreasing.')
    # For depth to top phreatic: check whether wells likely are representing depth to phreatic
    if stat_type=='dtp':
        problems = out_well[(out_well['depth'] > 10) & ~(out_well.comment.str.find('Trni')>=0)]
        if len(problems) > 0:
            for prob_wid, prob in problems.iterrows():
                warning = f"WARNING: Well {prob_wid} has depth of {prob.depth:.2f}m and no marker 'Trni'. Are you certain it represents depth to top phreatic?"
                out_warn.append(warning)
                print(warning)
    del top, top_ds, ll_ds, szb, szb_ds, mb, mb_ds, temp_xr, WS; gc.collect() #release memory

    # get "i_top" (number of layers)
    itop = int(ll.shape[0]) - 1
    # loop well by well to obtain iz
    iw = 0
    for wid, row in out_well.iterrows():
        x = row.x; y = row.y; ctop = row.topo
        cll = ll[:,iw]
        f_elev = ctop - row.depth # filter depth as absolute elevation
        # check filter depth in relation to layers
        if f_elev > ctop: #filter is above topography
            iz = itop
            if pd.isna(out_well.loc[wid, 'comment']):
                out_well.loc[wid, 'comment'] = 'AboveTopography'
            else:
                out_well.loc[wid, 'comment'] += ';AboveTopography'
            warning = f"WARNING: Well {wid} at X {x:.0f} Y {y:.0f}: {f_elev-ctop:.2f}m above topography at {ctop:.2f}m. Use uppermost layer."
            out_warn.append(warning)
            print(warning)
        elif f_elev < cll[0]: #filter is below lowest layer
            iz = 0
            if pd.isna(out_well.loc[wid, 'comment']):
                out_well.loc[wid, 'comment'] = 'BelowLowestLayer'
            else:
                out_well.loc[wid, 'comment'] += ';BelowLowestLayer'
            warning = f"WARNING: Well {wid} at X {x:.0f} Y {y:.0f}: {cll[0]-f_elev:.2f}m below lowest layer {cll[0]:.2f}m. Use lowest layer."
            out_warn.append(warning)
            print(warning)
        else: # filter is between lowest layer bottom and topo: if (f_elev >= cll[0]) & (f_elev <= ctop):
            iz = int(np.max(np.where(cll <= f_elev)[0]))
        out_well.loc[wid, 'layer'] = iz
        out_well.at[wid, 'z_bottoms'] = list(cll) #use .at to assign list to single element of dataframe
        iw += 1
    
    # map to out_obs (FASTER than doing in loop above)
    out_obs['z_bottoms'] = out_obs.index.map(out_well['z_bottoms'])
    out_obs['layer'] = out_obs.index.map(out_well['layer'])
    out_obs['ix'] = out_obs.index.map(out_well['ix'])
    out_obs['iy'] = out_obs.index.map(out_well['iy'])
    out_obs['boundary'] = out_obs.index.map(out_well['boundary'])
    out_obs['comment'] = out_obs.index.map(out_well['comment'])
    
    del ll; gc.collect() #release memory
    
    # exit here if no valid observations (outside model boundary etc)
    if len(out_obs) == 0:
        sys.exit('ERROR: None of the observations are valid (outside model boundary etc).')
    

    #%% STEP 3: Obtain the actual simulation data
    # for "normal" WellStats when head data are output
    if stat_type=='head':
        temp_xr = xr.Dataset({'x': (['index'], out_obs['x'].values), 
                                'y': (['index'], out_obs['y'].values), 
                                'z': (['index'], out_obs['layer']),
                                'time': (['index'], out_obs['dato'].values)}, 
                          coords={'index': out_obs.index.values})
        temp_xr_below = xr.Dataset({'x': (['index'], out_obs['x'].values), 
                                'y': (['index'], out_obs['y'].values), 
                                'z': (['index'], (out_obs['layer'] - 1).clip(lower=0)), #limit to layer=0, i.e. lowest layer
                                'time': (['index'], out_obs['dato'].values)}, 
                          coords={'index': out_obs.index.values})
        gwl_sim_cell = gwl.sel(temp_xr, method='nearest')
        gwl_sim_cell_below = gwl.sel(temp_xr_below, method='nearest')
        """
        Ideally, gwl_sim_cell would also be interpolated in time. As of now, nearest ts!
        gwl_sim_cell = gwl_sim_cell.interp(time=temp_xr['time'], method='linear')
        """
        """
        Calculation below is done layer by layer. To save RAM.
        The simpler method would be 
            gwl_sim_intp = gwl.interp(temp_xr, method='linear')
        However, excessive RAM usage and only marginally faster
        """
        gwl_sim_intp = gwl_sim_cell.copy(deep=True)
        for l in range(itop,-1,-1):
            temp = out_obs.loc[out_obs['layer']==l, :]
            temp_xr_l = xr.Dataset({'x': (['index'], temp['x'].values), 
                                    'y': (['index'], temp['y'].values), 
                                    'time': (['index'], temp['dato'].values)}, 
                              coords={'index': temp.index.values})
            mask = gwl_sim_intp['z'].values == l
            if mask.sum() > 0:
                sim_intp = gwl.sel({'z':l}).interp(temp_xr_l, method='linear')
                gwl_sim_intp.values[mask] = sim_intp.values  # Direct assignment
            
        """
        Determine dry layer based on same method MIKE SHE uses to calcualte depth 
        to phreatic. Dry if:
            Saturated thickness of current layer < epsilon
            AND
            UNsaturated thickness of layer below > epsilon
        Where epsilon typically is between 0.02m and 0.10m; see here:
            http://geuswikihydro.geus.dk/w/index.php/Depth_to_phreatic_surface
        and hard-coded here in the .xml config file
        """
        # find current layer bottoms, and bottoms of layer one below
        bottoms = out_obs.apply(lambda row: row['z_bottoms'][row['layer']], axis=1)
        # determine dry cells based on SIM_CELL only! (but replace values for both)
        dry = (gwl_sim_cell < (bottoms + conf['EpsilonForPhreatic'])) & \
            (gwl_sim_cell_below < (bottoms - conf['EpsilonForPhreatic']))
        del temp_xr, temp_xr_below; gc.collect() #release memory
        if dry.sum() > 0:
            iz_below = 0
            while dry.sum() > 0: #find lower layer values in case layer is dry, and proceed until layer not dry anymore
                dry_init_i = dry.copy() #get current dry init
                iz_below += 1
                temp_xr = xr.Dataset({'x': (['index'], out_obs['x'].values), 
                                      'y': (['index'], out_obs['y'].values), 
                                      'z': (['index'], (out_obs['layer'] - iz_below).clip(lower=0)),
                                      'time': (['index'], out_obs['dato'].values)}, 
                                     coords={'index': out_obs.index.values})
                temp_xr_below = xr.Dataset({'x': (['index'], out_obs['x'].values), 
                                      'y': (['index'], out_obs['y'].values), 
                                      'z': (['index'], (out_obs['layer'] - iz_below - 1).clip(lower=0)),
                                      'time': (['index'], out_obs['dato'].values)}, 
                                     coords={'index': out_obs.index.values})
                gwl_sim_cell_dry = gwl.sel(temp_xr, method='nearest')
                gwl_sim_cell_below_dry = gwl.sel(temp_xr_below, method='nearest')
                """
                Again, calculation below is done layer by layer. To save RAM.
                The simpler method would be 
                    gwl_sim_intp_dry = gwl.interp(temp_xr, method='linear')
                However, excessive RAM usage and only marginally faster
                """
                gwl_sim_intp_dry = gwl_sim_cell.copy(deep=True)
                for l in range(itop,-1,-1):
                    temp = out_obs.loc[out_obs['layer']==l, :]
                    temp_xr_l = xr.Dataset({'x': (['index'], temp['x'].values), 
                                            'y': (['index'], temp['y'].values), 
                                            'time': (['index'], temp['dato'].values)}, 
                                      coords={'index': temp.index.values})
                    mask = gwl_sim_intp_dry['z'].values == l
                    if mask.sum() > 0:
                        sim_intp = gwl.sel({'z':max(l - iz_below, 0)}).interp(temp_xr_l, method='linear')
                        gwl_sim_intp_dry.values[mask] = sim_intp.values  # Direct assignment
                bottoms_dry = out_obs.apply(lambda row: row['z_bottoms'][max(row['layer'] - iz_below, 0)], axis=1)
                dry = dry & (gwl_sim_cell_dry.values < (bottoms_dry + conf['EpsilonForPhreatic'])) & \
                    (gwl_sim_cell_below_dry.values < (bottoms_dry - conf['EpsilonForPhreatic']))
                # remove dry value marker if we already reached bottom layer (layer < 0)
                dry = dry & ((out_obs['layer'] - iz_below)>=0)
                # not dry anymore in this step - replace values
                not_dry_i = (dry_init_i & ~dry)
                out_obs.loc[not_dry_i.values, 'dry'] = f'Layer dry - {iz_below} below'
                # replace values from lower layer where current layer NOT is dry
                gwl_sim_cell[not_dry_i] = gwl_sim_cell_dry[not_dry_i]
                gwl_sim_intp[not_dry_i] = gwl_sim_intp_dry[not_dry_i]
                del gwl_sim_cell_dry, gwl_sim_cell_below_dry, gwl_sim_intp_dry, temp_xr, temp_xr_below, bottoms_dry; gc.collect() #release memory
        del gwl; gc.collect() #release memory
    
    # for depth to phreatic output
    elif (stat_type=='dtp') | (stat_type=='dtb'):
        temp_xr = xr.Dataset({'x': (['index'], out_obs['x'].values), 
                                'y': (['index'], out_obs['y'].values), 
                                'time': (['index'], out_obs['dato'].values)}, 
                          coords={'index': out_obs.index.values})
        gwl_sim_cell = gwl.sel(temp_xr, method='nearest')
        gwl_sim_intp = gwl.interp(temp_xr, method='linear')
        # flip sign to follow convention with positive values below ground!
        gwl_sim_cell = -gwl_sim_cell
        gwl_sim_intp = -gwl_sim_intp
   
    
    #%% STEP 4: Assign values to out dataframes
    # observation output
    out_obs['sim_cell'] = gwl_sim_cell
    out_obs['sim_intp'] = gwl_sim_intp
    out_obs['err'] = out_obs['obs_value'] - out_obs['sim_intp']
    out_obs['err2'] = out_obs['err']**2
    
    # add well aggregated values
    out_well['sim_mean'] = out_obs.groupby(out_obs.index)['sim_intp'].mean()
    out_well['ME'] = out_obs.groupby(out_obs.index)['err'].mean()
    out_well['MSE'] = out_obs.groupby(out_obs.index)['err2'].mean()
    
    # reverse MIKE-internal z-indexing (0: lowest layer, zmax-1: top) to intuitive z-indexing (1: top layer, zmax: lowest)
    out_obs['layer'] = itop + 1 - out_obs['layer']
    out_well['layer'] = itop + 1 - out_well['layer']
    
    # layer output
    if stat_type=='head':
        out_lay = pd.DataFrame(index=range(1, itop+2), #layers 1 (top layer) to itop+1 (bottom layer)
                               columns=['RMSE_wells','RMSE_obs','ME_wells','ME_obs','nwells','nobs'])
        for il, row in out_lay.iterrows():
            out_lay.loc[il, 'RMSE_wells'] = np.sqrt(out_well.loc[out_well['layer']==il, 'MSE'].mean())
            out_lay.loc[il, 'RMSE_obs'] = np.sqrt((out_obs.loc[out_obs['layer']==il, 'err2']).mean())
            out_lay.loc[il, 'ME_wells'] = out_well.loc[out_well['layer']==il, 'ME'].mean()
            out_lay.loc[il, 'ME_obs'] = out_obs.loc[out_obs['layer']==il, 'err'].mean()
            out_lay.loc[il, 'nwells'] = out_well.loc[out_well['layer']==il].shape[0]
            out_lay.loc[il, 'nobs'] = out_obs.loc[out_obs['layer']==il].shape[0]
    
    
    #%% STEP 5: Write output to text files
    fp_stump = os.path.splitext(fp_obsin)[0]
    fp_ext = os.path.splitext(fp_obsin)[1]
    fp_obs =  f'{fp_stump}_observations{fp_ext}' 
    fp_well = f'{fp_stump}_wells{fp_ext}' 
    fp_lay = f'{fp_stump}_layers{fp_ext}' 
    fp_warn = f'{fp_stump}_warnings{fp_ext}' 
    
    out_obs.drop(columns=['z_bottoms','boundary']).to_csv(fp_obs, sep='\t', index_label='OBS_ID')
    out_well.drop(columns=['z_bottoms']).to_csv(fp_well, sep='\t', index_label='OBS_ID')
    if stat_type=='head':
        out_lay.to_csv(fp_lay, sep='\t', index_label='Layer')
    with open(fp_warn, 'w') as f:
        for w in out_warn:
            f.write(w + '\n')


#%%
if __name__ == "__main__":
    main()
