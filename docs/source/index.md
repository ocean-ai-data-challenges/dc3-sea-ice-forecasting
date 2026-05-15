# DC3: Arctic Sea Ice Forecasting

DC3 is an open benchmark for **forecasting Arctic sea ice concentration on a seasonal time
frame**. Participants submit daily sea ice concentration fields on a polar stereographic grid
and are evaluated against independent gridded and in-situ Arctic observations.

Challenge period: **2020-11-01 to 2021-05-01** (181-day seasonal window).

Required variable:

- `siconc` (sea ice area fraction, dimensionless, 0–1)

Grid: EPSG:3413 Arctic polar stereographic, ~3.25 km spacing.

::::{grid} 2
:::{grid-item-card} Scientific context
:link: content/task
:link-type: doc

Task definition, target variable, evaluation schedule, baseline model.
:::

:::{grid-item-card} Data
:link: content/data
:link-type: doc

Reference datasets (AMSR2, IABP, MODIS) and practical data notes.
:::

:::{grid-item-card} Metrics
:link: content/metrics
:link-type: doc

RMSD-based metrics used by the evaluation pipeline.
:::

:::{grid-item-card} Submissions
:link: content/submissions
:link-type: doc

Input layouts, configuration, and run commands.
:::
::::

## Quick start

```bash
# 1) Clone and install
git clone https://github.com/ppr-ocean-ia/dc3-sea-ice-forecasting.git
cd dc3-sea-ice-forecasting
conda env create -f docker/environment.yml
conda activate dc-env
python -m pip install -e .
python -m pip install "dctools @ git+https://github.com/ocean-ai-data-challenges/dc-tools.git"

# 2) Run evaluation
python dc3/evaluate.py --model-name MyModel
```

For Docker and full options, see {doc}`content/quickstart`.

```{toctree}
:maxdepth: 2
:caption: Getting started

content/quickstart.md
content/evaluation.md
content/submissions.md
```

```{toctree}
:maxdepth: 2
:caption: DC3 Challenge

content/task.md
content/data.md
content/metrics.md
content/leaderboard.md
content/references.md
```

