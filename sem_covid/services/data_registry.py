#!/usr/bin/python3

# data.py
# Date:  19/04/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

"""
    A registry of the frequently used datasets and language models
"""
from sem_covid import config
from sem_covid.adapters.data_source import BinaryDataSource, TabularDatasource


class Dataset(object):
    """
        Registry of dataset sources
    """
    PWDB = TabularDatasource(config.PWDB_ELASTIC_SEARCH_INDEX_NAME)
    EU_CELLAR = TabularDatasource(config.EU_CELLAR_ELASTIC_SEARCH_INDEX_NAME)
    EU_ACTION_TIMELINE = TabularDatasource(config.EU_TIMELINE_ELASTIC_SEARCH_INDEX_NAME)
    IRELAND_ACTION_TIMELINE = TabularDatasource(config.IRELAND_TIMELINE_ELASTIC_SEARCH_INDEX_NAME)


class LanguageModel(object):
    """
        Registry of language model data sources
    """
    LAW2VEC = BinaryDataSource(config.LANGUAGE_MODEL_BUCKET_NAME, config.LAW2VEC_MODEL_PATH)
    JRC2VEC = BinaryDataSource(config.LANGUAGE_MODEL_BUCKET_NAME, config.JRC2VEC_MODEL_PATH)
