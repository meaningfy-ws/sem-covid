import pandas as pd
import requests

from tests.fake_storage import FakeTripleStore

def test_triple_store():
    triple_store = FakeTripleStore()
    datasets  = triple_store.list_datasets()
    assert datasets is not None
    assert len(datasets) == 2
    response = triple_store.create_dataset(dataset_id="Hey")
    assert type(response) ==  requests.Response
    response = triple_store.delete_dataset(dataset_id="Hey")
    assert type(response) == requests.Response
    df = triple_store.sparql_query(dataset_id="hey", query="test query")
    assert type(df) == pd.DataFrame
