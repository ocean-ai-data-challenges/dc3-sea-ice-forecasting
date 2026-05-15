# Task description

## Overview

Data Challenge 3 (DC3) is an open benchmark for **forecasting Arctic sea ice concentration
on a seasonal time frame**. Participants train a forecasting model and submit daily
sea ice concentration (SIC) fields on a polar stereographic grid. Predictions are evaluated
against independent gridded and in-situ Arctic observations covering the period
**2020-11-01 – 2021-05-01** (181 days, covering Arctic winter through spring melt onset).

The fundamental goal of DC3 is to assess whether data-driven models can faithfully reproduce
the evolution of Arctic sea ice concentration throughout an entire seasonal cycle, from freeze-up
to melt onset, using only surface-level fields.

DC3 is part of the [PPR Océan & Climat](https://www.ocean-climat.fr/) (*Projet Prioritaire
de Recherche*), a national research program launched by the French government and managed
by CNRS and Ifremer to improve understanding of the ocean and climate.

## Goal

Given any set of input data (e.g. reanalysis fields, satellite observations, atmospheric
forcings), produce daily Arctic sea ice concentration fields for a **181-day seasonal
forecast** starting from an initialization date in autumn. The single physical variable
to predict is:

| CF standard name | Short name | Description |
|---|---|---|
| `sea_ice_area_fraction` | `siconc` | Sea ice concentration (dimensionless, 0–1) |

The prediction field has dimensions `(time, x, y)` on the EPSG:3413 polar stereographic
grid.

## Evaluation setup

A single forecast covers **181 days** of lead time (one full Arctic season). The evaluation
pipeline:

1. Reads or downloads the submitted seasonal forecast.
2. Interpolates predicted SIC fields to the space-time locations of each reference dataset.
3. Computes RMSD between the interpolated prediction and observations.
4. Aggregates scores per variable and lead time and publishes them on the
   [leaderboard](leaderboard.md).

## Spatial domain

The target grid covers the Arctic Ocean on a **polar stereographic projection (EPSG:3413)**:

| Dimension | Range | Step | Approx. points |
|---|---|---|---|
| **x** | −3 850 000 m to +3 750 000 m | 3 250 m | ~2 338 |
| **y** | −5 350 000 m to +5 850 000 m | 3 250 m | ~3 446 |

This is consistent with the NSIDC 3.125 km polar stereographic grid used by AMSR2
sea ice products. The coordinate reference system (EPSG:3413) has its origin at the
North Pole with the standard parallel at 70°N.

## Reference model — TOPAZ4

The baseline against which all submissions are compared is **TOPAZ4** (*Towards an
Operational Prediction system for the North Atlantic European coastal Zones*), a
coupled ocean–sea ice model run operationally by NERSC and distributed through the
Copernicus Arctic Monitoring and Forecasting Centre (ARC MFC). TOPAZ4 produces daily
Arctic forecasts at ~12.5 km resolution; its `siconc` output serves as the benchmark
score on the leaderboard.
