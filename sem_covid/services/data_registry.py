#!/usr/bin/python3

# data.py
# Date:  19/04/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

"""
    A registry of the frequently used datasets and language models
"""
from sem_covid import config
from sem_covid.adapters.data_source import BinaryDataSource, IndexTabularDataSource
from sem_covid.services.storage_registry import StorageRegistry


class Dataset(object):
    """
        Registry of dataset sources
    """
    PWDB = IndexTabularDataSource(config.PWDB_ELASTIC_SEARCH_INDEX_NAME,
                                  StorageRegistry.es_index_storage()
                                  )
    EU_CELLAR = IndexTabularDataSource(config.EU_CELLAR_ELASTIC_SEARCH_INDEX_NAME,
                                       StorageRegistry.es_index_storage()
                                       )
    EU_ACTION_TIMELINE = IndexTabularDataSource(config.EU_TIMELINE_ELASTIC_SEARCH_INDEX_NAME,
                                                StorageRegistry.es_index_storage()
                                                )
    IRELAND_ACTION_TIMELINE = IndexTabularDataSource(config.IRELAND_TIMELINE_ELASTIC_SEARCH_INDEX_NAME,
                                                     StorageRegistry.es_index_storage()
                                                     )


class LanguageModel(object):
    """
        Registry of language model data sources
    """
    LAW2VEC = BinaryDataSource(config.LAW2VEC_MODEL_PATH,
                               StorageRegistry.minio_object_storage(config.LANGUAGE_MODEL_BUCKET_NAME)
                               )
    JRC2VEC = BinaryDataSource(config.JRC2VEC_MODEL_PATH,
                               StorageRegistry.minio_object_storage(config.LANGUAGE_MODEL_BUCKET_NAME)
                               )
