# Data

## Training data

DC3 does not prescribe a fixed training dataset. Participants can use reanalyses,
satellite observations, model outputs (e.g. TOPAZ4, PIOMAS, ERA5), and their own
preprocessing pipelines. Any data available before the evaluation period
(**2020-11-01**) may be used for training.

## Evaluation references

The DC3 evaluation pipeline evaluates submissions against three independent reference
datasets:

### AMSR2 — Gridded sea ice concentration

The primary reference for `siconc` evaluation.
AMSR2 (Advanced Microwave Scanning Radiometer 2) provides daily gridded sea ice
concentration at **3.125 km resolution** on the NSIDC polar stereographic grid
(EPSG:3413), produced by the University of Bremen using the ASI algorithm (v5.4).

- **Coverage:** Full Arctic basin, daily
- **Evaluated variable:** `z` (SIC fraction, 0–1)
- **Source:** Wasabi S3 bucket `ppr-ocean-climat / DC3/AMSR2_1D-time`
- **File pattern:** `[YYYY]/asi-AMSR2-n3125-[YYMMDD]-v5.4.zarr`

### IABP — International Arctic Buoy Programme

In-situ drifting buoy observations providing surface temperature and position tracks
across the Arctic.

- **Coverage:** Scattered point observations across the Arctic basin
- **Evaluated variable:** `Ts` (surface temperature, °C)
- **Additional variables kept:** `BP` (barometric pressure), `Ta` (air temperature at 1m),
  `Th` (hull temperature)
- **Source:** Wasabi S3 bucket `ppr-ocean-climat / DC3/IABP`
- **File pattern:** `LEVEL1_[YYYY].zarr`

### MODIS — Sea ice lead maps

MODIS (Moderate Resolution Imaging Spectroradiometer) lead maps derived from thermal
infrared imagery, providing information on open water fraction within sea ice.

- **Coverage:** Arctic basin (cloud-permitting), daily composite
- **Evaluated variable:** `leadmap` (fractional lead coverage)
- **Source:** Wasabi S3 bucket `ppr-ocean-climat / DC3/MODIS`
- **File pattern:** `[YYYY][YY+1]_ArcLeads.zarr`

## Evaluation period

- **Start:** 2020-11-01
- **End:** 2021-05-01
- **Duration:** 181 days (one full Arctic winter–spring season)

## Coordinate system

All DC3 spatial fields use the **EPSG:3413** Arctic polar stereographic projection.
Coordinates `x` and `y` are in metres. Auxiliary `lat`/`lon` variables in 2-D are
provided alongside the projected coordinates for geographic reference.

## Where dataset definitions live

Dataset sources and metric assignments are defined in:

- `dc3/config/dc3.yaml`

This file contains:

- S3 connection settings (Wasabi endpoints, bucket, folder)
- per-dataset `keep_variables` and `eval_variables`
- time-matching tolerances (`time_tolerance: 12` hours)
- metric lists (currently `rmsd`)

## Practical note

The evaluation pipeline fetches and caches reference data from S3 as needed. A local
catalog cache is maintained under `dc3_output/catalogs/`. No manual download of
reference data is required before running evaluation.
