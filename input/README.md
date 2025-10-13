*List of input files from:*

### Model Domain and Grid (`../input/domain/`)
- **Skjern.shp** — *Catchment shapefile of Skjern*

### Topography (`../input/topography/`)
- **dkmj_topo_0.dfs2** — *DEM (500m resolution)*

### Climate (`../input/climate/`)
- **DK_DMI_Corr_Precip_10km_1989-2022.dfs2** — *Preciitation rate, Distributed time series [mm/day]*
- **DK_ETref_0.95west_of_storebaelt_20km_1989-2022.dfs2** — *Reference Evapotranspiration rate, Distributed time series [mm/day]*
- **DK_Ta_20km_1989-2022.dfs2** — *Daily Air Temperature [C]*

### Land Use (`../input/land_use/`)
- **DK_Landuse_9classes_5cropsCorr_100m_MB500.dfs2** — *Vegeration 2D classification grid codes*
- **DK_2018_Veg_Prop_inv_100m.etv** — *Vegetation property file, Time series* 
- **irrigation_depth_class_100m_hav_2_newgeology.dfs2** — *Irrigation well depth codes*
- **License_limitated_irrigation_DK5_50mm.dfs0** — *Irrigation well timeseries [m^3]*
- **crop_map_irrigation_5class_500m.dfs2** — *Irrigation demand - crop irrigation class grid codes*
- **Deficit_factor_5veg_inv.dfs0** — *Moisture deficit time series [Fraction]*

### Rivers, Lakes and Sewers (`../input/rivers_lakes_sewers/`)
- **HIP_500m_mh_Skjern_DHI.mhydro** — *MIKE Hydro River Network file (cross sections, river boundary conditions, river shapefiles contained here)*
- **500m_Skjern.xns11** — *Cross section file for MIKE Hydro setup*
- **ManningM_Res_fac_DK2020.dfs0** — *Bed roughness information*

### Overland Flow (`../input/overland/`)
- **dk_manning500m.dfs2** — *Manning number, Distributed*  
- **dk_pavedcoef500m_inv.dfs2** — *Paved area fraction, Distributed*  
- **DK_ID15_opl_ver20_HIP500m.dfs2** — *Drain codes*  

### Unsaturated Flow (`../input/unsaturated/`)
- **DK_soil_georeg_250m-50m.dfs2** — *Two-Layer UZ Soil Codes*  
- **DK_ID15_opl_ver20_HIP500m.dfs2** — *Drain codes* 


### Saturated Zone (`../input/saturated/`)
#### > Geological Layers (`../input/saturated/geological_layers/`)
- **dkmj_k\*\*\*.dfs2 AND dkmj_kalk50m.dfs2** — *Geologic layer lower level elevation map [m]*  
- **DK456_Kx_Kalk_inv.dfs2** — *Horizontal Hydraulic Conductivity, Distributed*  
- **DK456_Kz_Kalk_inv.dfs2** — *Vertical Hydraulic Conductivity, Distributed*  

#### > Geological Lenses (`../input/saturated/geological_lenses/`)
J25200 lens
- **dkmj_topo.dfs2** — *Lens upper level elevation map [m]*
- **dkmj_subsoil_type.dfs2** — *Lens lower level elevation map [m]*
- **DK_j25200sea_9classes_3regions100m_Kx_Inv_500mMB.dfs2** — *Horizontal Hydraulic Conductivity, Distributed*
- **DK_j25200sea_9classes_3regions100m_Kz_Inv_500mMB.dfs2** — *Vertical Hydraulic Conductivity, Distributed*  

Salt lens
- **dkmj_sk1b.dfs2** — *Lens upper level elevation map [m]*
- **dkmj_ss1b.dfs2** — *Lens lower level elevation map [m]*

Sea lens
- **dkmj_sea.dfs2** — *Horizontal extent, distributed*
- **dkmj_topo_0.dfs2** — *Lens upper level elevation map [m]*
- **dkmj_topo.dfs2** — *Lens lower level elevation map [m]*

#### > Computational Layers (`../input/saturated/computational_layers/`)
- **dkmj_k\*\*\*.dfs2 AND dkmj_top2m.dfs2 AND dkmj_bottom.dfs2** — *Computational layer lower level elevation map [m]*  
- **dk_h_mean00_06_lay\*\*.dfs2** — *Initial potential head for each computational layer [m]*
- **DK_internal_boundary_100m_MB.dfs2** — *Internal boundary condition grid codes*


#### > Drainage (`../input/saturated/drainage/`)
- **DrainDepth_dist_500mMB.dfs2** — *Drainage level [m], Distributed*  
- **DrainTConst_dist_500mMB.dfs2** — *Drainage time constant (Leakage Coefficient) [per sec], Distributed*  
- **DK_ID15_opl_ver20_HIP500m.dfs2** — *Drain codes*  

#### > Pumping Wells (`../input/saturated/pumping_wells/`)
- **DK456_wells2022.wel** — *Well parameter file (Locations, Level, Depth, Well ID)*  
- **DK456_dkm2019_abstraction_08Jul2022.dfs0** — *Well abstraction timeseries*  

