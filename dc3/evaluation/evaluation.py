#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""Evaluator class."""

from argparse import Namespace

import geopandas as gpd
from loguru import logger
import pandas as pd
from shapely import geometry

from dctools.data.datasets.dataset import get_dataset_from_config
from dctools.data.datasets.dataloader import EvaluationDataloader
from dctools.data.datasets.dataset_manager import MultiSourceDatasetManager

from dctools.data.transforms import CustomTransforms
from dctools.metrics.evaluator import Evaluator
from dctools.metrics.metrics import MetricComputer
from dctools.utilities.init_dask import setup_dask
from dctools.utilities.xarray_utils import DICT_RENAME_CMEMS,\
    LIST_VARS_GLONET


class DC3Evaluation:
    """Class to evaluate models."""

    def __init__(self, arguments: Namespace) -> None:
        """Init class.

        Args:
            aruguments (str): Namespace with config.
        """
        self.args = arguments

    def setup_dataset_manager(self) -> MultiSourceDatasetManager:
        # TODO

        for source in self.args.sources:
            source_name = source['dataset']
            dataset = get_dataset_from_config(
                    source,
                    self.args.data_directory,
                    self.args.catalog_dir,
                    self.args.max_samples,
                )
        
        match source_name:
            case "modis":
                modis_dataset = dataset
            case "amsr2":
                amsr2_dataset = dataset
            case "iabp":
                iabp_dataset = dataset
        
        """
        Coordinate systems (CRS):

        MODIS   EPSG:3413 (Arctic)  EPSG:3412 (Antarctic)   1.0km
        AMSR2   EPSG:3413 (Arctic)  EPSG:3412 (Antarctic)   3.125km
        """

        """
        x range from -3850 to 3750 (km)
        y range from -5350 to 5850 (km)
        """

        filter_region = gpd.GeoSeries(geometry.Polygon((
            (self.args.min_x,self.args.min_y),
            (self.args.min_x,self.args.max_y),
            (self.args.max_x,self.args.min_y),
            (self.args.max_x,self.args.max_y),
            (self.args.min_x,self.args.min_y),
            )), crs="EPSG:3413")
        


    def setup_transforms() -> dict[str, CustomTransforms]:
        # TODO: Convert IABP points to polar grid
        pass

    def check_dataloader() -> None:
        # TODO
        pass

    def run_eval(self) -> None:
        """Proceed to evaluation."""
        dataset_manager = self.setup_dataset_manager()
        dask_cluster = setup_dask(self.args)
        
        transforms = self.setup_transforms()

        dataloader = dataset_manager.get_dataloader(
            # TODO: set this up
            pred_alias="PLACEHOLDER",
            ref_alias="PLACEHOLDER",
            batch_size=self.args.batch_size,
            pred_transform=None,
            ref_transform=None,
            )

        self.check_dataloader(dataloader)

        # Forecast accuracy metrics
        accuracy_metrics = [
            MetricComputer(
                metric_name='rmse',
            ),
        ]

        # Physical realism metrics
        # TODO

        # User-oriented metrics
        # TODO

        # Computational efficiency metrics
        # TODO

        accuracy_evaluator = Evaluator(
            dask_cluster=dask_cluster,
            metrics=accuracy_metrics,
            dataloader=dataloader,
        )

        accuracy_results = accuracy_evaluator.evaluate()

        # Check that results exist
        assert len(accuracy_results) > 0

        # Check that all expected fields are in results
        for result in accuracy_results:
            assert "date" in result
            assert "metric" in result
            assert "result" in result
        logger.info(f"Test Results: {accuracy_results}")

