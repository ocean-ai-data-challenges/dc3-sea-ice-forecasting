#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""Evaluator class."""

from argparse import Namespace
import os

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

    def filter_data(
        self,
        manager: MultiSourceDatasetManager,
        filter_region: gpd.GeoSeries,        
    ) -> MultiSourceDatasetManager:
        
        manager.filter_all_by_date(
            start=pd.to_datetime(self.args.start_times),
            end=pd.to_datetime(self.args.end_times),
        )

        manager.filter_all_by_region(
            region=filter_region
        )

        return manager

    def setup_transforms(
        self,
        manager: MultiSourceDatasetManager,
        aliases: list[str],
    ) -> dict[str, CustomTransforms]:
        transforms_dict = {}
        if "iabp" in aliases:
            transforms_dict["iabp"] = manager.get_transform(
                "to_epsg3413",
                dataset_alias="iabp",
            )
        pass

    def check_dataloader(
        self,
        dataloader: EvaluationDataloader,
    ) -> None:
        # TODO
        pass

    def setup_dataset_manager(self) -> MultiSourceDatasetManager:
        # TODO
        manager = MultiSourceDatasetManager()
        datasets = {}

        for source in self.args.sources:
            source_name = source['dataset']
            if source_name not in ["modis", "amsr2", "iabp"]:
                logger.warning(f"Dataset {source_name} is not supported yet, skipping.")
                continue
            kwargs = {}
            kwargs["source"] = source
            kwargs["root_data_folder"] = self.args.data_directory
            kwargs["root_catalog_folder"] = self.args.catalog_dir
            logger.debug(f"\n\nSetup dataset {source_name}\n\n")
            datasets[source_name] = get_dataset_from_config(
                **kwargs
            )
            # Add dataset with its alias
            manager.add_dataset(source_name, datasets[source_name])

            # Build catalog
            logger.debug(f"Build catalog")
            manager.build_catalogs()
            manager.all_to_json(output_dir=self.args.catalog_dir)
            manager = self.filter_data(manager, filter_region)
            return manager
        
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
        
    def run_eval(self) -> None:
        """Proceed to evaluation."""
        dataset_manager = self.setup_dataset_manager()
        aliases = dataset_manager.datasets.keys()
        dask_cluster = setup_dask(self.args)
        
        dataloaders = {}
        metrics_names = {}
        metrics = {}
        evaluators = {}
        models_results = {}
        transforms_dict = self.setup_transforms(dataset_manager, aliases)

        for alias in dataset_manager.datasets.keys():
            logger.debug(f"\n\n\nGet dataloader for {alias}")
            logger.debug(f"Transform: {transforms_dict.get(alias)}\n\n\n")
            pred_transform = transforms_dict.get(alias)
            if alias in ["modis", "amsr2", "iabp"]:
                ref_transform = transforms_dict.get(alias)
                ref_alias=alias
            else:
                ref_transform = None
                ref_alias=None
            dataloaders[alias] = dataset_manager.get_dataloader(
                pred_alias=alias,
                ref_alias=ref_alias,
                batch_size=self.args.batch_size,
                pred_transform=pred_transform,
                ref_transform=ref_transform,
            )

            self.check_dataloader(dataloaders[alias])

        # Calculate metrics
        for alias in dataset_manager.datasets.keys():
            # TODO: Add Class 4 metrics once they're available
                # Forecast accuracy metrics
                # Physical realism metrics
                # User-oriented metrics
                # Computational efficiency metrics
            metrics_names[alias] = [
                "rmsd",
            ]
            metrics_kwargs = {}
            metrics_kwargs[alias] = {"add_noise": False,
                "eval_variables": dataloaders[alias].eval_variables,
            }
            metrics[alias] = [
                MetricComputer(metric_name=metric, **metrics_kwargs[alias])
                for metric in metrics_names[alias]
            ]

            evaluators[alias] = Evaluator(
                dask_cluster=dask_cluster,
                metrics=metrics[alias],
                dataloader=dataloaders[alias],
                json_path=os.path.join(self.args.catalog_dir, f"test_results_{alias}.json"),
            )

            models_results[alias] = evaluators[alias].evaluate()


        # Vérifier que chaque résultat contient les champs attendus, afficher
        for dataset_alias, results in models_results.items():
            # Vérifier que les résultats existent
            assert len(results) > 0
            logger.info(f"\n\n\nResults for {dataset_alias}:")
            for result in results:
                assert "date" in result
                assert "metric" in result
                assert "result" in result
                logger.info(f"Test Result: {result}")
