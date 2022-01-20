#!/usr/bin/python3

# rml_transform_dag.py
# Date:  20.01.2022
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com

from datetime import datetime, timedelta

from airflow.decorators import dag, task

from sem_covid import config
from sem_covid.adapters.rml_mapper import RMLMapper
from sem_covid.services.dataset_pipelines.topics_rml_transformation_pipeline import TopicsTransformPipeline
from sem_covid.services.store_registry import store_registry

DEFAULT_DAG_ARGUMENTS = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime.now(),
    "email": ["info@meaningfy.ws"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=3600),
    "schedule_interval": "@once",
    "max_active_runs": 128,
    "concurrency": 128,
    "execution_timeout": timedelta(hours=24),
}

MINIO_RML_BUCKET = 'rdf-transformer'
RML_RULES_FILE_NAME = 'ds_unified_topics.ttl'
RML_SOURCE_FILE_NAME = 'topics_data.json'
RDF_RESULT_FILE_NAME = 'ds_unified_topics_result.ttl'


@dag(default_args=DEFAULT_DAG_ARGUMENTS, tags=['etl'])
def topics_rml_transform_dag():
    rml_mapper = RMLMapper(rml_mapper_url=config.RML_MAPPER_URL)
    rml_transform_pipeline = TopicsTransformPipeline(rml_rules_file_name=RML_RULES_FILE_NAME,
                                                     source_file_name=RML_SOURCE_FILE_NAME,
                                                     rdf_result_file_name=RDF_RESULT_FILE_NAME,
                                                     rml_mapper=rml_mapper,
                                                     object_storage=store_registry.minio_object_store(
                                                         minio_bucket=MINIO_RML_BUCKET),
                                                     triple_storage=store_registry.fuseki_triple_store())

    @task
    def execute(rml_pipeline: TopicsTransformPipeline):
        rml_pipeline.execute()

    execute(rml_transform_pipeline)


etl_dag = topics_rml_transform_dag()
