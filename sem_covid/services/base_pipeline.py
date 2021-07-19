#!/usr/bin/python3

# base_pipeline.py
# Date:  19/05/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

"""
    This module implements a pipeline skeleton that latter
    on can be materialised as Airflow DAG or any other type of workflow.

    ----
    TODO: revise this
    Old documentation
    ----
    This module implements reusable components and a base DAG class necessary for the ETL pipelines.

    Features:
    - predefined sequence of abstract stages
    - extensible/customisable implementation
    - build the corresponding Airflow DAG (externalised into a factory method)
    - easy tracking using MlFlow ()
    - support injection of external dependencies (Airflow, MlFlow, S3 etc.)
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Any

logger = logging.getLogger(__name__)


class BasePipeline(ABC):
    """
        The base pipeline class from which all pipelines shall be derived.

        Simply define and implement as methods functions that represent steps in the pipeline and
        then chain them in a property called
    """

    @property
    @abstractmethod
    def pipeline_stages(self) -> List[Any]:
        """
            Returns the stages of the pipeline that are methods defined and implemented by __THIS__ class.
        :return: array of class methods
        """

    @property
    def version(self) -> str:
        return "0.0.1"


class BaseExperiment(BasePipeline):
    """
     The base experiment class from which all experiments shall be derived.
    """

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

    def pipeline_stages(self) -> List[Any]:
        return [self.data_extraction,
                self.data_validation,
                self.data_preparation,
                self.model_training,
                self.model_evaluation,
                self.model_validation]
