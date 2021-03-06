import hashlib
import json
import logging
from typing import List

import numpy as np
import pandas as pd
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from sem_covid.adapters.abstract_store import SPARQLEndpointABC
from sem_covid.adapters.dag.base_etl_dag_pipeline import BaseMasterPipeline
from sem_covid.services.index_mapping_registry import IndicesMappingRegistry
from sem_covid.services.sc_wrangling.json_transformer import transform_eu_cellar_item
from sem_covid.services.store_registry import StoreRegistryABC

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
    return unified_dataframe


def get_and_transform_documents_from_triple_store(list_of_queries: List[str],
                                                  triple_store_adapter: SPARQLEndpointABC,
                                                  transformation_function=transform_eu_cellar_item,
                                                  ) -> List[pd.DataFrame]:
    """
        This is a helper function that given a list of SPARQL queries,
        1. fetch the result sets,
        2. cast them to dicts and
        3. transform them with JQ based transformation function (item level)
        4. cast the results back into dataframes and return teh results
    """
    list_of_result_data_frames = [triple_store_adapter.with_query(sparql_query=query).get_dataframe() for query in
                                  list_of_queries]

    # The NaN cause strange behaviour in the JQ transformer (3 work days have been lost on writing these 2 lines: RIP)
    # please use teh debugger more often than one every three days
    for df in list_of_result_data_frames:
        df.replace({np.nan: None}, inplace=True)
    list_of_result_sets = [df.to_dict(orient="records") for df in list_of_result_data_frames]
    list_of_transformed_result_sets = [[transformation_function(item_dict) for item_dict in result_set_dict_list] for
                                       result_set_dict_list in list_of_result_sets]
    list_of_transformed_df = [pd.DataFrame.from_records(result_set) for result_set in list_of_transformed_result_sets]

    return list_of_transformed_df


def get_documents_from_triple_store(list_of_queries: List[str],
                                    list_of_query_flags: List[str],
                                    triple_store_adapter: SPARQLEndpointABC,
                                    id_column: str) -> pd.DataFrame:
    """

        Give a list of SPARQL queries, fetch the result set and merge it into a unified result set.
        Each distinct work is also flagged indicating the query used to fetch it. When fetched multiple times,
        a work is simply flagged multiple times.
        When merging the result sets, the unique identifier will be specified in a result-set column.
    """
    list_of_result_df = get_and_transform_documents_from_triple_store(list_of_queries=list_of_queries,
                                                                      triple_store_adapter=triple_store_adapter,
                                                                      transformation_function=transform_eu_cellar_item)

    return unify_dataframes_and_mark_source(list_of_data_frames=list_of_result_df,
                                            list_of_flags=list_of_query_flags,
                                            id_column=id_column)


class CellarDagMaster(BaseMasterPipeline):
    """
        A pipeline for selecting works to be fetched from Cellar
    """

    def __init__(self, list_of_queries: List[str],
                 sparql_endpoint_url: str, minio_bucket_name: str, worker_dag_name: str,
                 store_registry: StoreRegistryABC, index_name: str,
                 index_mappings: dict = IndicesMappingRegistry().CELLAR_INDEX_MAPPING,
                 list_of_query_flags: List[str] = ["core"]):
        self.store_registry = store_registry
        self.list_of_queries = list_of_queries
        self.list_of_query_flags = list_of_query_flags
        self.minio_bucket_name = minio_bucket_name
        self.sparql_endpoint_url = sparql_endpoint_url
        self.worker_dag_name = worker_dag_name
        self.index_name = index_name
        self.index_mappings = index_mappings

    def select_assets(self, *args, **context):
        """
            this function:
                (0) creates the elastic index for the dataset, if it doesn't exist
                (1) queries the triple store with all the queries,
                (2) unifies the result set,
                (3) stores the unified result set and then
                (4) splits the result set into separate documents/fragments and
                (5) stores each fragment for further processing

            The SPARQL query shall return at least the list of work URIs.
        """
        es_adapter = self.store_registry.es_index_store()
        es_adapter.create_index(index_name=self.index_name, index_mappings=self.index_mappings)
        triple_store_adapter = self.store_registry.sparql_endpoint(self.sparql_endpoint_url)

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
            logger.info(f"Bootstrapping Work {row[WORK_ID_COLUMN]} with content {row.to_dict()}")
            filename = DOCUMENTS_PREFIX + hashlib.sha256(row[WORK_ID_COLUMN].encode('utf-8')).hexdigest() + ".json"
            minio.put_object(filename, json.dumps(row.to_dict()))

    def trigger_workers(self, *args, **context):
        minio = self.store_registry.minio_object_store(self.minio_bucket_name)
        documents = minio.list_objects(DOCUMENTS_PREFIX)
        for index, document in enumerate(documents):
            file_content = json.loads(minio.get_object(document.object_name))
            TriggerDagRunOperator(
                task_id='trigger_slave_dag____' + document.object_name.replace("/", "_"),
                trigger_dag_id=self.worker_dag_name,
                conf={WORK_ID_COLUMN: file_content[WORK_ID_COLUMN]}
            ).execute(context)
            logger.info(f"Triggered {index} {document.object_name} DAG run")
