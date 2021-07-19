# -*- coding: utf-8 -*-
# Date    : 19.07.2021 
# Author  : Stratulat Ștefan
# File    : classifiers_pipeline_dag.py
# Software: PyCharm
from sem_covid.adapters.dag.abstract_dag_pipeline import DagPipeline
from sem_covid.services.ml_pipelines.pwdb_classifiers_pipeline import FeatureEngineering, ModelTraining


class ClassifiersPipelineDag(DagPipeline):
    """
           This class aims to unify the feature engineering pipeline and the model training pipeline.
    """

    def __init__(self, feature_engineering_pipeline: FeatureEngineering,
                 model_training_pipeline: ModelTraining):
        self.feature_engineering_pipeline = feature_engineering_pipeline
        self.model_training_pipeline = model_training_pipeline

    def get_steps(self) -> list:
        return [
            self.feature_engineering,
            self.model_training
        ]

    def feature_engineering(self, *args, **context):
        """
            This method executes feature engineering pipeline with preset parameters.
        :return:
        """
        self.feature_engineering_pipeline.execute()

    def model_training(self, *args, **context):
        """
            This method executes training model pipeline with preset parameters.
        :return:
        """
        self.model_training_pipeline.execute()
