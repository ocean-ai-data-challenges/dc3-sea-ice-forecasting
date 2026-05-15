# Quickstart

This page gets you from installation to a first evaluation run.

## 1. Install

Choose one option.

### Option A: Docker (recommended)

```bash
docker run -it --rm --name dc3 \
    ghcr.io/ocean-ai-data-challenges/dc3-sea-ice-forecasting:latest bash
```

JupyterLab mode:

```bash
docker run --rm -p 8888:8888 --name dc3-lab \
    ghcr.io/ocean-ai-data-challenges/dc3-sea-ice-forecasting:latest
```

### Option B: local Conda + pip

```bash
git clone https://github.com/ppr-ocean-ia/dc3-sea-ice-forecasting.git
cd dc3-sea-ice-forecasting

conda env create -f docker/environment.yml
conda activate dc-env

python -m pip install -U pip
python -m pip install -e .
python -m pip install "dctools @ git+https://github.com/ocean-ai-data-challenges/dc-tools.git"
```

## 2. Prepare model outputs

Your model must output daily **sea ice concentration** (`siconc`) fields on the EPSG:3413
Arctic polar stereographic grid for the evaluation period.

Recommended layout (single Zarr store):

```text
my_model/
    siconc_2020-2021.zarr    # dimensions: (time=181, x=~2338, y=~3446)
```

Include auxiliary 2-D `lat`/`lon` variables for spatial diagnostics:

```python
import xarray as xr
import numpy as np

ds = xr.Dataset(
    {"siconc": (["time", "x", "y"], my_data)},
    coords={
        "time": pd.date_range("2020-11-01", periods=181, freq="1D"),
        "x": x_coords,      # 1-D array in metres
        "y": y_coords,      # 1-D array in metres
        "lat": (["x", "y"], lat_2d),   # 2-D geographic lat
        "lon": (["x", "y"], lon_2d),   # 2-D geographic lon
    },
)
ds.to_zarr("my_model/siconc_2020-2021.zarr")
```

## 3. Configure the evaluation

Edit `dc3/config/dc3.yaml` to add your model under `dataset_references`:

```yaml
dataset_references:
  my_model:        # must match --model-name
    - amsr2
```

Set the path to your model data under the `sources` section or pass it via the CLI.

## 4. Run full pipeline

```bash
python dc3/evaluate.py --model-name my_model
```

This command runs evaluation and writes results to `dc3_output/results/`.

## 5. Inspect results

```bash
python -c "import json; print(json.dumps(json.load(open('dc3_output/results/results_my_model.json')), indent=2))"
```

## Next pages

- {doc}`submissions`
- {doc}`evaluation`
- {doc}`metrics`
- {doc}`data`
