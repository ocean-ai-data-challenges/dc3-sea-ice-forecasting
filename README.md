# DC3 - Sea Ice Forecasting

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)

Data Challenge 3 (DC3) is an open benchmark for **forecasting Arctic sea ice concentration
on a seasonal time frame**. Participants submit daily sea ice concentration forecasts on a
polar stereographic grid and are evaluated against independent gridded and in-situ
observations over the Arctic winter–spring period **2020-11-01 – 2021-05-01** (181 days).

DC3 is part of the [PPR Océan & Climat](https://www.ocean-climat.fr/) (*Projet Prioritaire
de Recherche*), a national research program managed by CNRS and Ifremer.

## Challenge summary

Required predicted variable:

| CF standard name | Short name | Description |
|---|---|---|
| `sea_ice_area_fraction` | `siconc` | Sea ice concentration (fraction, 0–1) |

Expected grid (EPSG:3413 — Arctic polar stereographic):

- **x:** −3 850 000 m to +3 750 000 m, step 3 250 m (~2 338 points)
- **y:** −5 350 000 m to +5 850 000 m, step 3 250 m (~3 446 points)
- **Lead times:** 0 to 180 days (181-day seasonal forecast)

Reference datasets used during evaluation:

- **AMSR2** — gridded sea ice concentration (25 km resolution, NSIDC polar grid)
- **IABP** — drifting buoy surface temperatures (International Arctic Buoy Programme)
- **MODIS** — sea ice lead maps (Arctic)

Baseline model: **TOPAZ4** (coupled ocean–sea ice model, NERSC/Copernicus Arctic MFC).

## Installation

### Option A (recommended): Docker image

```bash
docker run -it --rm --name dc3 \
  ghcr.io/ocean-ai-data-challenges/dc3-sea-ice-forecasting:latest bash
```

JupyterLab mode:

```bash
docker run --rm -p 8888:8888 --name dc3-lab \
  ghcr.io/ocean-ai-data-challenges/dc3-sea-ice-forecasting:latest
```

Build instructions are available in `docker/README.md`.

### Option B: local environment (Conda + pip)

```bash
git clone https://github.com/ppr-ocean-ia/dc3-sea-ice-forecasting.git
cd dc3-sea-ice-forecasting

conda env create -f docker/environment.yml
conda activate dc-env

python -m pip install -U pip
python -m pip install -e .
python -m pip install "dctools @ git+https://github.com/ocean-ai-data-challenges/dc-tools.git"
```

## Usage

### Run full evaluation pipeline

```bash
python dc3/evaluate.py --model-name MyModel
```

By default, outputs are written to `dc3_output/`:

- `dc3_output/results/results_MyModel.json`
- `dc3_output/results/results_MyModel_per_bins.jsonl.gz`
- `dc3_output/results/coordinate_conformance_report.json`
- `dc3_output/logs/dc3.log`

### Key configuration knobs (`dc3/config/dc3.yaml`)

| Key | Default | Description |
|---|---|---|
| `n_days_forecast` | 181 | Seasonal forecast horizon (days) |
| `start_time` / `end_time` | 2020-11-01 / 2021-05-01 | Evaluation window |
| `per_bins_resolution` | 2 | Spatial bin size for map diagnostics (degrees) |
| `batch_size` | 32 | Number of forecast dates per batch |
| `n_parallel_workers` | 6 | Dask worker count |
| `resume` | true | Resume interrupted runs |

## Outputs

Typical generated artifacts:

- `dc3_output/results/results_<MODEL_NAME>.json` — aggregated RMSD scores
- `dc3_output/results/results_<MODEL_NAME>_per_bins.jsonl.gz` — per-bin spatial scores
- `dc3_output/results/coordinate_conformance_report.json` — grid validation report
- `dc3_output/logs/dc3.log` — run log

## Documentation

Build locally:

```bash
pip install sphinx sphinx-rtd-theme myst-parser
sphinx-build -b html docs/source docs/build/html
```

## Project structure

```text
dc3/
  config/         # YAML configuration profiles
  evaluation/     # DC3Evaluation class
  evaluate.py     # CLI entry point
docs/             # Sphinx documentation
docker/           # Dockerfile and conda environment
notebooks/        # Example notebooks
```

## License

GPL-3.0. See `LICENSE`.

