#!/usr/bin/python3

# base_etl.py
# Date:  01/05/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

"""
    This module implements reusable components and a base DAG class necessary for the ETL pipelines.

Features:
- predefined sequence of abstract stages
- extensible/customisable implementation
- build the corresponding Airflow DAG
- easy tracking using MlFlow
- support injection of external dependencies (Airflow, MlFlow, S3 etc.)

"""
import logging
from abc import ABC, abstractmethod

from airflow import DAG
from airflow.operators.python import PythonOperator

from sem_covid.services import DEFAULTS_DAG_ARGS

logger = logging.getLogger(__name__)


class BaseETL(ABC):
    """
     The base experiment class from which all ETL pipelines shall be derived.

     The data is
        (1) extracted item by item and stored temporarely in an object store,
        (2) transformed (structure) - e.g. XSLT/JQ etc
        (3) transformed (content) - e.g. aggregated, enriched, cleaned, etc.
        (4) loaded into final repository - e.g. a database, triple store, document management system, etc.
    """

    def __init__(self, version: str = "0.0.1"):
        self.version = version
        self.ml_stages = [self.extract, self.transform_structure,
                          self.transform_content, self.load]

    @abstractmethod
    def load(self, *args, **kwargs):
        """
        load data
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

    # @abstractmethod
    # def transform_content(self, *args, **kwargs):
    #     """
    #         Access the data in the temporary store and load it into a repository where it is indexed and made
    #         available for querying and full text search.
    #
    #         Outcome: transformed data available in the final repository.
    #     :return:
    #     """

    # def create_dag(self, **dag_args):
    #     """
    #         TODO: move away & delete
    #         Create a standard ML DAG for the current experiment.
    #     :return:
    #     """
    #     updated_default_args_copy = {**DEFAULTS_DAG_ARGS.copy(), **dag_args.get('default_args', {})}
    #     dag_args['default_args'] = updated_default_args_copy
    #     dag_id = f"mlx_{self.__class__.__name__}_{self.version if self.version else '0.0.1'}"
    #     print(dag_id)
    #     dag = DAG(dag_id=dag_id, **dag_args)
    #     with dag:
    #         # instantiate a PythonOperator for each ml stage
    #         stage_python_operators = [PythonOperator(task_id=f"{stage.__name__}_step",
    #                                                  python_callable=stage,
    #                                                  dag=dag,
    #                                                  )
    #                                   for stage in self.ml_stages]
    #         # iterate stages in successive pairs and connect them
    #         for stage, successor_stage in zip(stage_python_operators, stage_python_operators[1:]):
    #             stage >> successor_stage
    #     return dag
