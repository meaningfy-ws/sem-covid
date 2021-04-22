#!/usr/bin/python3

# base.py
# Date:  18/03/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

"""
This module implements reusable components and a base DAG class necessary for the ML experiments.

This is a DAG template for the generic ML MLOps level 1 described in [this article](https://cloud.google.com/solutions/machine-learning/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning).

Features:
- predefined sequence of abstract stages
- extensible/customisable implementation
- build the corresponding Airflow DAG
- easy tracking using MlFlow
- support injection of external dependencies (Airflow, MlFlow, S3 etc.)
"""
import logging
from abc import ABC, abstractmethod
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

logger = logging.getLogger(__name__)

DEFAULTS_DAG_ARGS = {
    'owner': 'Meaningfy',
    'schedule_interval': '@once',
    "start_date": datetime.now(),
    'max_active_runs': 1,
    'concurrency': 1,
    "retries": 0,
    'depends_on_past': False,
}


class BaseExperiment(ABC):
    """
     The base experiment class from which all experiments shall be derived.
    """

    def __init__(self, version: str = "0.0.1"):
        self.version = version
        self.ml_stages = [self.data_extraction, self.data_validation,
                          self.data_preparation, self.model_training,
                          self.model_evaluation, self.model_validation]

    @abstractmethod
    def data_extraction(self, *args, **kwargs):
        """
            Select and integrate the relevant data from various data sources for the ML experiment.
            Outcome: data available for processing.
        :return:
        """

    @abstractmethod
    def data_validation(self, *args, **kwargs):
        """
            Decide automatically if to (re)train the model or stop the execution of the pipeline.
            This decission is automatically done based on the following criteria:
            - Data schema skews: non compliance with the expected data schema,
                including unexpected features, missing features, unexpected feature values.
                Fix by schema update.
            - Data values skews: significant changes in the statistical properties of data,
                implying data pattern changes.
                Fix by reanalysing (EDA) of the data.
            Outcome: halting the pipeline if expectations are broken; or not.
        :return:
        """

    @abstractmethod
    def data_preparation(self, *args, **kwargs):
        """
            Prepare the data for the ML task,
            including cleaning, transformation, feature engineering and split into training, test and validation sets.
            Consider using the concept of a feature store such as 'feast' or 'hopswork'; however elasticsearch might
            be fulfilling this role
            Outcome: data splits available in the prepared format.
        :return:
        """

    @abstractmethod
    def model_training(self, *args, **kwargs):
        """
            Implement different ML algorithms to train one or multiple models,
            including hyperparameter tuning to get best performing model.
            Outcome: trained model available.
        :return:
        """

    @abstractmethod
    def model_evaluation(self, *args, **kwargs):
        """
            Evaluate the model on a (holdout) test set to measure the model quality in terms of preselected metrics.
            Outcome: metrics available to asses the model quality.
        :return:
        """

    @abstractmethod
    def model_validation(self, *args, **kwargs):
        """
            Confirm that the model is adequate for deployment based on a given baseline and store the model in a ML
            metadata repository.
            In addition (a) k-Fold Cross-Validation (k-Fold CV), (b) Leave-one-out Cross-Validation (LOOCV),
            or (c) Nested Cross-Validation may be implemented in the previous steps of model training and evaluation.
            Outcome: halt the pipeline if the model is not suitable for deployment in production, or not.
        :return:
        """

    def create_dag(self, **dag_args):
        """
            Create a standard ML DAG for the current experiment.
        :return:
        """
        updated_default_args_copy = {**DEFAULTS_DAG_ARGS.copy(), **dag_args.get('default_args', {})}
        dag_args['default_args'] = updated_default_args_copy
        dag_id = f"mlx_{self.__class__.__name__}_{self.version if self.version else '0.0.1'}"
        print(dag_id)
        dag = DAG(dag_id=dag_id, **dag_args)
        with dag:
            # instantiate a PythonOperator for each ml stage
            stage_python_operators = [PythonOperator(task_id=f"{stage.__name__}_step",
                                                     python_callable=stage,
                                                     dag=dag)
                                      for stage in self.ml_stages]
            # iterate stages in successive pairs and connect them
            for stage, successor_stage in zip(stage_python_operators, stage_python_operators[1:]):
                stage >> successor_stage
        return dag
