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
from sem_covid.services.store_registry import StoreRegistry

"""
   These constants represent the name of the index in ElasticSearch,
     which consist of the original index name and the label for enriched datasets.
"""
ENRICHED_INDEX_NAME_SUFFIX = '_enriched'
EU_CELLAR_ENRICHED_INDEX_NAME = config.EU_CELLAR_ELASTIC_SEARCH_INDEX_NAME + ENRICHED_INDEX_NAME_SUFFIX
EU_TIMELINE_ENRICHED_INDEX_NAME = config.EU_TIMELINE_ELASTIC_SEARCH_INDEX_NAME + ENRICHED_INDEX_NAME_SUFFIX
IRELAND_TIMELINE_ENRICHED_INDEX_NAME = config.IRELAND_TIMELINE_ELASTIC_SEARCH_INDEX_NAME + ENRICHED_INDEX_NAME_SUFFIX


class Dataset(object):
    """
        Registry of dataset sources
    """
    PWDB = IndexTabularDataSource(config.PWDB_ELASTIC_SEARCH_INDEX_NAME, StoreRegistry.es_index_store())
    EU_CELLAR = IndexTabularDataSource(config.EU_CELLAR_ELASTIC_SEARCH_INDEX_NAME, StoreRegistry.es_index_store())
    EU_ACTION_TIMELINE = IndexTabularDataSource(config.EU_TIMELINE_ELASTIC_SEARCH_INDEX_NAME,
                                                StoreRegistry.es_index_store())
    IRELAND_ACTION_TIMELINE = IndexTabularDataSource(config.IRELAND_TIMELINE_ELASTIC_SEARCH_INDEX_NAME,
                                                     StoreRegistry.es_index_store())
    EU_CELLAR_ENRICHED = IndexTabularDataSource(EU_CELLAR_ENRICHED_INDEX_NAME,
                                                StoreRegistry.es_index_store())
    EU_ACTION_TIMELINE_ENRICHED = IndexTabularDataSource(EU_TIMELINE_ENRICHED_INDEX_NAME,
                                                         StoreRegistry.es_index_store())
    IRELAND_ACTION_TIMELINE_ENRICHED = IndexTabularDataSource(IRELAND_TIMELINE_ENRICHED_INDEX_NAME,
                                                              StoreRegistry.es_index_store())


class LanguageModel(object):
    """
        Registry of language model data sources
    """
    LAW2VEC = BinaryDataSource(config.LAW2VEC_MODEL_PATH,
                               StoreRegistry.minio_object_store(config.LANGUAGE_MODEL_BUCKET_NAME)
                               )

    # TODO : This language model is not available in MinIO, check changes
    """
    To read that:
    You can follow https://radimrehurek.com/gensim/models/word2vec.html on how to use these files and search for similar
     terms. Let me know if you have any difficulties using the model. To download you have to use: SeTA2020
    To load:
    KeyedVectors.load("word2vec.wordvectors", mmap='r') mmap usually works on Linux only.
     Earlier it was export in txt format to be able see and analyse phrases independently.
    """
    JRC2VEC = BinaryDataSource(config.JRC2VEC_MODEL_PATH,
                               StoreRegistry.minio_object_store(config.LANGUAGE_MODEL_BUCKET_NAME)
                               )
