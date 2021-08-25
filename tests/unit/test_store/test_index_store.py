import pandas as pd

from sem_covid.adapters.es_index_store import ESIndexStore
from tests.fake_storage import FakeIndexStore, FakeEsPandasClient, FakeObjectStore


def test_fake_index_store():
    index_store = FakeIndexStore()
    df = pd.DataFrame([{"col1": "A", "col2": "B"}])
    index_store.put_dataframe(index_name="test", content=df)
    tmp_df = index_store.get_dataframe(index_name="test")
    assert len(tmp_df) == len(df)
    assert "col1" in tmp_df.columns
    assert "col2" in tmp_df.columns
    assert tmp_df["col1"][0] == "A"
    tmp_df = index_store.get_dataframe(index_name="NoIndex")
    assert tmp_df is None


def test_index_store():
    es_store = ESIndexStore(FakeEsPandasClient())
    df = pd.DataFrame([{"A": "B"}])
    assert es_store.index(index_name="no", document_id=0, document_body="nope") == "FakeIndexResult"
    assert es_store.search(index_name="no", query="no_query") == "FakeSearchResult"
    assert es_store.get_document(index_name="no", document_id=0) == "FakeGetResult"
    es_store.put_dataframe(index_name="test_df", content=df)
    result_df = es_store.get_dataframe(index_name="test_df")
    assert type(result_df) == pd.DataFrame
    assert result_df.equals(df)
    es_store.dump(index_name="test_df", file_name="test_file", remote_store=FakeObjectStore())
