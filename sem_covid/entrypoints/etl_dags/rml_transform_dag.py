#!/usr/bin/python3

# rml_transform_dag.py
# Date:  30.12.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com

from datetime import datetime, timedelta

from airflow.decorators import dag, task

from sem_covid import config
from sem_covid.adapters.rml_mapper import RMLMapper
from sem_covid.services.dataset_pipelines.rml_transform_pipeline import RMLTransformPipeline
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
RML_RULES_FILE_NAME = 'ds_unified_dataset.ttl'
RDF_RESULT_FILE_NAME = 'ds_unified_dataset_result.ttl'
RML_MAPPING_SOURCES = ['country.json', 'datasets.json', 'eu_cellar_author_labels.json',
                       'eu_cellar_directory_code_labels.json', 'eu_cellar_resource_type_labels.json',
                       'eu_cellar_subject_matter_labels.json', 'eu_timeline_topic.json', 'ireland_keyword.json',
                       'ireland_page_type.json', 'pwdb_actors.json', 'pwdb_category.json', 'pwdb_funding.json',
                       'pwdb_target_group_l1.json', 'pwdb_target_group_l2.json', 'pwdb_type_of_measure.json']


@dag(default_args=DEFAULT_DAG_ARGUMENTS, tags=['etl'])
def rml_transform_dag():
    rml_mapper = RMLMapper(rml_mapper_url=config.RML_MAPPER_URL)
    rml_transform_pipeline = RMLTransformPipeline(rml_rules_file_name=RML_RULES_FILE_NAME,
                                                  source_file_names=RML_MAPPING_SOURCES,
                                                  rdf_result_file_name=RDF_RESULT_FILE_NAME,
                                                  rml_mapper=rml_mapper,
                                                  object_storage=store_registry.minio_object_store(
                                                      minio_bucket=MINIO_RML_BUCKET),
                                                  index_storage=store_registry.es_index_store(),
                                                  triple_storage=store_registry.fuseki_triple_store()
                                                  )
    @task
    def extract(rml_pipeline: RMLTransformPipeline):
        rml_pipeline.extract()
        return rml_pipeline

    @task
    def transform(rml_pipeline: RMLTransformPipeline):
        rml_pipeline.transform()
        return rml_pipeline
    @task
    def load(rml_pipeline: RMLTransformPipeline):
        rml_pipeline.load()
        return rml_pipeline

    pipeline_state = rml_transform_pipeline
    pipeline_state = extract(pipeline_state)
    pipeline_state = transform(pipeline_state)
    pipeline_state = load(pipeline_state)


etl_dag = rml_transform_dag()

