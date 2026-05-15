# Evaluation

This page describes what happens when you run DC3 evaluation and which configuration knobs
matter in practice.

## Run command

```bash
python dc3/evaluate.py --model-name <MODEL_NAME>
```

`evaluate.py` writes logs and outputs under `dc3_output/` by default.

## Main pipeline stages

1. Read submission files and normalise coordinates/variable names.
2. Promote `lat`/`lon` arrays to xarray coordinates for spatial indexing.
3. Fetch and prepare reference datasets (AMSR2, IABP, MODIS) according to `dc3.yaml`.
4. Interpolate predictions to the reference support (grid or point locations) and compute
   configured metrics.
5. Write consolidated outputs under the chosen data directory.

## Default outputs

Typical files produced in `dc3_output/results/`:

- `results_<MODEL_NAME>.json`
- `results_<MODEL_NAME>_per_bins.jsonl.gz` (when per-bin output is enabled)
- `coordinate_conformance_report.json`

Logs are written in `dc3_output/logs/dc3.log`.

## Configuration profile

DC3 ships a single YAML profile at `dc3/config/dc3.yaml`.

Important keys to tune:

| Key | Default | Description |
|---|---|---|
| `batch_size` | 32 | Dates processed per Dask batch |
| `n_parallel_workers` | 6 | Dask distributed worker count |
| `nthreads_per_worker` | 4 | Threads per Dask worker |
| `memory_limit_per_worker` | 4GB | Memory cap per worker |
| `restart_workers_per_batch` | — | Restart workers between batches (memory safety) |
| `cleanup_between_batches` | — | Free caches between batches |
| `resume` | true | Skip already-computed dates |
| `per_bins_resolution` | 2 | Degree bin size for spatial map output |

## Coordinate handling

DC3 uses an Arctic polar stereographic projection (EPSG:3413). The evaluation pipeline:

- Detects `x`/`y` as the spatial target dimensions (in metres).
- Expects auxiliary 2-D `lat`/`lon` arrays (or `latitude`/`longitude`) for geographic
  per-bin aggregation.
- Automatically promotes `lat`/`lon` data variables to xarray coordinates if needed.

## Temporal setup

- Evaluation window: **2020-11-01 to 2021-05-01**
- Forecast horizon: **181 lead times** (0..180 days)
- Time-matching tolerance: **12 hours** (for all reference datasets)

## Practical guidance

- Keep `resume: true` for long seasonal runs so interrupted jobs can be restarted safely.
- Adjust `n_parallel_workers` and `memory_limit_per_worker` to fit your machine.
- Start with a reduced `end_time` (e.g. `2020-12-01`) when benchmarking a new model or
  environment.
- The AMSR2 reference is the largest dataset; allow extra memory for those batches.
