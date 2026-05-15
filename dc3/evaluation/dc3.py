#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""DC3 evaluation class - challenge-specific wiring only."""

from __future__ import annotations

from argparse import Namespace
from pathlib import Path
from typing import Any, Dict

import geopandas as gpd
import numpy as np
import pandas as pd
import yaml
from loguru import logger
from shapely import geometry

from dctools.data.coordinates import get_target_dimensions
from dctools.data.datasets.dataset import get_dataset_from_config
from dctools.data.datasets.dataset_manager import MultiSourceDatasetManager
from dctools.processing.base import BaseDCEvaluation


def _default_dc3_target_dimensions() -> Dict[str, np.ndarray]:
    """Return default DC3 polar grid if no target_dimensions is defined in YAML."""
    return {
        "x": np.arange(-3850000, 3750000, 3250),
        "y": np.arange(-5350000, 5850000, 3250),
    }


def _promote_latlon_coords(ds: Any) -> Any:
    """Promote lat/lon variables to xarray coordinates for per-bins support.

    The per-bins spatial RMSD computation in dctools looks for ``lat``/``lon``
    in ``ds.coords``.  DC3 polar datasets store them as data variables (AMSR2:
    ``lat``/``lon``) or use alternative names (TOPAZ: ``latitude``/``longitude``
    which are already coords).  This helper:

    1. Sets ``lat`` and ``lon`` as coordinates if they are data variables.
    2. Creates ``lat``/``lon`` aliases when only ``latitude``/``longitude``
       coordinates exist (TOPAZ case).
    """
    import xarray as xr

    if not isinstance(ds, xr.Dataset):
        return ds

    # 1. Promote lat/lon data variables to coordinates.
    promote = [v for v in ("lat", "lon") if v in ds.data_vars]
    if promote:
        ds = ds.set_coords(promote)

    # 2. Alias latitude/longitude → lat/lon if only the long names exist.
    for long_name, short_name in (("latitude", "lat"), ("longitude", "lon")):
        if long_name in ds.coords and short_name not in ds.coords:
            ds = ds.assign_coords({short_name: ds[long_name]})

    return ds


def _wrap_with_latlon_promotion(transform: Any) -> Any:
    """Wrap a transform callable to also promote lat/lon after it runs."""
    if transform is None:
        return _promote_latlon_coords

    def _wrapped(ds: Any) -> Any:
        ds = transform(ds)
        return _promote_latlon_coords(ds)

    return _wrapped


class DC3Evaluation(BaseDCEvaluation):
    """Class that manages evaluation of Data Challenge 3."""

    CHALLENGE_NAME = "DC3"

    def __init__(self, arguments: Namespace) -> None:
        super().__init__(arguments)

        # Load leaderboard display config — path injected by evaluate.py into args
        # (falls back to the YAML key from the DC config file if present).
        _lb_config_path = getattr(arguments, "leaderboard_config", None)
        if _lb_config_path:
            _lb_yaml = Path(_lb_config_path)
            if not _lb_yaml.is_absolute():
                _lb_yaml = Path.cwd() / _lb_yaml
            if _lb_yaml.is_file():
                try:
                    self.leaderboard_custom_config = (
                        yaml.safe_load(_lb_yaml.read_text(encoding="utf-8")) or {}
                    )
                except Exception:  # noqa: BLE001
                    pass  # leave self.leaderboard_custom_config as None (base default)

        # Use YAML-defined target_dimensions when available, otherwise use the
        # canonical DC3 polar grid.
        self.target_dimensions = get_target_dimensions(self.args) or _default_dc3_target_dimensions()

        # Use dataset_references from YAML config when provided.
        config_refs = getattr(self.args, "dataset_references", None)
        if isinstance(config_refs, dict) and config_refs:
            self.dataset_references = config_refs
        else:
            self.dataset_references = {
                "topaz": ["amsr2"],
            }

        self.all_datasets = list(
            set(
                list(self.dataset_references.keys())
                + [item for sublist in self.dataset_references.values() for item in sublist]
            )
        )

        self._init_cluster()

    def filter_data(
        self,
        manager: MultiSourceDatasetManager,
        filter_region: gpd.GeoSeries,
    ) -> MultiSourceDatasetManager:
        """Filter by date only.

        Spatial bounds are already applied per-dataset through the
        ``filter_values`` dict (``min_x/max_x/min_y/max_y``) passed to
        ``get_dataset_from_config`` in :meth:`setup_dataset_manager`.
        Calling ``filter_all_by_region`` here with a EPSG:3413 polygon fails
        for datasets stored in EPSG:4326 (e.g. TOPAZ), so we skip it.
        """
        manager.filter_all_by_date(
            start=pd.to_datetime(self.args.start_time),
            end=pd.to_datetime(self.args.end_time),
        )
        return manager

    def setup_transforms(
        self,
        dataset_manager: MultiSourceDatasetManager,
        aliases: list[str],
    ) -> dict[str, Any]:
        """Configure DC3-specific transforms for polar datasets.

        Each transform is wrapped with :func:`_wrap_with_latlon_promotion` so
        that ``lat``/``lon`` are always promoted to xarray coordinates before
        the per-bins spatial RMSD is computed.
        """
        transforms_dict: dict[str, Any] = {}
        if "iabp" in aliases:
            transforms_dict["iabp"] = _wrap_with_latlon_promotion(
                dataset_manager.get_transform("to_epsg3413", dataset_alias="iabp")
            )
        if "amsr2" in aliases:
            transforms_dict["amsr2"] = _wrap_with_latlon_promotion(
                dataset_manager.get_transform("standardize", dataset_alias="amsr2")
            )
        # Apply lat/lon promotion to any other dataset (e.g. topaz) that has
        # no other transform but may need coordinate normalisation.
        for alias in aliases:
            if alias not in transforms_dict:
                transforms_dict[alias] = _wrap_with_latlon_promotion(None)
        return transforms_dict

    def setup_dataset_manager(self, list_all_references: list[str]) -> MultiSourceDatasetManager:
        """Build a dataset manager adapted to DC3 polar x/y coordinates."""
        manager = MultiSourceDatasetManager(
            dataset_processor=self.dataset_processor,
            target_dimensions=self.target_dimensions,
            time_tolerance=pd.Timedelta(hours=self.args.delta_time),
            list_references=list_all_references,
            max_cache_files=self.args.max_cache_files,
        )

        datasets: dict[str, Any] = {}
        for source in sorted(self.args.sources, key=lambda x: x["dataset"]):
            source_name = source["dataset"]

            if source_name not in self.all_datasets:
                logger.warning(f"Dataset {source_name} is not used for the evaluation, skipping.")
                continue

            kwargs: dict[str, Any] = {
                "source": source,
                "root_data_folder": self.args.data_directory,
                "root_catalog_folder": self.args.catalog_dir,
                "dataset_processor": self.dataset_processor,
                "max_samples": self.args.max_samples,
                "file_cache": manager.file_cache,
                "filter_values": {
                    "start_time": self.args.start_time,
                    "end_time": self.args.end_time,
                    "min_x": self.args.min_x,
                    "max_x": self.args.max_x,
                    "min_y": self.args.min_y,
                    "max_y": self.args.max_y,
                },
            }

            datasets[source_name] = get_dataset_from_config(**kwargs)
            manager.add_dataset(source_name, datasets[source_name])

        filter_region = gpd.GeoSeries(
            [
                geometry.Polygon(
                    (
                        (self.args.min_x, self.args.min_y),
                        (self.args.min_x, self.args.max_y),
                        (self.args.max_x, self.args.max_y),
                        (self.args.max_x, self.args.min_y),
                        (self.args.min_x, self.args.min_y),
                    )
                )
            ],
            crs="EPSG:3413",
        )
        manager = self.filter_data(manager, filter_region)

        # DC3 zarr files are single-day snapshots: date_end == date_start.
        # build_forecast_index_from_catalog requires date_end >= valid_time + 1 day,
        # so we set date_end = date_start + 1 day for all single-day catalog entries.
        import pandas as _pd

        for _alias, _dataset in manager.datasets.items():
            _catalog = _dataset.get_catalog()
            if _catalog is None:
                continue
            _gdf = _catalog.get_dataframe()
            _mask = _gdf["date_end"] == _gdf["date_start"]
            if _mask.any():
                _gdf = _gdf.copy()
                _gdf.loc[_mask, "date_end"] = (
                    _gdf.loc[_mask, "date_start"] + _pd.Timedelta(days=1)
                )
                _catalog.set_dataframe(_gdf)

        return manager


