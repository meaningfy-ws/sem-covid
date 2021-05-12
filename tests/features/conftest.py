import json
import pathlib
from pathlib import Path

import pytest
from elasticsearch import Elasticsearch

from sem_covid import config
from sem_covid.adapters.es_index_storage import ESIndexStorage


@pytest.fixture(scope="session")
def scenario_context() -> dict:
    return {
        "test_data_directory": pathlib.Path(__file__).resolve().parents[1] / "test_data/pwdb",
        "index_name": "ds_pwdb"
    }


# @pytest.fixture(scope="module")
# def elasticsearch_client():
#     print("Instantiating Elasticsearch client . . . ")
#     elasticsearch = ESIndexStorage(config.ELASTICSEARCH_HOST_NAME, config.ELASTICSEARCH_PORT,
#                               config.ELASTICSEARCH_USERNAME, config.ELASTICSEARCH_PASSWORD)
#
#     return elasticsearch


@pytest.fixture(scope="module")
def elasticsearch_client():
    print("Instantiating ElasticSearch client...")
    elasticsearch = Elasticsearch([config.ELASTICSEARCH_PROTOCOL + '://' +
                                   config.ELASTICSEARCH_USERNAME + ':' +
                                   config.ELASTICSEARCH_PASSWORD + '@' +
                                   config.ELASTICSEARCH_HOST_NAME + ':' +
                                   str(config.ELASTICSEARCH_PORT)])

    return elasticsearch