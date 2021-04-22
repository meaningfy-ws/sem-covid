import os

ES_PROTOCOL = os.environ.get('ES_PROTOCOL', 'http')
ES_HOSTNAME = os.environ.get('ES_HOSTNAME', 'srv.meaningfy.ws')
ES_PORT = os.environ.get('ES_PORT', 9200)
ES_USERNAME = os.environ.get('ES_USERNAME', 'elastic')
ES_PASSWORD = os.environ.get('ES_PASSWORD', 'changeme')
ES_PWDB_INDEX_MAPPING_FILE = os.environ.get('ES_PWDB_INDEX_MAPPING_FILE', './resources/elasticsearch/pwdb_index_mapping.json')
ES_PWDB_INDEX_NAME = os.environ.get('ES_PWDB_INDEX_NAME', 'uat-pwdb-index')
PWDB_ES_TEST_DATA_DIRECTORY = os.environ.get('PWDB_ES_TEST_DATA_DIRECTORY', 'tests/test_data/pwdb')

