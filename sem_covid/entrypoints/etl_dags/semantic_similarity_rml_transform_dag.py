#!/usr/bin/python3

# rml_transform_dag.py
# Date:  30.12.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com

from datetime import datetime, timedelta

from airflow.decorators import dag, task

from sem_covid import config
from sem_covid.adapters.rml_mapper import RMLMapper
from sem_covid.services.dataset_pipelines.similarity_matrix_rml_transformation_pipeline import \
    SemanticSimilarityMapRMLTransformPipeline
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

SEMANTIC_SIMILARITY_MINIO_BUCKET = 'semantic-similarity-matrices'
RDF_TRANSFORMER_MINIO_BUCKET = 'rdf-transformer'
SEMANTIC_SIMILARITY_DATAFRAME = 'unified_dataset_similarity_matrix.pkl'
DS_UNIFIED_SEM_SIMILARITY_MATRIX = 'ds_unified_sem_similarity_matrix'
MINIO_RML_RULES_DIR = 'rml_rules'
RML_RULES_FILE_NAME = 'ds_unified_similarity_matrix.ttl'
RDF_RESULT_FILE_NAME = 'ds_unified_similarity_matrix_result.ttl'


@dag(default_args=DEFAULT_DAG_ARGUMENTS, tags=['etl'])
def semantic_similarity_rml_transform_dag():
    rml_mapper = RMLMapper(rml_mapper_url=config.RML_MAPPER_URL)
    rml_transform_pipeline = SemanticSimilarityMapRMLTransformPipeline(rml_rules_file_name=RML_RULES_FILE_NAME,
                                                                       source_file_name=SEMANTIC_SIMILARITY_DATAFRAME,
                                                                       rdf_result_file_name=RDF_RESULT_FILE_NAME,
                                                                       rml_mapper=rml_mapper,
                                                                       object_storage=store_registry.minio_object_store(
                                                                           minio_bucket=RDF_TRANSFORMER_MINIO_BUCKET),
                                                                       feature_storage=store_registry.minio_feature_store(
                                                                           minio_bucket=SEMANTIC_SIMILARITY_MINIO_BUCKET),
                                                                       triple_storage=store_registry.fuseki_triple_store(),
                                                                       use_sample_data=True
                                                                       )
    @task
    def execute(rml_pipeline: SemanticSimilarityMapRMLTransformPipeline):
        rml_pipeline.execute()

    execute(rml_transform_pipeline)


etl_dag = semantic_similarity_rml_transform_dag()

