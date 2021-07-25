import json
import pathlib

import pytest
from elasticsearch import Elasticsearch

from sem_covid import config


@pytest.fixture(scope="session")
def scenario_context() -> dict:
    return {
        "test_data_directory": pathlib.Path(__file__).resolve().parents[1] / "test_data/pwdb",
        "index_name": "ds_pwdb"
    }

@pytest.fixture(scope="module")
def elasticsearch_client():
    elasticsearch = Elasticsearch([config.ELASTICSEARCH_PROTOCOL + '://' +
                                   config.ELASTICSEARCH_USERNAME + ':' +
                                   config.ELASTICSEARCH_PASSWORD + '@' +
                                   config.ELASTICSEARCH_HOST_NAME + ':' +
                                   str(config.ELASTICSEARCH_PORT)])

    return elasticsearch
