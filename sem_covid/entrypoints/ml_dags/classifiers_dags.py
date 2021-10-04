# -*- coding: utf-8 -*-
# Date    : 19.07.2021 
# Author  : Stratulat Ștefan
# File    : classifiers_dags.py
# Software: PyCharm


from sem_covid.adapters.dag.dag_factory import DagFactory
from sem_covid.entrypoints import dag_name
from sem_covid.entrypoints.ml_dags.classifiers_pipeline_dag import ClassifiersPipelineDag

from sem_covid.services.ml_pipelines.pwdb_classifiers_pipeline import (FeatureEngineering, ModelTraining,
                                                                       FeatureEngineeringBERT)
# TODO: the dependency to PyCaret breaks the zen harmony
import airflow
import logging
logger = logging.getLogger(__name__)
logger.debug(f"This line is important for DAG discovery because the *airflow module* "
             f"shall be imported here. Otherwise it does not discover DAGs in this "
             f"module. Airflow version {airflow.__version__}")

MINOR = 1
MAJOR = 3
CATEGORY = "ml"

EXPERIMENT_NAME = "PyCaret_pwdb"
PWDB_FEATURE_STORE_NAME = 'fs_pwdb'

REQUIREMENTS = ['pycaret']

# Word-Embedding-AVG classifiers

classifier_dag_name = dag_name(category=CATEGORY, name="pwdb_classifiers", version_major=MAJOR,
                               version_minor=MINOR)

classifiers_pipeline_dag = ClassifiersPipelineDag(
    feature_engineering_pipeline=FeatureEngineering(feature_store_name=PWDB_FEATURE_STORE_NAME),
    model_training_pipeline=ModelTraining(feature_store_name=PWDB_FEATURE_STORE_NAME,
                                          experiment_name=EXPERIMENT_NAME))

dag = DagFactory(
    dag_pipeline=classifiers_pipeline_dag, dag_name=classifier_dag_name).create_ml_dag(
    requirements=REQUIREMENTS,
    schedule_interval="@once",
    max_active_runs=1, concurrency=1)

# Universal-Sentence-Encoding classifiers

# BERT_EXPERIMENT_NAME = "PyCaret_pwdb_bert"
# PWDB_BERT_FEATURE_STORE_NAME = 'fs_pwdb_bert'
#
# classifier_universal_sentence_encoding_dag_name = dag_name(category=CATEGORY,
#                                                            name="pwdb_classifiers_universal_sentence_encoding",
#                                                            version_major=MAJOR,
#                                                            version_minor=MINOR)
#
# classifiers_universal_sentence_encoding_pipeline_dag = ClassifiersPipelineDag(
#     feature_engineering_pipeline=FeatureEngineeringBERT(feature_store_name=PWDB_BERT_FEATURE_STORE_NAME),
#     model_training_pipeline=ModelTraining(feature_store_name=PWDB_BERT_FEATURE_STORE_NAME,
#                                           experiment_name=BERT_EXPERIMENT_NAME))

# dag_universal_sentence_encoding = DagFactory(
#     dag_pipeline=classifiers_universal_sentence_encoding_pipeline_dag,
#     dag_name=classifier_universal_sentence_encoding_dag_name).create_dag(
#     schedule_interval="@once",
#     max_active_runs=1, concurrency=1)
