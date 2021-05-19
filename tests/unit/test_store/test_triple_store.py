
from tests.unit.test_store.fake_storage import FakeTripleStore


def test_triple_store():
    triple_store = FakeTripleStore()
    tmp_store = triple_store.with_query(sparql_query="Use SPARQL query")
    assert type(tmp_store) == FakeTripleStore
    assert tmp_store == triple_store
    tmp_df = tmp_store.get_dataframe()
    assert "col1" in tmp_df.columns
    assert "col2" in tmp_df.columns
    assert tmp_df["col1"][0] == "A"
