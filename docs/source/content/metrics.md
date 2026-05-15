# Metrics

Metrics are computed by `dctools` during evaluation and aggregated in the result JSON files.

## Core metric

The main score is RMSD (Root Mean Square Deviation):

$$
\mathrm{RMSD} = \sqrt{\frac{1}{N}\sum_{i=1}^{N} (\hat{x}_i - x_i)^2}
$$

where $\hat{x}_i$ is the model value interpolated at the reference location/time and $x_i$
is the reference observation value. Lower RMSD indicates better agreement.

## Metrics per dataset

| Reference | Variable | Metric |
|---|---|---|
| AMSR2 (gridded SIC) | `z` (sea ice concentration) | `rmsd` |
| IABP (buoy surface temperature) | `Ts` | `rmsd` |
| MODIS (lead maps) | `leadmap` | `rmsd` |

## Spatial per-bin outputs

When enabled, the pipeline exports per-bin metric summaries at `per_bins_resolution` (2°
by default). Each bin aggregates all observations falling within a 2°×2° lat/lon cell.
This allows spatial diagnostics and map visualisation of where models perform well or
poorly across the Arctic.

## RMSD for gridded (AMSR2) vs. in-situ (IABP) references

- **AMSR2** is a gridded product on the same EPSG:3413 polar grid as the model output.
  The evaluation performs a nearest-neighbour remap to the AMSR2 grid before computing RMSD.
- **IABP** provides scattered point observations. The model is interpolated to each buoy
  location and time before computing RMSD against the measured surface temperature.

## Practical interpretation

- Compare scores by lead time to assess how quickly model skill degrades over the
  181-day forecast horizon.
- AMSR2 RMSD is the primary leaderboard score for sea ice concentration.
- Validate stability across all three references (AMSR2, IABP, MODIS) for a comprehensive
  assessment of model performance.
