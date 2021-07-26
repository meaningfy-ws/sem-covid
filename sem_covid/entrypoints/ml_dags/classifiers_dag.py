# -*- coding: utf-8 -*-
# Date    : 19.07.2021 
# Author  : Stratulat Ștefan
# File    : classifiers_dag.py
# Software: PyCharm

import logging

from sem_covid.adapters.dag.dag_factory import DagFactory
from sem_covid.entrypoints import dag_name
from sem_covid.entrypoints.ml_dags.classifiers_pipeline_dag import ClassifiersPipelineDag

import airflow

from sem_covid.services.ml_pipelines.pwdb_classifiers_pipeline import FeatureEngineering, ModelTraining

logger = logging.getLogger(__name__)
logger.debug(f"This line is important for DAG discovery because the *airflow module* "
             f"shall be imported here. Otherwise it does not discover DAGs in this "
             f"module. Airflow version {airflow.__version__}")

MINOR = 1
MAJOR = 2
CATEGORY = "ml"

EXPERIMENT_NAME = "PyCaret_pwdb"
PWDB_FEATURE_STORE_NAME = 'fs_pwdb'

classifier_dag_name = dag_name(category=CATEGORY, name="pwdb_classifiers", version_major=MAJOR,
                               version_minor=MINOR)

classifiers_pipeline_dag = ClassifiersPipelineDag(
    feature_engineering_pipeline=FeatureEngineering(feature_store_name=PWDB_FEATURE_STORE_NAME),
    model_training_pipeline=ModelTraining(feature_store_name=PWDB_FEATURE_STORE_NAME,
                                          experiment_name="PyCaret_pwdb"))

dag = DagFactory(
    dag_pipeline=classifiers_pipeline_dag, dag_name=classifier_dag_name).create_dag(
    schedule_interval="@once",
    max_active_runs=1, concurrency=1)
