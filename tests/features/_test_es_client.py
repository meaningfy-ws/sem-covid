def test_elasticsearch_client(elasticsearch_client):
    elasticsearch = elasticsearch_client
    get_data = elasticsearch.get(index='ds_pwdb', id="008674a64c7bb9dd4cfa5ba093bbaede04ad38d302b304fe3f60e75b5a9c7d2d")
    assert get_data
