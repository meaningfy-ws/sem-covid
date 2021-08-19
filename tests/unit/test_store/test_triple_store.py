
from tests.fake_storage import FakeTripleStore


def test_triple_store():
    triple_store = FakeTripleStore()
    tmp_store = triple_store.with_query(sparql_query="Use SPARQL query")
    assert type(tmp_store) == FakeTripleStore
    assert tmp_store == triple_store
    tmp_df = tmp_store.get_dataframe()
    assert "title" in tmp_df.columns
    assert "work" in tmp_df.columns
    assert tmp_df["work"][0] == 'http://publications.europa.eu/resource/cellar/0009c137-0348-11eb-a511-01aa75ed71a1'
