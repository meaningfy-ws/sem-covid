import json
from pathlib import Path

import pytest
from elasticsearch import Elasticsearch


@pytest.fixture(scope="session")
def scenario_context():
    from tests.features.config import PWDB_ES_TEST_DATA_DIRECTORY
    from tests.features.config import ES_PWDB_INDEX_NAME
    return {"test_data_directory": PWDB_ES_TEST_DATA_DIRECTORY, "index_name": ES_PWDB_INDEX_NAME}


@pytest.fixture(scope="module")
def elasticsearch_client():
    print("Instantiating ElasticSearch client...")
    from tests.features.config import ES_PROTOCOL
    from tests.features.config import ES_USERNAME
    from tests.features.config import ES_PASSWORD
    from tests.features.config import ES_HOSTNAME
    from tests.features.config import ES_PORT
    elasticsearch = Elasticsearch([ES_PROTOCOL +
                                   '://' +
                                   ES_USERNAME +
                                   ':' +
                                   ES_PASSWORD +
                                   '@' +
                                   ES_HOSTNAME +
                                   ':' +
                                   str(ES_PORT)])
    from tests.features.config import ES_PWDB_INDEX_MAPPING_FILE
    with open(ES_PWDB_INDEX_MAPPING_FILE) as json_file:
        mapping = json.load(json_file)
    from tests.features.config import ES_PWDB_INDEX_NAME
    print("Creating index " + ES_PWDB_INDEX_NAME)
    elasticsearch.indices.create(index=ES_PWDB_INDEX_NAME, body=mapping, ignore=400)

    from tests.features.config import PWDB_ES_TEST_DATA_DIRECTORY
    path_list = Path(PWDB_ES_TEST_DATA_DIRECTORY) / Path('tika')
    count = 0
    for path in path_list.glob('*.*'):
        with open(Path(path)) as json_file:
            payload = json.load(json_file)
        res = elasticsearch.index(index=ES_PWDB_INDEX_NAME, body=payload)
        count += 1
        print(str(count) + " - sent  " + str(path) + " - the result was " + str(res))
    print("Forcing index refresh...")
    elasticsearch.indices.refresh(index=ES_PWDB_INDEX_NAME)
    yield elasticsearch
    print("Deleting index " + ES_PWDB_INDEX_NAME)
    elasticsearch.indices.delete(index=ES_PWDB_INDEX_NAME)
