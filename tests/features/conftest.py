import json
import pathlib
from pathlib import Path

import pytest
from elasticsearch import Elasticsearch

from sem_covid import config
from sem_covid.adapters.es_adapter import ESAdapter


@pytest.fixture(scope="session")
def scenario_context() -> dict:
    return {
        "test_data_directory": pathlib.Path(__file__).resolve().parents[1] / "test_data/pwdb",
        "index_name": "ds_pwdb"
    }


# @pytest.fixture(scope="module")
# def elasticsearch_client():
#     print("Instantiating Elasticsearch client . . . ")
#     elasticsearch = ESAdapter(config.ELASTICSEARCH_HOST_NAME, config.ELASTICSEARCH_PORT,
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

    # with open(config.ES_PWDB_INDEX_MAPPING_FILE) as json_file:
    #     mapping = json.load(json_file)
    # print("Creating index " + config.PWDB_ELASTIC_SEARCH_INDEX_NAME)
    # elasticsearch.indices.create(index=config.PWDB_ELASTIC_SEARCH_INDEX_NAME, body=mapping, ignore=400)
    #
    # path_list = Path(config.PWDB_ES_TEST_DATA_DIRECTORY) / Path('tika')
    # count = 0
    # for path in path_list.glob('*.*'):
    #     with open(Path(path)) as json_file:
    #         payload = json.load(json_file)
    #     res = elasticsearch.index(index=config.PWDB_ELASTIC_SEARCH_INDEX_NAME, body=payload)
    #     count += 1
    #     print(str(count) + " - sent  " + str(path) + " - the result was " + str(res))
    # print("Forcing index refresh...")
    #
    # elasticsearch.indices.refresh(index=config.PWDB_ELASTIC_SEARCH_INDEX_NAME)
    # yield elasticsearch
    #
    # print("Deleting index " + config.PWDB_ELASTIC_SEARCH_INDEX_NAME)
    # elasticsearch.indices.delete(index=config.PWDB_ELASTIC_SEARCH_INDEX_NAME)
    return elasticsearch