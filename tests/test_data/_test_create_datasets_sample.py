#!/usr/bin/python3

# _test_create_datasets_sample.py
# Date:  16.08.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com
import math

import pandas as pd
from sem_covid import config
from sem_covid.adapters.abstract_store import IndexStoreABC
from sem_covid.services.store_registry import store_registry

SAMPLE_SIZE = 100


def create_dataset_sample(index_name: str, index_store: IndexStoreABC):
    df = index_store.get_dataframe(index_name=index_name)
    step = math.floor(len(df) / SAMPLE_SIZE)
    sample = pd.DataFrame(df.iloc[:SAMPLE_SIZE * step:step])
    sample.to_json(f'datasets_sample/{index_name}.json')


def test_create_datasets_sample():
    index_names = [config.PWDB_ELASTIC_SEARCH_INDEX_NAME,
                   config.EU_CELLAR_ELASTIC_SEARCH_INDEX_NAME,
                   config.EU_TIMELINE_ELASTIC_SEARCH_INDEX_NAME,
                   config.IRELAND_TIMELINE_ELASTIC_SEARCH_INDEX_NAME
                   ]
    es_store = store_registry.es_index_store()
    for index_name in index_names:
        create_dataset_sample(index_name=index_name, index_store=es_store)
