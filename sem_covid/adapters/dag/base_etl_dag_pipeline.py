#!/usr/bin/python3

# base_etl_dag_pipeline.py
# Date:  01/05/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

"""
    This module implements reusable components and a base DAG class necessary for the ETL pipelines.

Features:
- predefined sequence of abstract stages
- extensible/customisable implementation
- build the corresponding Airflow DAG
- easy tracking (using MlFlow or others)
- support injection of external dependencies (Airflow, MlFlow, S3 etc.)

"""

from abc import abstractmethod

from sem_covid.adapters.dag.abstract_dag_pipeline import DagPipeline


class BaseETLPipeline(DagPipeline):
    """
     The base class from which all ETL pipelines shall be derived.

     The data is
        (1) extracted item by item and stored temporarely in an object store,
        (2) transformed (structure) - e.g. XSLT/JQ etc
        (3) transformed (content) - e.g. aggregated, enriched, cleaned, etc.
        (4) loaded into final repository - e.g. a database, triple store, document management system, etc.
    """

    def get_steps(self) -> list:
        return [self.extract, self.transform_structure,
                self.transform_content, self.load]

    @abstractmethod
    def load(self, *args, **kwargs):
        """
            load data into the final store
        :return:
        """

    @abstractmethod
    def extract(self, *args, **kwargs):
        """
            Select and download the relevant data from various data sources.
            Outcome: data available for transformation in a temporary object storage.
        :return:
        """

    @abstractmethod
    def transform_structure(self, *args, **kwargs):
        """
            Access the data in the temporary store and perform a structure transformation in order to normalise
            the data representation, generally simplifying it and increasing its usability, yet maintaining
            the maximally useful structure.

            Outcome: transformed data available in the temporary object storage.
        :return:
        """

    @abstractmethod
    def transform_content(self, *args, **kwargs):
        """
            Access the data in the temporary store and perform a content transformation, which generally consists of
            text extraction, enrichment, restructuring, aggregation and other operations.

            Outcome: transformed data available in the temporary object storage.
        :return:
        """


class BaseMasterPipeline(DagPipeline):
    """
        In case the ETLs pipeline needs to be cascaded, this master pipeline provides a simple mechanism to
        select assets to be processed and then trigger subsequent pipelines to perform the processing.
    """

    def get_steps(self):
        return [self.select_assets, self.trigger_workers]

    @abstractmethod
    def select_assets(self, *args, **kwargs):
        """
            Selects a range of assets to be processed by the worker pipelines in detail.

            Outcome: select a set of asset IDs to be further processed by the worker pipelines
        :return:
        """

    @abstractmethod
    def trigger_workers(self, *args, **kwargs):
        """
            For each selected asset ID triggers an individual processing

            Outcome: a second pipeline is triggered to process each asset based on its ID
        """
