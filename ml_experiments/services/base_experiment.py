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
from abc import ABC, abstractmethod


class BaseExperiment(object, ABC):
    """
     The base experiment class from which all experiments shall be derived.
    """

    @abstractmethod
    def data_extraction(self):
        """
            Select and integrate the relevant data from various data sources for the ML experiment.
            Outcome: data available for processing.
        :return:
        """

    @abstractmethod
    def data_validation(self):
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
    def data_preparation(self):
        """
            Prepare the data for the ML task,
            including cleaning, transformation, feature engineering and split into training, test and validation sets.
            Consider using the concept of a feature store such as 'feast' or 'hopswork'; however elasticsearch might
            be fulfilling this role
            Outcome: data splits available in the prepared format.
        :return:
        """

    @abstractmethod
    def model_training(self):
        """
            Implement different ML algorithms to train one or multiple models,
            including hyperparameter tuning to get best performing model.
            Outcome: trained model available.
        :return:
        """

    @abstractmethod
    def model_evaluation(self):
        """
            Evaluate the model on a (holdout) test set to measure the model quality in terms of preselected metrics.
            Outcome: metrics available to asses the model quality.
        :return:
        """

    @abstractmethod
    def model_validation(self):
        """
            Confirm that the model is adequate for deployment based on a given baseline and store the model in a ML
            metadata repository.
            In addition (a) k-Fold Cross-Validation (k-Fold CV), (b) Leave-one-out Cross-Validation (LOOCV),
            or (c) Nested Cross-Validation may be implemented in the previous steps of model training and evaluation.
            Outcome: halt the pipeline if the model is not suitable for deployment in production, or not.
        :return:
        """

    def create_dag(self, default_dag_args: dict = None):
        """
            Create a standard ML DAG for the current experiment.
        :return:
        """

    def build_default_args(self, kwargs):
        fixed_defaults_args = {
            'owner': 'Meaningfy',
            'schedule_interval': '@once',
            'max_active_runs': 1,
            'concurrency': 1,
            "retries": 0,
            'depends_on_past': False,
        }
