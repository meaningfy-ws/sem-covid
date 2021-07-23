# -*- coding: utf-8 -*-
# Date    : 19.07.2021 
# Author  : Stratulat Ștefan
# File    : enrich_dags.py
# Software: PyCharm


from sem_covid import config
from sem_covid.adapters.dag.dag_factory import DagFactory
from sem_covid.entrypoints import dag_name
from sem_covid.entrypoints.ml_dags.enrich_pipeline_dag import EnrichPipelineDag

# TODO: the dependency to PyCaret breaks the zen harmony
# import logging
# import airflow
# logger = logging.getLogger(__name__)
# logger.debug(f"This line is important for DAG discovery because the *airflow module* "
#              f"shall be imported here. Otherwise it does not discover DAGs in this "
#              f"module. Airflow version {airflow.__version__}")

MINOR = 1
MAJOR = 2
CATEGORY = "ml"

# Eu-Cellar enrich DAG

EU_CELLAR_ENRICH_DAG_NAME = dag_name(category=CATEGORY, name="eu_cellar_enrich", version_major=MAJOR,
                                     version_minor=MINOR)

EU_CELLAR_TEXT_COLUMNS = ['title']

enrich_eu_cellar_pipeline = EnrichPipelineDag(textual_columns=EU_CELLAR_TEXT_COLUMNS,
                                              ds_es_index=config.EU_CELLAR_ELASTIC_SEARCH_INDEX_NAME,
                                              features_store_name='fs_eu_cellar'
                                              )

dag_enrich_eu_cellar = DagFactory(
    dag_pipeline=enrich_eu_cellar_pipeline, dag_name=EU_CELLAR_ENRICH_DAG_NAME).create_dag(
    schedule_interval="@once",
    max_active_runs=1, concurrency=1)

# Eu-timeline enrich DAG

EU_TIMELINE_ENRICH_DAG_NAME = dag_name(category=CATEGORY, name="eu_timeline_enrich", version_major=MAJOR,
                                       version_minor=MINOR)

EU_TIMELINE_TEXT_COLUMNS = ['title', 'abstract', 'detail_content']

enrich_eu_timeline_pipeline = EnrichPipelineDag(textual_columns=EU_TIMELINE_TEXT_COLUMNS,
                                                ds_es_index=config.EU_TIMELINE_ELASTIC_SEARCH_INDEX_NAME,
                                                features_store_name='fs_eu_timeline'
                                                )

dag_enrich_eu_timeline = DagFactory(
    dag_pipeline=enrich_eu_timeline_pipeline, dag_name=EU_TIMELINE_ENRICH_DAG_NAME).create_dag(
    schedule_interval="@once",
    max_active_runs=1, concurrency=1)

# Ireland-timeline enrich DAG

IRELAND_TIMELINE_ENRICH_DAG_NAME = dag_name(category=CATEGORY, name="ireland_timeline_enrich", version_major=MAJOR,
                                            version_minor=MINOR)

IRELAND_TIMELINE_TEXT_COLUMNS = ['title', 'content', 'keyword']

enrich_ireland_timeline_pipeline = EnrichPipelineDag(textual_columns=IRELAND_TIMELINE_TEXT_COLUMNS,
                                                     ds_es_index=config.IRELAND_TIMELINE_ELASTIC_SEARCH_INDEX_NAME,
                                                     features_store_name='fs_ireland_timeline'
                                                     )

dag_enrich_ireland_timeline = DagFactory(
    dag_pipeline=enrich_ireland_timeline_pipeline, dag_name=IRELAND_TIMELINE_ENRICH_DAG_NAME).create_dag(
    schedule_interval="@once",
    max_active_runs=1, concurrency=1)
