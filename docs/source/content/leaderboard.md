# Leaderboard

The DC3 leaderboard ranks submitted sea ice forecasting models by their RMSD score against
the AMSR2 sea ice concentration reference over the Arctic winter–spring season
(2020-11-01 – 2021-05-01).

The leaderboard is updated as new submissions are processed. The interactive leaderboard
and spatial map visualizations are available at the project documentation site.

## Baseline

The reference score is provided by **TOPAZ4**, the operational coupled ocean–sea ice model
from NERSC/Copernicus Arctic MFC. All submitted models are compared against this baseline.

## How to appear on the leaderboard

1. Run the full evaluation pipeline (see {doc}`submissions`).
2. Share your `results_<MODEL_NAME>.json` file with the challenge organizers.
3. Provide a brief model description, training data summary, and an optional URL
   (paper or repository).

Open an issue in the
[DC3 repository](https://github.com/ppr-ocean-ia/dc3-sea-ice-forecasting) to submit
your results.
