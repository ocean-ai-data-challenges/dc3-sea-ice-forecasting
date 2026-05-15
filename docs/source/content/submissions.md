# Submissions

This page describes accepted input formats and how to run DC3 evaluation.

## CLI entry point

The evaluation is launched directly from the repository script:

```bash
python dc3/evaluate.py --model-name <MODEL_NAME>
```

## Required content

DC3 evaluates a single variable:

- `siconc` — sea ice area fraction (dimensionless, 0–1)

Expected target grid (EPSG:3413 — Arctic polar stereographic):

| Dimension | Range | Step |
|---|---|---|
| x | −3 850 000 m to +3 750 000 m | 3 250 m |
| y | −5 350 000 m to +5 850 000 m | 3 250 m |
| lead times | 0 to 180 days | 1 day |

The submission must also provide auxiliary 2-D `lat`/`lon` arrays (or `latitude`/`longitude`)
so the pipeline can map polar-grid cells to geographic coordinates for per-bin diagnostics.

## Accepted data layouts

The evaluation pipeline accepts any format supported by `xarray.open_dataset` / `xarray.open_zarr`:

1. **Single Zarr store** — one store covering the full 181-day period
2. **Single NetCDF file** (`.nc` or `.nc4`)
3. **Directory of per-date files** — one Zarr or NetCDF per initialization date
4. **Glob pattern** — e.g. `/data/my_model/*.zarr`

Recommended layout (one Zarr store per year):

```text
my_model/
  2020.zarr
```

or one store covering the full seasonal window:

```text
my_model/
  siconc_2020-11-01_2021-05-01.zarr
```

## Configure the evaluation

Edit `dc3/config/dc3.yaml` to point to your model output:

```yaml
# dataset_references maps model names to their reference datasets
dataset_references:
  <MODEL_NAME>:
    - amsr2
    - iabp
    - modis
```

Key parameters to configure before running:

| Key | Default | Description |
|---|---|---|
| `start_time` | 2020-11-01 | Start of evaluation window |
| `end_time` | 2021-05-01 | End of evaluation window |
| `n_days_forecast` | 181 | Forecast horizon (days) |
| `batch_size` | 32 | Dates processed per batch |
| `n_parallel_workers` | 6 | Dask worker count |
| `per_bins_resolution` | 2 | Spatial bin resolution (degrees) |

## Run

```bash
python dc3/evaluate.py --model-name <MODEL_NAME>
```

Outputs are written by default to `dc3_output/`:

- `dc3_output/results/results_<MODEL_NAME>.json`
- `dc3_output/results/results_<MODEL_NAME>_per_bins.jsonl.gz`
- `dc3_output/results/coordinate_conformance_report.json`
- `dc3_output/logs/dc3.log`

## Typical output files

- `results_<MODEL_NAME>.json` — aggregated RMSD scores per dataset, variable, and lead time
- `results_<MODEL_NAME>_per_bins.jsonl.gz` — per-bin spatial breakdown for map generation
- `coordinate_conformance_report.json` — grid validation report

## Leaderboard submission process

To appear on the official leaderboard, share at least:

1. `results_<MODEL_NAME>.json`
2. Model description and training data summary
3. Paper or repository URL (if available)

For questions, open an issue in the
[project repository](https://github.com/ppr-ocean-ia/dc3-sea-ice-forecasting).
