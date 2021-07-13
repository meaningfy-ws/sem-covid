import hashlib
import json
import logging
from typing import List

import pandas as pd
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from sem_covid.adapters.abstract_store import TripleStoreABC
from sem_covid.adapters.dag.dag_pipeline_abc import DagPipeline
from sem_covid.services.sc_wrangling.json_transformer import transform_eu_cellar_item
from sem_covid.services.store_registry import StoreRegistryManagerABC

logger = logging.getLogger(__name__)

CONTENT_PATH_KEY = 'content_path'
CONTENT_KEY = 'content'
FAILURE_KEY = 'failure_reason'
RESOURCE_FILE_PREFIX = 'res/'
TIKA_FILE_PREFIX = 'tika/'
CONTENT_LANGUAGE = "language"
DOCUMENTS_PREFIX = "documents/"
WORK_ID_COLUMN = "work"
DOWNLOAD_TIMEOUT = 30


def unify_dataframes_and_mark_source(list_of_data_frames: List[pd.DataFrame], list_of_flags: List[str],
                                     id_column: str) -> pd.DataFrame:
    """
        Unify a list of dataframes dropping duplicates and adding
        a provenance flag (i.e. in which dataframe the record was present)
    """
    assert len(list_of_data_frames) == len(
        list_of_flags), "The number of dataframes shall be the same as the number of flags"
    unified_dataframe = pd.concat(list_of_data_frames). \
        sort_values(id_column).drop_duplicates(subset=[id_column], keep="first")
    for flag, original_df in zip(list_of_flags, list_of_data_frames):
        unified_dataframe[flag] = unified_dataframe.apply(func=
                                                          lambda row: True if row[id_column] in original_df[
                                                              id_column].values else False, axis=1)
    unified_dataframe.reset_index(drop=True, inplace=True)
    unified_dataframe.fillna("", inplace=True)
    return unified_dataframe


def get_documents_from_triple_store(list_of_queries: List[str],
                                    list_of_query_flags: List[str],
                                    triple_store_adapter: TripleStoreABC,
                                    id_column: str) -> pd.DataFrame:
    """
        Give a list of SPARQL queries, fetch the result set and merge it into a unified result set.
        Each distinct work is also flagged indicating the query used to fetch it. When fetched multiple times,
        a work is simply flagged multiple times.
        When merging the result sets, the unique identifier will be specified in a result-set column.
    """
    list_of_result_data_frames = [triple_store_adapter.with_query(sparql_query=query).get_dataframe() for query in
                                  list_of_queries]
    return unify_dataframes_and_mark_source(list_of_data_frames=list_of_result_data_frames,
                                            list_of_flags=list_of_query_flags,
                                            id_column=id_column)


class CellarDagMaster(DagPipeline):
    """
        A pipeline for selecting works to be fetched from Cellar
    """

    def __init__(self, list_of_queries: List[str],
                 sparql_endpoint_url: str, minio_bucket_name: str, worker_dag_name: str,
                 store_registry: StoreRegistryManagerABC,
                 list_of_query_flags: List[str] = ["core"], ):
        self.store_registry = store_registry
        self.list_of_queries = list_of_queries
        self.list_of_query_flags = list_of_query_flags
        self.minio_bucket_name = minio_bucket_name
        self.sparql_endpoint_url = sparql_endpoint_url
        self.worker_dag_name = worker_dag_name

    def get_steps(self) -> list:
        return [self.download_and_split, self.execute_worker_dags]

    def download_and_split(self, *args, **context):
        """
            this function:
                (1) queries the triple store with all the queries,
                (2) unifies the result set,
                (3) stores the unified result set and then
                (4) splits the result set into separate documents/fragments and
                (5) stores each fragment for further processing

            The SPARQL query shall return at least the list of work URIs.
        """
        triple_store_adapter = self.store_registry.sparql_triple_store(self.sparql_endpoint_url)
        unified_df = get_documents_from_triple_store(
            list_of_queries=self.list_of_queries,
            list_of_query_flags=self.list_of_query_flags,
            triple_store_adapter=triple_store_adapter,
            id_column=WORK_ID_COLUMN)

        minio = self.store_registry.minio_object_store(self.minio_bucket_name)
        minio.empty_bucket(object_name_prefix=None)
        minio.empty_bucket(object_name_prefix=RESOURCE_FILE_PREFIX)
        minio.empty_bucket(object_name_prefix=TIKA_FILE_PREFIX)
        minio.empty_bucket(object_name_prefix=DOCUMENTS_PREFIX)

        for index, row in unified_df.iterrows():
            file_content = transform_eu_cellar_item(dict(row.to_dict()))
            filename = DOCUMENTS_PREFIX + hashlib.sha256(row[WORK_ID_COLUMN].encode('utf-8')).hexdigest() + ".json"
            minio.put_object(filename, json.dumps(file_content))

    def execute_worker_dags(self, *args, **context):
        minio = self.store_registry.minio_object_store(self.minio_bucket_name)
        documents = minio.list_objects(DOCUMENTS_PREFIX)
        for index, document in enumerate(documents):
            file_content = json.loads(minio.get_object(document.object_name))
            TriggerDagRunOperator(
                task_id='trigger_slave_dag____' + document.object_name.replace("/", "_"),
                trigger_dag_id=self.worker_dag_name,
                conf={"work": file_content['work']}
            ).execute(context)
            logger.info(f"Triggered {index} {document.object_name} DAG run")
