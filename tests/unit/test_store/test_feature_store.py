import pandas as pd

from sem_covid.adapters.es_feature_store import ESFeatureStore
from sem_covid.adapters.minio_feature_store import MinioFeatureStore
from tests.fake_storage import FakeFeatureStore, FakeIndexStore, FakeObjectStore, FakePickle

def test_fake_feature_store():
    feature_store = FakeFeatureStore()
    feature_df = pd.DataFrame([{"f1": "A", "f2": "B"}])
    feature_store.put_features(features_name="test_feature", content=feature_df)
    tmp_df = feature_store.get_features(features_name="test_feature")
    assert len(tmp_df) == len(feature_df)
    assert "f1" in tmp_df.columns
    assert "f2" in tmp_df.columns
    assert tmp_df["f1"][0] == "A"
    tmp_df = feature_store.get_features(features_name="NoFeature")
    assert tmp_df is None


def test_es_feature_store():
    feature_store = ESFeatureStore(FakeIndexStore())
    feature_df = pd.DataFrame([{"f1": "C", "f2": "B"}])
    feature_store.put_features(features_name="test_feature", content=feature_df)
    tmp_df = feature_store.get_features(features_name="test_feature")
    assert len(tmp_df) == len(feature_df)
    assert "f1" in tmp_df.columns
    assert "f2" in tmp_df.columns
    assert tmp_df["f1"][0] == "C"
    tmp_df = feature_store.get_features(features_name="NoFeature")
    assert tmp_df is None


def test_minio_feature_store():
    feature_store = MinioFeatureStore(FakeObjectStore(),pickle_convertor=FakePickle())
    feature_df = pd.DataFrame([{"f1": "C", "f2": "B"}])
    feature_store.put_features(features_name="test_feature", content=feature_df)
    tmp_df = feature_store.get_features(features_name="test_feature")
    assert len(tmp_df) == len(feature_df)
    assert "f1" in tmp_df.columns
    assert "f2" in tmp_df.columns
    assert tmp_df["f1"][0] == "C"
    tmp_df = feature_store.get_features(features_name="NoFeature")
    assert tmp_df is None
