import pandas as pd

from tests.unit.test_store.fake_storage import FakeIndexStore


def test_index_store():
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
