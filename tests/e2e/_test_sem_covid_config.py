from sem_covid import config, FlaskConfig


def test_elastic_search_config():
    assert config.ELASTICSEARCH_PORT is not None
    assert config.ELASTICSEARCH_PASSWORD is not None
    assert config.ELASTICSEARCH_PROTOCOL is not None
    assert config.ELASTICSEARCH_USERNAME is not None
    assert config.ELASTICSEARCH_HOST_NAME is not None


def test_eu_cellar_config():
    assert config.EU_CELLAR_JSON is not None
    assert config.EU_CELLAR_SPARQL_URL is not None
    assert config.EU_CELLAR_BUCKET_NAME is not None
    assert config.EU_CELLAR_EXTENDED_JSON is not None
    assert config.EU_CELLAR_ELASTIC_SEARCH_INDEX_NAME is not None


def test_eu_timeline_config():
    assert config.EU_TIMELINE_JSON is not None
    assert config.EU_TIMELINE_BUCKET_NAME is not None
    assert config.EU_TIMELINE_ELASTIC_SEARCH_INDEX_NAME is not None


def test_ireland_timeline_config():
    assert config.IRELAND_TIMELINE_JSON is not None
    assert config.IRELAND_TIMELINE_BUCKET_NAME is not None
    assert config.IRELAND_TIMELINE_ELASTIC_SEARCH_INDEX_NAME is not None


def test_pwdb_config():
    assert config.PWDB_DATASET_URL is not None
    assert config.PWDB_COVID19_BUCKET_NAME is not None
    assert config.PWDB_ELASTIC_SEARCH_INDEX_NAME is not None


def test_minio_config():
    assert config.MINIO_URL is not None
    assert config.MINIO_ACCESS_KEY is not None
    assert config.MINIO_SECRET_KEY is not None


def test_legal_initiatives_config():
    assert config.LEGAL_INITIATIVES_JSON is not None
    assert config.LEGAL_INITIATIVES_BUCKET_NAME is not None
    assert config.LEGAL_INITIATIVES_ELASTIC_SEARCH_INDEX_NAME is not None


def test_treaties_config():
    assert config.TREATIES_JSON is not None
    assert config.TREATIES_SPARQL_URL is not None
    assert config.TREATIES_BUCKET_NAME is not None
    assert config.TREATIES_ELASTIC_SEARCH_INDEX_NAME is not None


def test_vault_config():
    assert config.VAULT_TOKEN is not None
    assert config.VAULT_ADDR is not None


def test_flask_config():
    assert FlaskConfig.FLASK_SECRET_KEY is not None



